"""Export simulation results: incremental CSV writer + summary exports."""

from __future__ import annotations

import csv
import json
import logging
import os
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
    """Append rows to a CSV file incrementally (no in-memory accumulation).

    With ``append=True`` the file is opened in append mode and the header
    is only written if the file is empty or doesn't exist yet — letting
    callers resume partial output safely.
    """

    def __init__(self, path: Path, columns: list[str], flush_each_write: bool = False,
                 append: bool = False):
        self.path = path
        self.columns = columns
        self.flush_each_write = flush_each_write
        mode = "a" if append else "w"
        write_header = not append or not (Path(path).exists() and Path(path).stat().st_size > 0)
        self._fp = open(path, mode, newline="")
        self._writer = csv.DictWriter(self._fp, fieldnames=columns, extrasaction="ignore")
        if write_header:
            self._writer.writeheader()
        if self.flush_each_write:
            self._fp.flush()
            os.fsync(self._fp.fileno())

    def write_row(self, row: dict):
        self._writer.writerow(row)
        if self.flush_each_write:
            self._fp.flush()
            os.fsync(self._fp.fileno())

    def write_rows(self, rows: list[dict]):
        self._writer.writerows(rows)
        if self.flush_each_write:
            self._fp.flush()
            os.fsync(self._fp.fileno())

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
    "active_capital", "idle_capital",
    "product_stock", "total_order", "total_input", "rationing",
    "profit", "price", "delta_price_input",
    "reconstruction_sales", "imports", "input_consumed", "input_stock",
]

HOUSEHOLD_COLUMNS = [
    "time_step", "household", "region",
    "tot_consumption", "tot_spending",
    "consumption_loss", "extra_spending",
    "imports", "inventory_total",
]

HOUSEHOLD_BY_SECTOR_COLUMNS = [
    "time_step", "household", "sector",
    "consumption", "spending",
    "consumption_loss", "extra_spending",
]

COUNTRY_COLUMNS = [
    "time_step", "country",
    "extra_spending", "consumption_loss",
    "qty_sold", "qty_received",
    "generalized_transport_cost",
    "usd_transported", "tons_transported", "tonkm_transported",
]

INVENTORY_COLUMNS = [
    "time_step", "firm", "input_sector",
    "eq_need", "inventory_qty", "inventory_days",
]

LINK_COLUMNS = [
    "time_step", "seller_id", "seller_region", "seller_sector",
    "buyer_id", "buyer_type", "buyer_region", "buyer_sector",
    "order", "delivery", "realized_delivery", "delivery_in_tons",
    "product_type", "cargo_type",
    "eq_price", "price",
]

