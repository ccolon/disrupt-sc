"""Export simulation results: incremental CSV writer + summary exports."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import pandas as pd
import geopandas as gpd


def _ensure_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Ensure GeoDataFrame has CRS set to EPSG:4326."""
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    return gdf


# ------------------------------------------------------------------
# Incremental CSV writer
# ------------------------------------------------------------------

class CsvWriter:
    """Append rows to a CSV file incrementally (no in-memory accumulation)."""

    def __init__(self, path: Path, columns: list[str]):
        self.path = path
        self.columns = columns
        self._fp = open(path, "w", newline="")
        self._writer = csv.DictWriter(self._fp, fieldnames=columns, extrasaction="ignore")
        self._writer.writeheader()

    def write_row(self, row: dict):
        self._writer.writerow(row)

    def write_rows(self, rows: list[dict]):
        self._writer.writerows(rows)

    def close(self):
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ------------------------------------------------------------------
# Agent CSV writers (opened once, written to each time step)
# ------------------------------------------------------------------

FIRM_COLUMNS = [
    "time_step", "firm", "region", "sector",
    "production", "production_target", "production_capacity",
    "product_stock", "total_order", "total_input", "rationing",
    "profit", "price", "delta_price_input",
]

HOUSEHOLD_COLUMNS = [
    "time_step", "household", "region",
    "consumption_loss", "extra_spending",
]

HOUSEHOLD_BY_SECTOR_COLUMNS = [
    "time_step", "household", "sector",
    "consumption_loss", "extra_spending",
]

COUNTRY_COLUMNS = [
    "time_step", "country",
    "extra_spending", "consumption_loss",
    "generalized_transport_cost",
    "usd_transported", "tons_transported", "tonkm_transported",
]

INVENTORY_COLUMNS = [
    "time_step", "firm", "input_sector",
    "eq_need", "inventory_qty", "inventory_days",
]


class AgentWriters:
    """Manage the set of CSV writers for agent time-series data."""

    def __init__(self, export_folder: Path, days_per_timestep: float = 7.0):
        self.firm = CsvWriter(export_folder / "firm_data.csv", FIRM_COLUMNS)
        self.household = CsvWriter(export_folder / "household_data.csv", HOUSEHOLD_COLUMNS)
        self.household_by_sector = CsvWriter(
            export_folder / "household_data_by_sector.csv", HOUSEHOLD_BY_SECTOR_COLUMNS,
        )
        self.country = CsvWriter(export_folder / "country_data.csv", COUNTRY_COLUMNS)
        self.inventory = CsvWriter(export_folder / "inventory_data.csv", INVENTORY_COLUMNS)
        self._days_per_timestep = days_per_timestep

    def write_step(self, firms: dict, households: dict, countries: dict, time_step: int):
        """Collect and write one time step of agent data."""
        # Firms — flat rows
        for firm in firms.values():
            self.firm.write_row(firm.collect_data(time_step))

        # Households — scalar row + per-sector rows
        for hh in households.values():
            data = hh.collect_data(time_step)
            self.household.write_row(data)

            cl_per_sector = data.get("consumption_loss_per_sector", {})
            es_per_sector = data.get("extra_spending_per_sector", {})
            sectors = set(list(cl_per_sector.keys()) + list(es_per_sector.keys()))
            for sector in sectors:
                self.household_by_sector.write_row({
                    "time_step": time_step,
                    "household": data["household"],
                    "sector": sector,
                    "consumption_loss": cl_per_sector.get(sector, 0),
                    "extra_spending": es_per_sector.get(sector, 0),
                })

        # Countries — flat rows
        for c in countries.values():
            self.country.write_row(c.collect_data(time_step))

        # Firm inventories — one row per (firm, input_sector)
        for firm in firms.values():
            for input_sector, inv_qty in firm.inventory.items():
                eq_need = firm.eq_needs.get(input_sector, 0.0)
                inv_days = (inv_qty / eq_need * self._days_per_timestep) if eq_need > 0 else 0.0
                self.inventory.write_row({
                    "time_step": time_step,
                    "firm": firm.pid,
                    "input_sector": input_sector,
                    "eq_need": eq_need,
                    "inventory_qty": inv_qty,
                    "inventory_days": inv_days,
                })

    def close(self):
        self.firm.close()
        self.household.close()
        self.household_by_sector.close()
        self.country.close()
        self.inventory.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ------------------------------------------------------------------
# Data collection helpers (for in-memory accumulation path)
# ------------------------------------------------------------------

def collect_firm_data(firms: dict, time_step: int) -> list[dict]:
    return [firm.collect_data(time_step) for firm in firms.values()]


def collect_household_data(households: dict, time_step: int) -> list[dict]:
    return [hh.collect_data(time_step) for hh in households.values()]


