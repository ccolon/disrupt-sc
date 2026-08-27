"""Mrio — Multi-Regional Input-Output table as a pandas DataFrame."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Selection:
    """Result of MRIO flow-coverage filtering.

    Encodes which agents (region_sectors, external countries) and which
    bilateral MRIO cells survive the cutoff. Downstream stages (firm
    creation, tech-coef loading, household & country building) read from
    this object instead of separate cutoff params.

    Attributes
    ----------
    flow_coverage : float
        The coverage fraction used to derive this selection.
    region_sectors : list[tuple[str, str]]
        Kept (region, sector) tuples, sorted.
    external_buying_countries : list[str]
        External countries that retain at least one kept buy-side cell
        (i.e. an export column with at least one kept supplier).
    external_selling_countries : list[str]
        External countries that retain at least one kept sell-side cell.
    kept_cells : frozenset[tuple[tuple, tuple]]
        The bilateral cells (row_tuple, col_tuple) kept under the
        per-buyer ∪ per-supplier union rule. Includes intermediate,
        final-demand, export and import cells.
    """
    flow_coverage: float
    region_sectors: tuple = field(default_factory=tuple)
    external_buying_countries: tuple = field(default_factory=tuple)
    external_selling_countries: tuple = field(default_factory=tuple)
    kept_cells: frozenset = field(default_factory=frozenset)

    def has_cell(self, row, col) -> bool:
        return (row, col) in self.kept_cells

    def kept_inputs_of(self, buyer_col) -> list:
        """Return the list of supplier rows kept for *buyer_col*."""
        return [row for (row, col) in self.kept_cells if col == buyer_col]

    def kept_buyers_of(self, supplier_row) -> list:
        """Return the list of buyer cols kept for *supplier_row*."""
        return [col for (row, col) in self.kept_cells if row == supplier_row]


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
        "export_label", "final_demand_label", "capital_label", "government_label",
        "import_label", "value_added_label", "tax_label",
    ]

    def __init__(self, *args, monetary_units: str = "mUSD", **kwargs):
        super().__init__(*args, **kwargs)
        self.export_label = self._detect_label("export", axis=1)
        # 'households' is the post-split HFCE label; 'final_demand' was the pre-split
        # C+G+I bundle. Government and investment (GFCF + inventory change) are now their
        # own final-use columns/agents. Patterns keep back-compat with bundled MRIOs.
        self.final_demand_label = self._detect_label("final.?demand|household", axis=1)
        self.government_label = self._detect_label("government", axis=1)
        self.capital_label = self._detect_label("capital|investment", axis=1)
        self.import_label = self._detect_label("import", axis=0)
        self.value_added_label = self._detect_label("value.?added|va", axis=0)
        self.tax_label = self._detect_label("tax", axis=0)
        self._check_square()
        self.region_sectors = [
            t for t in self.columns
            if t[1] not in (self.final_demand_label, self.export_label, self.capital_label, self.government_label)
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
        filepath = Path(filepath)
        if filepath.suffix == ".parquet":
            table = pd.read_parquet(filepath)
        else:
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
        # The level-0 sentinel for the VA row varies by MRIO source
        # (None, '', 'ALL', NaN). Find the row by level-1 match instead of
        # hard-coding the level-0 value.
        va_rows = [idx for idx in self.index if idx[1] == self.value_added_label]
        if not va_rows:
            logging.warning("No VA row in MRIO, defaulting to 20%")
            return {ind: 0.2 for ind in selected}
        if len(va_rows) > 1:
            logging.warning(
                f"Multiple VA rows in MRIO ({va_rows}); summing across them"
            )
            va = self.loc[va_rows, selected].sum(axis=0)
        else:
            va = self.loc[va_rows[0], selected]
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
        cols = [t for t in self.columns if t[1] not in (self.final_demand_label, self.export_label, self.capital_label, self.government_label)]
        rows = [t for t in self.index if t[1] not in (self.import_label, self.value_added_label, self.tax_label)]
        return self.loc[rows, cols]

    def get_import_rows(self) -> pd.DataFrame:
        cols = [t for t in self.columns if t[1] not in (self.final_demand_label, self.export_label, self.capital_label, self.government_label)]
        rows = [t for t in self.index if t[1] == self.import_label]
        return self.loc[rows, cols]

    def get_tech_coef_dict_for_selection(self, selection: "Selection") -> dict:
        """Tech-coefficient dict restricted to *selection.kept_cells*.

        For each kept (region_sector) buyer column, return
        ``{supplier_key: tech_coef}`` where the supplier set is exactly
        the kept input cells in that column. Coefficients are computed
        as ``intermediate / total_output`` of the buyer (same as the
        legacy `get_tech_coef_dict`). Self-supply (diagonal) is preserved
        when present in kept_cells.

        Returns
        -------
        dict[str, dict[str, float]]
            Keyed by buyer region_sector_name ("REG_SECTOR").
        """
        # Import rows are inputs too: a kept (bloc, imports) x (region, sector)
        # cell must become a tech coefficient, or firms never buy imported
        # intermediates and the firm->country "import" link path in
        # supply_chain never triggers (KI-16).
        intermediate = pd.concat([self.get_intermediary(), self.get_import_rows()])
        output = self.get_total_output()
        kept_rs_set = set(selection.region_sectors)

        # Bucket kept cells by buyer column (only intermediate cells matter
        # for tech coefficients; cells whose buyer column is a final-demand
        # or export column are not tech coefs).
        inputs_per_buyer: dict = {}
        inter_col_set = set(intermediate.columns)
        inter_row_set = set(intermediate.index)
        for (row, col) in selection.kept_cells:
            if col in inter_col_set and row in inter_row_set:
                inputs_per_buyer.setdefault(col, []).append(row)

        result: dict[str, dict[str, float]] = {}
        for buyer, suppliers in inputs_per_buyer.items():
            if buyer not in kept_rs_set:
                continue
            output_val = float(output.loc[buyer])
            if output_val <= 0:
                result["_".join(str(x) for x in buyer)] = {}
                continue
            buyer_key = "_".join(str(x) for x in buyer)
            entry: dict[str, float] = {}
            for sup in suppliers:
                value = float(intermediate.at[sup, buyer])
                if value <= 0:
                    continue
                entry["_".join(str(x) for x in sup)] = value / output_val
            result[buyer_key] = entry
        return result

    def get_tech_coef_dict(self, coverage: float, selected=None) -> dict:
        """Return technical coefficients as nested dict using cumulative coverage.

        For each buyer, inputs are sorted by **absolute MRIO flow** (descending)
        and kept until their cumulative share of the buyer's total intermediate
        input reaches *coverage*.  This preserves large absolute trade flows
        even when the tech-coefficient is small (e.g. small-country oil
        exports to large-economy refiners).

        Parameters
        ----------
        coverage : float in (0, 1]
            Cumulative input-coverage fraction.
        selected : list, optional
            Subset of region-sectors to include as buyers (and as supplier
            candidates, alongside external selling countries).
        """
        output = self.get_total_output()
        intermediate = self.get_intermediary()
        tech = intermediate.div(output, axis="columns")
        return self._tech_coef_by_coverage(tech, intermediate, coverage, selected)

    def _tech_coef_by_coverage(self, tech: pd.DataFrame,
                               intermediate: pd.DataFrame,
                               coverage: float,
                               selected: list | None) -> dict:
        """Keep the largest inputs per buyer until *coverage* fraction is met.

        Inputs are ranked by absolute MRIO flow (not tech-coefficient) so that
        large trade flows between a small supplier and a large buyer are not
        lost.  The returned dict still contains tech-coefficient values
        (fraction of buyer output), only the *selection* uses absolute flows.
        """
        result: dict[str, dict[str, float]] = {}

        selected_set = None
        if selected:
            if isinstance(selected[0], str):
                selected = [tuple(s.split("_", 1)) for s in selected]
            selected_set = set(selected)
        external_set = set(getattr(self, "external_selling_countries", []) or [])

        supplier_tuples = list(intermediate.index)
        supplier_keys = np.array(["_".join(str(x) for x in t) for t in supplier_tuples])
        if selected_set is not None:
            supplier_allowed = np.array([
                (t in selected_set) or (t[0] in external_set) for t in supplier_tuples
            ])
        else:
            supplier_allowed = None

        tech_values = tech.values
        abs_values = intermediate.values
        buyers = list(tech.columns)

        for col_idx, buyer in enumerate(buyers):
            if selected_set is not None and buyer not in selected_set:
                continue
            buyer_key = "_".join(str(x) for x in buyer)

            tech_col = tech_values[:, col_idx]
            abs_col = abs_values[:, col_idx]

            mask = (tech_col > 0) & ~np.isnan(tech_col)
            if supplier_allowed is not None:
                mask = mask & supplier_allowed
            if not mask.any():
                result[buyer_key] = {}
                continue

            abs_m = abs_col[mask]
            tech_m = tech_col[mask]
            keys_m = supplier_keys[mask]

            # Stable sort on negated values = descending with ties in original
            # order, matching Python's list.sort(key=..., reverse=True).
            order = np.argsort(-abs_m, kind="stable")
            abs_sorted = abs_m[order]
            total_abs = abs_sorted.sum()
            if total_abs <= 0:
                result[buyer_key] = {}
                continue

            cumsum = np.cumsum(abs_sorted)
            keep_n = int(np.searchsorted(cumsum, coverage * total_abs, side="left")) + 1
            keep_n = min(keep_n, len(abs_sorted))

            result[buyer_key] = {
                str(keys_m[order[i]]): float(tech_m[order[i]])
                for i in range(keep_n)
            }

        return result

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filter_by_flow_coverage(self, coverage: float) -> Selection:
        """Filter the MRIO by approach-B flow coverage.

        For each buyer column (region_sector, final-demand, or export
        column) keep the largest cells, sorted by absolute MRIO value
        descending, until their cumulative share of the column total
        reaches *coverage*. Repeat symmetrically per supplier row (every
        region_sector row and every import row). Return the **union** of
        the two kept-cell sets — every kept agent thereby retains
        ≥coverage of its in-flows and ≥coverage of its out-flows.

        Meta rows/cols (value-added, tax, capital) are excluded from the
        scan: they aren't bilateral trade flows.

        Parameters
        ----------
        coverage : float in (0, 1]
            Fraction of each row/column total preserved.

        Returns
        -------
        Selection
            Kept region_sectors, external countries, and the cell set.
        """
        if not (0 < coverage <= 1):
            raise ValueError(f"flow_coverage must be in (0, 1] (got {coverage})")

        # Submatrix of all bilateral flows. Drops VA / tax rows and the
        # capital column (none of these are real trade flows to model).
        meta_row_labels = {self.value_added_label, self.tax_label} - {""}
        meta_col_labels = {self.capital_label} - {""}
        flow_rows = [t for t in self.index if t[1] not in meta_row_labels]
        flow_cols = [t for t in self.columns if t[1] not in meta_col_labels]
        flows = self.loc[flow_rows, flow_cols]
        abs_flows = flows.abs().values  # numpy view

        kept_mask = (
            _top_cells_per_axis(abs_flows, coverage, axis=0)  # per column
            | _top_cells_per_axis(abs_flows, coverage, axis=1)  # per row
        )

        # Map back to MRIO tuples
        rows_arr = np.array(flow_rows, dtype=object)
        cols_arr = np.array(flow_cols, dtype=object)
        kept_row_idx, kept_col_idx = np.where(kept_mask)
        kept_cells = frozenset(
            (tuple(rows_arr[i]), tuple(cols_arr[j]))
            for i, j in zip(kept_row_idx, kept_col_idx)
        )

        # Derive kept agents
        rs_set = set(self.region_sectors)
        ext_buy_set = set(self.external_buying_countries)
        ext_sell_set = set(self.external_selling_countries)

        kept_rows_tuples = {tuple(rows_arr[i]) for i in np.unique(kept_row_idx)}
        kept_cols_tuples = {tuple(cols_arr[j]) for j in np.unique(kept_col_idx)}

        kept_region_sectors = sorted(rs_set & (kept_rows_tuples | kept_cols_tuples))

        kept_ext_buying = sorted(
            c for c in ext_buy_set
            if any(col[0] == c and col[1] == self.export_label for col in kept_cols_tuples)
        )
        kept_ext_selling = sorted(
            c for c in ext_sell_set
            if any(row[0] == c and row[1] == self.import_label for row in kept_rows_tuples)
        )

        n_total = abs_flows.size
        n_kept = int(kept_mask.sum())
        total_value = float(abs_flows.sum())
        kept_value = float(abs_flows[kept_mask].sum())
        coverage_actual = (kept_value / total_value) if total_value > 0 else 0.0
        logging.info(
            f"Flow coverage q={coverage}: kept {n_kept:,}/{n_total:,} cells "
            f"({100*n_kept/n_total:.1f}% of cells, {100*coverage_actual:.2f}% of value) "
            f"→ {len(kept_region_sectors)}/{len(self.region_sectors)} region_sectors, "
            f"{len(kept_ext_buying)}/{len(self.external_buying_countries)} buying countries, "
            f"{len(kept_ext_selling)}/{len(self.external_selling_countries)} selling countries"
        )

        return Selection(
            flow_coverage=coverage,
            region_sectors=tuple(kept_region_sectors),
            external_buying_countries=tuple(kept_ext_buying),
            external_selling_countries=tuple(kept_ext_selling),
            kept_cells=kept_cells,
        )

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
            export_cols = pd.MultiIndex.from_product(
                [self.external_buying_countries, [self.export_label]]
            )
            deltas = (inp.loc[unbalanced] - output.loc[unbalanced] + EPSILON) / len(export_cols)
            self.loc[unbalanced, export_cols] = (
                self.loc[unbalanced, export_cols].add(deltas, axis=0)
            )



def _top_cells_per_axis(abs_matrix: np.ndarray, coverage: float, axis: int) -> np.ndarray:
    """Per-column (axis=0) or per-row (axis=1) "top cells until cumulative ≥ coverage" mask.

    For each slice along *axis*, sort cells by absolute value descending,
    accumulate, and keep cells up to and including the first one whose
    cumulative reaches `coverage * total`. A slice with zero total
    contributes no kept cells.

    Returns a boolean mask with the same shape as *abs_matrix*.
    """
    if axis == 1:
        # Transpose, run the column algorithm, transpose back.
        return _top_cells_per_axis(abs_matrix.T, coverage, axis=0).T

    n_rows, n_cols = abs_matrix.shape
    if n_rows == 0 or n_cols == 0:
        return np.zeros_like(abs_matrix, dtype=bool)

    # Sort each column descending. Argsort gives indices in ascending order;
    # negate to invert (stable sort preserves ties in original order).
    order = np.argsort(-abs_matrix, axis=0, kind="stable")  # (n_rows, n_cols)
    sorted_vals = np.take_along_axis(abs_matrix, order, axis=0)
    cumsum = np.cumsum(sorted_vals, axis=0)
    totals = cumsum[-1, :]  # (n_cols,)

    target = coverage * totals  # (n_cols,)
    reached = cumsum >= target[None, :]  # (n_rows, n_cols) bool

    # First-True row index per column. argmax on a bool returns the first
    # True position (or 0 if no True). We later zero out columns whose total
    # is non-positive, so the spurious 0 there is harmless.
    first_true_per_col = reached.argmax(axis=0)  # (n_cols,)

    # In sorted space, keep rows 0..first_true_per_col[col] inclusive.
    row_idx = np.arange(n_rows)[:, None]
    sorted_keep = row_idx <= first_true_per_col[None, :]
    sorted_keep[:, totals <= 0] = False  # nothing to keep when slice is empty

    # Scatter the sorted mask back to original positions.
    kept = np.zeros_like(abs_matrix, dtype=bool)
    np.put_along_axis(kept, order, sorted_keep, axis=0)
    return kept