# Per-country cross-border trade, aggregated from commercial links each step.
# A compact alternative to parsing the full per-link link_data when only
# country-level imports/exports are needed (e.g. the macroMIP adapter).
TRADE_COLUMNS = [
    "time_step", "country",
    "exports", "exports_value", "imports", "imports_value",
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
        self.link = CsvWriter(export_folder / "link_data.csv", LINK_COLUMNS)
        self.trade = CsvWriter(export_folder / "trade_data.csv", TRADE_COLUMNS)
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

            c_per_sector = data.get("consumption_per_sector", {})
            s_per_sector = data.get("spending_per_sector", {})
            cl_per_sector = data.get("consumption_loss_per_sector", {})
            es_per_sector = data.get("extra_spending_per_sector", {})
            sectors = set(c_per_sector) | set(s_per_sector) | set(cl_per_sector) | set(es_per_sector)
            for sector in sectors:
                self.household_by_sector.write_row({
                    "time_step": time_step,
                    "household": data["household"],
                    "sector": sector,
                    "consumption": c_per_sector.get(sector, 0),
                    "spending": s_per_sector.get(sector, 0),
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

    def write_links(self, sc_network, time_step: int):
        """Write one row per commercial link for this time step."""
        for u, v, data in sc_network.edges(data=True):
            link = data["object"]
            seller_type = type(u).__name__
            buyer_type = type(v).__name__

            seller_sector = "imports" if seller_type == "Country" else getattr(u, "sector", "")
            buyer_sector = "" if buyer_type in ("Country", "Household") else getattr(v, "sector", "")
            cargo = link.cargo_type if link.use_transport_network else ""

            self.link.write_row({
                "time_step": time_step,
                "seller_id": u.pid,
                "seller_region": getattr(u, "region", ""),
                "seller_sector": seller_sector,
                "buyer_id": v.pid,
                "buyer_type": buyer_type,
                "buyer_region": getattr(v, "region", ""),
                "buyer_sector": buyer_sector,
                "order": link.order,
                "delivery": link.delivery,
                "realized_delivery": link.realized_delivery,
                "delivery_in_tons": link.delivery_in_tons,
                "product_type": link.product_type,
                "cargo_type": cargo,
                "eq_price": link.eq_price,
                "price": link.price,
            })

    def write_trade(self, sc_network, time_step: int):
        """Aggregate per-country cross-border trade for this time step.

        A commercial link is international when its seller and buyer sit in
        different regions/countries (firm/household ``region`` is the country
        code; the virtual ROW country's region is ``ROW``). The seller's
        country books an export, the buyer's an import. Quantity is realized
        delivery; value uses the current link price.
        """
        from collections import defaultdict
        exp_q = defaultdict(float); exp_v = defaultdict(float)
        imp_q = defaultdict(float); imp_v = defaultdict(float)
        for u, v, data in sc_network.edges(data=True):
            sr = getattr(u, "region", None)
            br = getattr(v, "region", None)
            if sr is None or br is None or sr == br:
                continue
            link = data["object"]
            qty = link.realized_delivery
            if qty <= 0:
                continue
            val = qty * link.price
            exp_q[sr] += qty; exp_v[sr] += val
            imp_q[br] += qty; imp_v[br] += val
        for country in sorted(set(exp_q) | set(imp_q)):
            self.trade.write_row({
                "time_step": time_step,
                "country": country,
                "exports": exp_q.get(country, 0.0),
                "exports_value": exp_v.get(country, 0.0),
                "imports": imp_q.get(country, 0.0),
                "imports_value": imp_v.get(country, 0.0),
            })

    def close(self):
        self.firm.close()
        self.household.close()
        self.household_by_sector.close()
        self.country.close()
        self.inventory.close()
        self.link.close()
        self.trade.close()

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
            atype = row.get("agent_type", "household")
            for sector in set(list(es.keys()) + list(cl.keys())):
                loss_rows.append({
                    "household": row["household"],
                    "agent_type": atype,
                    "time_step": row["time_step"],
                    "sector": sector,
                    "loss": es.get(sector, 0) + cl.get(sector, 0),
                })

    loss_df_all = pd.DataFrame(loss_rows)
    # Only households are welfare. Government + investment are single national accounting
    # agents (see GovernmentDemand / InvestmentDemand): their unmet demand is a separate
    # public-service-disruption / investment-shortfall metric, NOT household welfare.
    def _agent_loss(atype: str) -> float:
        if loss_df_all.empty or "agent_type" not in loss_df_all.columns:
            return 0.0
        return float(loss_df_all.loc[loss_df_all["agent_type"] == atype, "loss"].sum())

    household_loss = _agent_loss("household")
    government_loss = _agent_loss("government")
    investment_loss = _agent_loss("investment")

    # Household-only loss by region/sector/time (feeds the welfare distribution/choropleth).
    if not loss_df_all.empty and "agent_type" in loss_df_all.columns:
        loss_df = loss_df_all[loss_df_all["agent_type"] == "household"].drop(columns=["agent_type"])
    else:
        loss_df = loss_df_all
    if household_table is not None and "id" in household_table.columns and not loss_df.empty:
        ht = household_table.copy()
        ht["id"] = "hh_" + ht["id"].astype(str)
        loss_df["region"] = loss_df["household"].map(ht.set_index("id")["region"])
    groupby_cols = [c for c in ["region", "sector", "time_step"] if c in loss_df.columns]
    if groupby_cols:
        loss_df = loss_df.groupby(groupby_cols, as_index=False)["loss"].sum()

    # Country losses
    c_df = pd.DataFrame(country_data)
    if c_df.empty:
        country_loss = 0.0
    else:
        c_df["loss"] = c_df["extra_spending"] + c_df["consumption_loss"]
        country_loss = c_df["loss"].sum()

    logging.info(f"Cumulated household loss: {household_loss:,.2f} {monetary_units}")
    if government_loss or investment_loss:
        logging.info(f"Cumulated government loss: {government_loss:,.2f}, "
                     f"investment loss: {investment_loss:,.2f} {monetary_units}")
    logging.info(f"Cumulated country loss: {country_loss:,.2f} {monetary_units}")

    if export_folder:
        loss_df.to_csv(export_folder / "loss_per_region_sector_time.csv", index=False)
        if not c_df.empty:
            c_df[["time_step", "country", "loss"]].to_csv(
                export_folder / "loss_per_country.csv", index=False,
            )
        pd.DataFrame({"households": [household_loss], "government": [government_loss],
                      "investment": [investment_loss], "countries": [country_loss]}).to_csv(
            export_folder / "loss_summary.csv", index=False,
        )

    return {"household_loss": household_loss, "government_loss": government_loss,
            "investment_loss": investment_loss, "country_loss": country_loss}


def summarize_criticality_losses(household_data: list, country_data: list) -> dict:
    """Aggregate compact loss metrics for scenario-based criticality runs."""
    hh_df = pd.DataFrame(household_data)
    if hh_df.empty:
        household_loss = 0.0
        by_region = {}
    else:
        hh_df = hh_df.copy()
        hh_df["loss"] = hh_df["extra_spending"].fillna(0.0) + hh_df["consumption_loss"].fillna(0.0)
        household_loss = float(hh_df["loss"].sum())
        if "region" in hh_df.columns:
            by_region = {
                str(region): float(loss)
                for region, loss in hh_df.groupby("region", dropna=False)["loss"].sum().items()
            }
        else:
            by_region = {}

    c_df = pd.DataFrame(country_data)
    if c_df.empty:
        country_loss = 0.0
    else:
        c_df = c_df.copy()
        c_df["loss"] = c_df["extra_spending"].fillna(0.0) + c_df["consumption_loss"].fillna(0.0)
        country_loss = float(c_df["loss"].sum())

    return {
        "total_household_loss": household_loss,
        "household_loss_per_region": dict(sorted(by_region.items())),
        "country_loss": country_loss,
    }


CRITICALITY_RESULT_COLUMNS = [
    "edge", "total_household_loss", "household_loss_per_region",
]


def criticality_result_to_row(result: dict) -> dict:
    return {
        "edge": json.dumps(result["edge_names"]),
        "total_household_loss": float(result["total_household_loss"]),
        "household_loss_per_region": json.dumps(
            result["household_loss_per_region"], sort_keys=True,
        ),
    }


def create_criticality_results_writer(csv_path: Path) -> CsvWriter:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    return CsvWriter(csv_path, CRITICALITY_RESULT_COLUMNS, flush_each_write=True)


def build_criticality_results_table(results: list[dict]) -> pd.DataFrame:
    """Build the compact CSV table for scenario-based criticality outputs."""
    rows = [criticality_result_to_row(result) for result in results]
    return pd.DataFrame(rows, columns=CRITICALITY_RESULT_COLUMNS)


def build_criticality_results_geodata(results: list[dict],
                                      transport_edges: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Map scenario summaries onto the disrupted transport-edge geometries."""
    cols_to_drop = [c for c in ["node_tuple"] if c in transport_edges.columns]
    frames = []
    for result in results:
        edge_names = result["edge_names"]
        scenario_edges = transport_edges.loc[
            transport_edges["name"].isin(edge_names)
        ].drop(columns=cols_to_drop).copy()
        if scenario_edges.empty:
            continue
        scenario_edges["edge"] = json.dumps(edge_names)
        scenario_edges["total_household_loss"] = float(result["total_household_loss"])
        scenario_edges["household_loss_per_region"] = json.dumps(
            result["household_loss_per_region"], sort_keys=True,
        )
        frames.append(scenario_edges)

    if not frames:
        empty = transport_edges.iloc[0:0].drop(columns=cols_to_drop).copy()
        return _ensure_crs(gpd.GeoDataFrame(empty, geometry="geometry"))

    merged = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry")
    return _ensure_crs(merged)


def export_criticality_results(results: list[dict],
                               transport_edges: gpd.GeoDataFrame,
                               csv_path: Path,
                               geojson_path: Path):
    """Write the compact CSV and GeoJSON outputs for scenario-based criticality."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    geojson_path.parent.mkdir(parents=True, exist_ok=True)

    build_criticality_results_table(results).to_csv(csv_path, index=False)
    build_criticality_results_geodata(results, transport_edges).to_file(
        geojson_path, driver="GeoJSON", index=False,
    )


def export_criticality_geojson(results: list[dict],
                               transport_edges: gpd.GeoDataFrame,
                               geojson_path: Path):
    geojson_path.parent.mkdir(parents=True, exist_ok=True)
    build_criticality_results_geodata(results, transport_edges).to_file(
        geojson_path, driver="GeoJSON", index=False,
    )


def export_initial_state(sc_network, export_folder: Path):
    """Export IO matrix and edge list for equilibrium runs."""
    sc_network.calculate_io_matrix().to_csv(export_folder / "io_table.csv")
    sc_network.generate_edge_list().to_csv(export_folder / "sc_network_edgelist.csv")
    logging.info(f"Exported IO table and edge list to {export_folder}")


def export_mrio_summary(mrio, selected, export_folder: Path):
    """Export MRIO reference summaries for reporting comparison.

    Writes three CSVs:
      - mrio_by_sector.csv    — output, input, VA, final_demand, export per sector
      - mrio_by_region.csv    — output, input, VA per region
      - mrio_by_country.csv   — imports (country as exporter) and
                                exports (country as importer) per external country

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

    # --- By country (external buying / selling countries) ---
    # imports:  country appears as an EXPORTER — supply flowing into `selected`
    #           columns from the country's import row.
    # exports:  country appears as an IMPORTER — demand from the country's
    #           export column drawing from `selected` rows.
    import_label = mrio.import_label
    export_label = mrio.export_label
    countries = sorted(
        set(mrio.external_selling_countries) | set(mrio.external_buying_countries)
    )
    imports_per_country = {}
    exports_per_country = {}
    for c in countries:
        if import_label and (c, import_label) in mrio.index:
            imports_per_country[c] = float(mrio.loc[(c, import_label), selected].sum())
        if export_label and (c, export_label) in mrio.columns:
            exports_per_country[c] = float(mrio.loc[selected, (c, export_label)].sum())
    by_country = pd.DataFrame({
        "country": countries,
        "mrio_imports": [imports_per_country.get(c, 0.0) for c in countries],
        "mrio_exports": [exports_per_country.get(c, 0.0) for c in countries],
    })
    by_country.to_csv(export_folder / "mrio_by_country.csv", index=False)

    logging.info(f"Exported MRIO summaries ({len(by_sector)} sectors, "
                 f"{len(by_region)} regions, {len(by_country)} countries) "
                 f"to {export_folder}")


def export_static_tables(firm_table, household_table, transport_edges,
                         transport_nodes, export_folder: Path,
                         countries_spatial_path: Path | None = None):
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
    if countries_spatial_path and Path(countries_spatial_path).exists():
        cgdf = gpd.read_file(countries_spatial_path)
        if "region" in cgdf.columns:
            cgdf = cgdf.rename(columns={"region": "country"})
        keep = [c for c in ["country", "geometry"] if c in cgdf.columns]
        _ensure_crs(cgdf[keep]).to_file(
            export_folder / "country_table.geojson", driver="GeoJSON",
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