def collect_country_data(countries: dict, time_step: int) -> list[dict]:
    return [c.collect_data(time_step) for c in countries.values()]


# ------------------------------------------------------------------
# Logistics report
# ------------------------------------------------------------------

def export_logistics_report(reports: list[dict], export_folder: Path,
                            monetary_units: str = "mUSD"):
    """Write logistics_report.csv from one or more timestep reports.

    Each *report* is the dict returned by
    ``TransportNetwork.compute_logistics_report()``.

    Outputs:
      - logistics_report.csv        — monitored edges (capacity overrides)
      - logistics_summary.csv       — network-level + modal-split summary
      - logistics_top_utilized.csv  — top 10 most utilized edges per timestep
    """
    # --- Monitored edges ---
    monitored_rows = []
    for r in reports:
        monitored_rows.extend(r["monitored"])
    if monitored_rows:
        df = pd.DataFrame(monitored_rows)
        df.to_csv(export_folder / "logistics_report.csv", index=False)
        logging.info(f"Logistics report: {len(monitored_rows)} monitored-edge rows "
                     f"→ logistics_report.csv")

        # Log a concise summary to console
        logging.debug(f"Monitored edges detail in logistics_report.csv")
    else:
        logging.info("Logistics report: no monitored edges found")

    # --- Network summary + modal split ---
    summary_rows = []
    for r in reports:
        net = r["network"]
        summary_rows.append(net)
        for mode, agg in r["by_mode"].items():
            summary_rows.append({
                "time_step": net["time_step"],
                "metric": f"mode_{mode}",
                "tons": round(agg["tons"], 1),
                "usd": round(agg["usd"], 1),
            })
    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(
            export_folder / "logistics_summary.csv", index=False)

    # --- Top utilized ---
    top_rows = []
    for r in reports:
        top_rows.extend(r["top_utilized"])
    if top_rows:
        pd.DataFrame(top_rows).to_csv(
            export_folder / "logistics_top_utilized.csv", index=False)


# ------------------------------------------------------------------
# Transport flow export (per-timestep GeoJSON — unchanged)
# ------------------------------------------------------------------

def export_transport_flows(transport_flow_data: list,
                           transport_edges: gpd.GeoDataFrame,
                           export_folder: Path):
    """Write per-timestep GeoJSON of edge flows."""
    if not transport_flow_data:
        return
    flow_df = pd.DataFrame(transport_flow_data)
    flow_df = flow_df[flow_df["flow_total"] > 0]
    for ts in flow_df["time_step"].unique():
        subset = flow_df[flow_df["time_step"] == ts]
        cols_to_drop = [c for c in ["node_tuple"] if c in transport_edges.columns]
        merged = pd.merge(
            transport_edges.drop(columns=cols_to_drop), subset,
            how="left", on="id",
        )
        _ensure_crs(merged).to_file(
            export_folder / f"transport_edges_with_flows_{ts}.geojson",
            driver="GeoJSON", index=False,
        )


# ------------------------------------------------------------------
# Summary exports
# ------------------------------------------------------------------

def export_summary(household_data: list, country_data: list,
                   household_table: pd.DataFrame | None = None,
                   monetary_units: str = "mUSD", export_folder: Path | None = None):
    """Compute and export loss summary CSVs."""
    hh_df = pd.DataFrame(household_data)
    if hh_df.empty:
        return {"household_loss": 0.0, "country_loss": 0.0}

    loss_rows = []
    for _, grp in hh_df.groupby("household"):
        for _, row in grp.iterrows():
            es = row.get("extra_spending_per_sector", {})
            cl = row.get("consumption_loss_per_sector", {})
            for sector in set(list(es.keys()) + list(cl.keys())):
                loss_rows.append({
                    "household": row["household"],
                    "time_step": row["time_step"],
                    "sector": sector,
                    "loss": es.get(sector, 0) + cl.get(sector, 0),
                })

    loss_df = pd.DataFrame(loss_rows)
    if household_table is not None and "id" in household_table.columns:
        ht = household_table.copy()
        ht["id"] = "hh_" + ht["id"].astype(str)
        loss_df["region"] = loss_df["household"].map(ht.set_index("id")["region"])
    groupby_cols = [c for c in ["region", "sector", "time_step"] if c in loss_df.columns]
    if groupby_cols:
        loss_df = loss_df.groupby(groupby_cols, as_index=False)["loss"].sum()

    household_loss = loss_df["loss"].sum()

    # Country losses
    c_df = pd.DataFrame(country_data)
    c_df["loss"] = c_df["extra_spending"] + c_df["consumption_loss"]
    country_loss = c_df["loss"].sum()

    logging.info(f"Cumulated household loss: {household_loss:,.2f} {monetary_units}")
    logging.info(f"Cumulated country loss: {country_loss:,.2f} {monetary_units}")

    if export_folder:
        loss_df.to_csv(export_folder / "loss_per_region_sector_time.csv", index=False)
        c_df[["time_step", "country", "loss"]].to_csv(
            export_folder / "loss_per_country.csv", index=False,
        )
        pd.DataFrame({"households": [household_loss], "countries": [country_loss]}).to_csv(
            export_folder / "loss_summary.csv", index=False,
        )

    return {"household_loss": household_loss, "country_loss": country_loss}


