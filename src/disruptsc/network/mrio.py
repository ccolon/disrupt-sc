"""Mrio — Multi-Regional Input-Output table as a pandas DataFrame."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


EPSILON = 1e-6

# Unit conversion helpers
_PERIODS = {"day": 365, "week": 52, "month": 12, "year": 1}
_UNITS = {"USD": 1, "kUSD": 1e3, "mUSD": 1e6}


def rescale_monetary_values(values, input_units="USD", input_time_resolution="year",
                            target_units="USD", target_time_resolution="year"):
    values = values * _PERIODS[input_time_resolution] / _PERIODS[target_time_resolution]
    values = values * _UNITS[input_units] / _UNITS[target_units]
    return values


class Mrio(pd.DataFrame):
    _metadata = [
        "region_sectors", "region_sector_names", "regions", "sectors",
        "external_buying_countries", "external_selling_countries",
        "region_households", "monetary_units",
        "export_label", "final_demand_label", "capital_label",
        "import_label", "value_added_label", "tax_label",
    ]

    def __init__(self, *args, monetary_units: str = "mUSD", **kwargs):
        super().__init__(*args, **kwargs)
        self.export_label = self._detect_label("export", axis=1)
        self.final_demand_label = self._detect_label("final.?demand", axis=1)
        self.capital_label = self._detect_label("capital", axis=1)
        self.import_label = self._detect_label("import", axis=0)
        self.value_added_label = self._detect_label("value.?added|va", axis=0)
        self.tax_label = self._detect_label("tax", axis=0)
        self._check_square()
        self.region_sectors = [
            t for t in self.columns
            if t[1] not in (self.final_demand_label, self.export_label, self.capital_label)
        ]
        self.region_sector_names = ["_".join(t) for t in self.region_sectors]
        self.regions = list({t[0] for t in self.region_sectors})
        self.sectors = list({t[1] for t in self.region_sectors})
        self.external_buying_countries = [t[0] for t in self.columns if t[1] == self.export_label]
        self.external_selling_countries = [t[0] for t in self.index if t[1] == self.import_label]
        self.region_households = [t for t in self.columns if t[1] == self.final_demand_label]
        self.monetary_units = monetary_units
        self._adjust_output()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @classmethod
    def load(cls, filepath: Path, monetary_units: str = "mUSD") -> Mrio:
        table = pd.read_csv(filepath, header=[0, 1], index_col=[0, 1])
        zero_output = table.index[table.sum(axis=1) == 0].tolist()
        zero_input = table.columns[table.sum(axis=0) == 0].tolist()
        no_flow = list(set(zero_output) & set(zero_input))
        table.drop(index=no_flow, inplace=True)
        table.drop(columns=no_flow, inplace=True)
        return cls(table, monetary_units=monetary_units)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_total_output(self, selected=None) -> pd.Series:
        selected = selected or self.region_sectors
        return self.loc[selected].sum(axis=1)

    def get_total_input(self, selected=None) -> pd.Series:
        selected = selected or self.region_sectors
        parts = pd.concat([self.get_intermediary(), self.get_import_rows()])
        return parts[selected].sum()

    def get_margin_per_industry(self, selected=None) -> dict:
        selected = selected or self.region_sectors
        if not self.value_added_label:
            logging.warning("No VA in MRIO, defaulting to 20%")
            return {ind: 0.2 for ind in selected}
        va = self.loc[(None, self.value_added_label), selected]
        output = self.loc[selected].sum(axis=1)
        ratios = va / output
        logging.info(f"Average VA/output ratio: {ratios.mean():.2%}")
        return ratios.to_dict()

    def get_transport_input_share(self, sector_types, selected=None) -> dict:
        if isinstance(sector_types, pd.Series):
            sector_types = sector_types.to_dict()
        transport_industries = [
            rs for rs in self.region_sectors
            if sector_types.get(rs[1], "").casefold() == "transport"
        ]
        selected = selected or self.region_sectors
        if not transport_industries:
            logging.warning("No transport industry in MRIO, defaulting to 0.2")
            return {ind: 0.2 for ind in selected}
        transport_input = self.loc[transport_industries, selected].sum(axis=0)
        total_input = self.get_total_input(selected)
        ratios = (transport_input / total_input).fillna(0.2)
        logging.info(f"Average transport share: {ratios.mean():.2%}")
        return ratios.to_dict()

    def get_final_demand(self, selected=None) -> pd.DataFrame:
        fd_cols = self.columns.get_level_values(1) == self.final_demand_label
        if selected:
            if isinstance(selected[0], str):
                selected = [tuple(s.split("_", 1)) for s in selected]
            return self.loc[selected, fd_cols]
        return self.loc[:, fd_cols]

    def get_intermediary(self) -> pd.DataFrame:
        cols = [t for t in self.columns if t[1] not in (self.final_demand_label, self.export_label, self.capital_label)]
        rows = [t for t in self.index if t[1] not in (self.import_label, self.value_added_label, self.tax_label)]
        return self.loc[rows, cols]

    def get_import_rows(self) -> pd.DataFrame:
        cols = [t for t in self.columns if t[1] not in (self.final_demand_label, self.export_label, self.capital_label)]
        rows = [t for t in self.index if t[1] == self.import_label]
        return self.loc[rows, cols]

    def get_region_sectors_with_internal_flows(self, threshold: float = 0) -> list:
        """Return region-sectors whose diagonal technical coefficient exceeds *threshold*.

        These are region-sectors that consume a significant share of their own
        output (e.g. oil fields using oil as fuel).  When a region-sector has
        only one firm, the supply-chain builder cannot create a self-loop, so
        the firm must be duplicated so one copy can supply the other.

        Returns a list of tuples, e.g. [('SAU', 'Oil'), ('QAT', 'Oil'), ...].
        """
        inter = self.get_intermediary()
        output = self.get_total_output()
        result = []
        for rs in self.region_sectors:
            try:
                total = float(output.loc[rs])
            except (KeyError, TypeError):
                continue
            if total <= 0:
                continue
            try:
                diag = float(inter.loc[rs, rs])
            except (KeyError, TypeError):
                continue
            coef = diag / total
            if coef > threshold:
                result.append(rs)
        if result:
            logging.info(
                f"Found {len(result)} region-sectors with internal flows "
                f"(diagonal coef > {threshold}): "
                + ", ".join("_".join(str(x) for x in rs) for rs in result[:10])
                + ("..." if len(result) > 10 else "")
            )
        else:
            logging.warning(
                f"No region-sectors with internal flows above threshold={threshold} "
                f"(checked {len(self.region_sectors)} region-sectors)"
            )
        return result

    def get_tech_coef_dict(self, threshold=0, selected=None) -> dict:
        output = self.get_total_output()
        intermediate = self.get_intermediary()
        mat = pd.concat([output] * len(intermediate.index), axis=1).T
        mat.index = intermediate.index
        tech = intermediate / mat

        if selected:
            if isinstance(selected[0], str):
                selected = [tuple(s.split("_", 1)) for s in selected]
            return {
                "_".join(str(x) for x in buyer): {
                    "_".join(str(x) for x in supplier): val
                    for supplier, val in col.items()
                    if val > threshold and (supplier in selected or supplier[0] in self.external_selling_countries)
                }
                for buyer, col in tech.to_dict().items()
                if buyer in selected
            }
        return {
            "_".join(str(x) for x in rs): {
                "_".join(str(x) for x in k): v for k, v in col.items() if v > threshold
            }
            for rs, col in tech.to_dict().items()
        }

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_output(self, cutoff_value, cutoff_type, cutoff_units, data_units) -> list:
        output = self.get_total_output().loc[self.region_sectors]
        return self._filter(output, cutoff_value, cutoff_type, cutoff_units, data_units)

    def filter_by_final_demand(self, cutoff_value, cutoff_type, cutoff_units, data_units) -> list:
        fd = self.get_final_demand().sum(axis=1).loc[self.region_sectors]
        return self._filter(fd, cutoff_value, cutoff_type, cutoff_units, data_units)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _detect_label(self, pattern: str, axis: int) -> str:
        levels = self.index.get_level_values(1) if axis == 0 else self.columns.get_level_values(1)
        matches = levels[levels.str.contains(pattern, case=False)]
        if len(matches) == 0:
            logging.warning(f"No label matching '{pattern}' in MRIO")
            return ""
        return matches[0]

    def _check_square(self):
        inter = self.get_intermediary()
        if inter.shape[0] != inter.shape[1]:
            raise ValueError(f"Intermediary matrix not square: {inter.shape}")

    def _adjust_output(self):
        output = self.get_total_output()
        inp = self.get_total_input()
        unbalanced = inp[inp > output].index.tolist()
        if unbalanced:
            logging.warning(f"{len(unbalanced)} region_sectors with input > output, adjusting export")
            for rs in unbalanced:
                export_cols = pd.MultiIndex.from_product(
                    [self.external_buying_countries, [self.export_label]]
                )
                delta = (inp[rs] - output[rs] + EPSILON) / len(export_cols)
                self.loc[rs, export_cols] += delta

    @staticmethod
    def _filter(series, cutoff_value, cutoff_type, cutoff_units, data_units) -> list:
        if cutoff_type == "percentage":
            rel = series / series.sum()
            return rel.index[rel > cutoff_value].tolist()
        elif cutoff_type == "absolute":
            adjusted = rescale_monetary_values(
                cutoff_value, input_units=cutoff_units, target_units=data_units,
                input_time_resolution="year", target_time_resolution="year",
            )
            return series.index[series > adjusted].tolist()
        elif cutoff_type == "relative_to_average":
            cutoff = cutoff_value * series.sum() / series.shape[0]
            return series.index[series > cutoff].tolist()
        raise ValueError(f"Unknown cutoff type: {cutoff_type}")