def export_initial_state(sc_network, export_folder: Path):
    """Export IO matrix and edge list for equilibrium runs."""
    sc_network.calculate_io_matrix().to_csv(export_folder / "io_table.csv")
    sc_network.generate_edge_list().to_csv(export_folder / "sc_network_edgelist.csv")
    logging.info(f"Exported IO table and edge list to {export_folder}")


def export_mrio_summary(mrio, selected, export_folder: Path):
    """Export MRIO reference summaries for reporting comparison.

    Writes two CSVs:
      - mrio_by_sector.csv   — output, input, VA, final_demand, export per sector
      - mrio_by_region.csv   — output, input, VA per region

    Values are in MRIO's native monetary units (annual).  The report
    applies time-resolution scaling when comparing to model values.
    """
    selected = selected or mrio.region_sectors

    total_output = mrio.get_total_output(selected)
    total_input = mrio.get_total_input(selected)

    # Final demand per region_sector
    fd = mrio.get_final_demand(selected).sum(axis=1)

    # Export per region_sector
    export_cols = [t for t in mrio.columns if t[1] == mrio.export_label]
    exports = mrio.loc[selected, export_cols].sum(axis=1) if export_cols else pd.Series(0, index=total_output.index)

    # Value added (if available in MRIO)
    va_label = mrio.value_added_label
    if va_label:
        va_rows = [t for t in mrio.index if t[1] == va_label]
        va = mrio.loc[va_rows, selected].sum(axis=0) if va_rows else total_output - total_input
    else:
        va = total_output - total_input

    # Build per-region_sector DataFrame
    rs_df = pd.DataFrame({
        "region": [rs[0] for rs in selected],
        "sector": [rs[1] for rs in selected],
        "mrio_output": total_output.values,
        "mrio_input": total_input.values,
        "mrio_va": va.values,
        "mrio_final_demand": fd.reindex(selected, fill_value=0).values,
        "mrio_export": exports.reindex(selected, fill_value=0).values,
    })

    # --- By sector ---
    by_sector = rs_df.groupby("sector")[
        ["mrio_output", "mrio_input", "mrio_va", "mrio_final_demand", "mrio_export"]
    ].sum().reset_index()
    by_sector.to_csv(export_folder / "mrio_by_sector.csv", index=False)

    # --- By region ---
    by_region = rs_df.groupby("region")[
        ["mrio_output", "mrio_input", "mrio_va"]
    ].sum().reset_index()
    by_region.to_csv(export_folder / "mrio_by_region.csv", index=False)

    logging.info(f"Exported MRIO summaries ({len(by_sector)} sectors, "
                 f"{len(by_region)} regions) to {export_folder}")


def export_static_tables(firm_table, household_table, transport_edges,
                         transport_nodes, export_folder: Path):
    """Export GeoJSON tables for visualization."""
    if firm_table is not None and hasattr(firm_table, "to_file"):
        _ensure_crs(firm_table).to_file(export_folder / "firm_table.geojson", driver="GeoJSON")
    if household_table is not None and hasattr(household_table, "to_file"):
        _ensure_crs(household_table).to_file(export_folder / "household_table.geojson", driver="GeoJSON")
    if transport_edges is not None:
        cols = [c for c in transport_edges.columns if c != "node_tuple"]
        _ensure_crs(transport_edges[cols]).to_file(
            export_folder / "transport_edges.geojson", driver="GeoJSON",
        )
    if transport_nodes is not None:
        _ensure_crs(transport_nodes).to_file(
            export_folder / "transport_nodes.geojson", driver="GeoJSON",
        )


# ------------------------------------------------------------------
# Monte Carlo CSV writer
# ------------------------------------------------------------------

class MCWriter:
    """Write one row per MC iteration with household + country loss."""

    def __init__(self, path: Path):
        self.path = path
        self._rows = []

    def add_iteration(self, iteration: int, household_loss: float,
                      country_loss: float, extra: dict | None = None):
        row = {"mc_repetition": iteration,
               "household_loss": household_loss,
               "country_loss": country_loss}
        if extra:
            row.update(extra)
        self._rows.append(row)

    def save(self):
        df = pd.DataFrame(self._rows)
        df.to_csv(self.path, index=False)
        logging.info(f"MC results saved to {self.path}")
