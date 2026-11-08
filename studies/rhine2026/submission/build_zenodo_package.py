r"""Build the Zenodo deposit of the whole-EU data package behind the Rhine 2026 paper. Nothing is uploaded: the
script writes a zip, its README, a sha256 manifest, a draft of the Zenodo metadata and a build report, for the
author to check and upload by hand (Zenodo: New upload -> Dataset -> drag the zip -> paste the metadata).

    python studies/rhine2026/submission/build_zenodo_package.py [--out DIR] [--version V]
           [--data DIR] [--with-calibration-log] [--with-gisco]

Default output: C:/dsc_runs/rhine2026/zenodo/ (outside the repositories). Default data folder: the sibling
checkout disrupt-sc-data/EU of this repository.

What goes in (see CONTENTS below): the EU scope of disrupt-sc-data (economic tables, agents, transport network,
validation targets, the scope manifest and the firm-extractor configuration), and from this repository the
scope's configuration file, the study's additional data (criticality, substitutability, inventory targets and
their sensitivity variants) and the scenario files (gauge profiles, loading tables, Rhine capacities). Run
outputs stay out (they are in the study's run tables, archived separately). Two groups are left out by default and
documented in the README: the GISCO boundary files under Spatial/sources (EuroGeographics copyright, non-commercial
terms, which a CC BY deposit cannot carry) and the calibration log (an internal working document).

Provenance is recorded from git (remote, commit, dirty files among the included ones) for both repositories.
Every file is hashed (sha256) into CHECKSUMS.sha256; the README carries the licence table and the TO CONFIRM
items, which the build report repeats.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]                       # disrupt-sc
DEFAULT_DATA = REPO.parent / "disrupt-sc-data" / "EU"
DEFAULT_OUT = Path("C:/dsc_runs/rhine2026/zenodo")
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")

AUTHOR = {"name": "Colon, Célian",
          "affiliation": "International Institute for Applied Systems Analysis (IIASA), Laxenburg, Austria"}
FUNDING = ("This work was financially supported by the Jubiläumsfonds of the Austrian Central Bank (OeNB) as part "
           "of the FutureGVC project (2024-2028).")
CODE_URL = "https://github.com/ccolon/disrupt-sc"
DATA_URL = "https://github.com/ccolon/disrupt-sc-data"

# ---------------------------------------------------------------------------------------------------- contents
# (zip folder, source root key, relative glob or file, what it is, source and licence key)
# source root keys: "data" = disrupt-sc-data/EU, "repo" = disrupt-sc
CONTENTS = [
    ("EU/Economic", "data", "Economic/mrio.csv",
     "the multi-regional input-output table of the model: 28 regions (EU-27 and Switzerland) x 50 sectors, 12 external partners, 2022, million USD", "oecd"),
    ("EU/Economic", "data", "Economic/sector_table.csv",
     "the 1,400 region-sectors with their type (goods, services, oil and gas), cargo class and value density (USD per tonne, from BACI 2023)", "oecd_baci"),
    ("EU/Economic", "data", "Economic/extract_config_proposed.txt",
     "the extraction block drafted for the MRIO extractor; the block actually run is quoted in scope_manifest.yaml (p4_details)", "own"),
    ("EU/Spatial", "data", "Spatial/firms.geojson",
     "the firm agents: 12,874 points in long format (region, sector, weight); plants for eleven sectors, NUTS employment for the other 39", "firms"),
    ("EU/Spatial", "data", "Spatial/firms_coverage.csv", "per sector and country, the placement source used (plant data, employment, population fallback)", "own"),
    ("EU/Spatial", "data", "Spatial/firms_population.geojson", "the population-weighted fallback placement (NUTS2), used by the smoke runs only", "eurostat"),
    ("EU/Spatial", "data", "Spatial/households.geojson", "251 household agents, one per NUTS2 region, with 2023 population", "eurostat"),
    ("EU/Spatial", "data", "Spatial/countries.geojson", "the 12 external partners at their gateway points (sea nodes and land crossings)", "own"),
    ("EU/Spatial", "data", "Spatial/country_points.csv", "the gateway coordinates behind countries.geojson, with the bloc composition", "own"),
    ("EU/Spatial/sources", "data", "Spatial/sources/employment_nuts2_2022.csv", "Eurostat regional employment 2022 by NUTS2 and activity, as used for the dispersed sectors", "eurostat"),
    ("EU/Spatial/sources", "data", "Spatial/sources/employment_nuts3_2022.csv", "Eurostat regional employment 2022 by NUTS3 and activity", "eurostat"),
    ("EU/Spatial/sources", "data", "Spatial/sources/employment_nuts3_2022_raw.csv", "the same before the country-specific grouping of service activities", "eurostat"),
    ("EU/Spatial/sources", "data", "Spatial/sources/nama_10r_3empers_2022.sdmx.csv", "the Eurostat download (nama_10r_3empers, 2022) the employment files are built from", "eurostat"),
    ("EU/Transport", "data", "Transport/transport.gpkg",
     "the TEN-T multimodal network: 8,694 edges (roads, railways, inland waterways, maritime lanes) with the Rhine chain Basel-Rotterdam named edge by edge", "tentec"),
    ("EU/Transport", "data", "Transport/multimodal.gpkg", "the 1,490 terminal connectors between modes (ports, rail terminals, inland ports)", "tentec"),
    ("EU/Transport", "data", "Transport/port_capacities.csv", "port capacity table (not binding in the paper's runs: ports are unconstrained)", "own"),
    ("EU/Transport", "data", "Transport/port_capacity_overrides.csv", "manual overrides of the port table", "own"),
    ("EU/Transport/tagged", "data", "Transport/tagged/transport.gpkg",
     "the same network with each waterway edge tagged with its waterway and basin (tag_network_attributes.py); the network the calibration rounds from October 2026 ran on", "tentec"),
    ("EU/Transport/tagged", "data", "Transport/tagged/multimodal.gpkg", "the connectors of the tagged network (identical to Transport/multimodal.gpkg)", "tentec"),
    ("EU/Transport/tagged", "data", "Transport/tagged/tagging_report.csv", "the tagging report (edges and km per waterway)", "own"),
    ("EU", "data", "scope_manifest.yaml", "the scope manifest: every onboarding phase with its decisions, sources, counts and known gaps", "own"),
    ("EU", "data", "firm_extractor_config.yaml", "the firm-extractor configuration that built firms.geojson (which source for which sector)", "own"),
    ("EU/validation", "data", "validation/*.csv",
     "the calibration targets: Destatis tables 46321-0005/0014/0015/0016/0017 (inland-waterway freight 2022-2023) and waterway sections 2023, Eurostat mar_go_aa, mar_sg_am_cw and tran_hv_frmod, the derived mode-split and waterway targets, and the port and waterway gazetteers", "destatis_eurostat"),
    ("config", "repo", "config/user_defined_EU.yaml", "the scope's configuration file of the model (file paths, logistics costs, inventory targets, pooling, pipelines)", "own"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/input_criticality.csv",
     "input criticality by buying industry (critical, important, non-critical), from the IHS Markit survey of Pichler et al. 2022", "pichler"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/input_criticality_dfuel0.csv", "the sensitivity variant with the power sector's fuel-oil input non-critical", "pichler"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/product_substitutability.csv", "the 18 poolable products (the same product from several regions is one input)", "own"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/inventory_targets_by_buyer.yaml",
     "inventory targets by buying industry in days (Bundesbank balance-sheet statistics and the physical-stock sources of Supplementary Table S-stocks)", "own"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/inventory_targets_service45.yaml", "the sensitivity variant with a 45-day coping duration for services", "own"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/inventory_targets_construction_nonstorable.yaml", "the variant that treats construction as non-storable (the paper's setting)", "own"),
    ("additional_data", "repo", "studies/rhine2026/additional_data/wiod_correspondence.csv", "the sector correspondence used to map the criticality survey onto the ICIO sectors", "own"),
    ("scenarios", "repo", "studies/rhine2026/scenarios/*.csv",
     "the weekly gauge profiles (2018, 2026 and its vintages, the stress paths q25/q75, the wave experiments), the daily Kaub records, the BfG six-week outlooks, the loading tables (draught_table*.csv with their ledger) and the Rhine capacities per cargo class", "scenarios"),
]

SOURCES = {
    "oecd": ("OECD Inter-Country Input-Output Tables, 2025 edition (2022 table)",
             "OECD terms and conditions: free re-use, including redistribution, with attribution (TO CONFIRM against the current OECD terms page)"),
    "oecd_baci": ("OECD ICIO 2025 (as above); value densities from BACI HS17 2023 (CEPII)",
                  "OECD as above; BACI under the Etalab Open Licence 2.0 (attribution)"),
    "firms": ("Global Energy Monitor trackers (coal mines, oil and gas, steel, cement, aluminium, power), Climate TRACE 2022 source inventory, SPAM 2020 v2r2 crop production, FINEPRINT/Jasansky mining, Eurostat regional employment 2022; centroids from GISCO NUTS 2024",
              "GEM CC BY 4.0; Climate TRACE CC BY 4.0; SPAM CC BY 4.0; FINEPRINT CC BY 4.0 (TO CONFIRM the Zenodo record's licence); Eurostat: free re-use with acknowledgement; the points are derived data, no boundary is redistributed"),
    "eurostat": ("Eurostat (regional employment nama_10r_3empers; population demo_r_pjanaggr3) and GISCO NUTS 2024 centroids",
                 "Eurostat re-use policy: free re-use with acknowledgement of the source"),
    "tentec": ("TENtec, the European Commission's TEN-T information system (comprehensive network and EFTA extension), via tentec-extractor; Rhine chain named and waterway tags added by the author",
               "European Commission re-use policy (Decision 2011/833/EU; CC BY 4.0 compatible) (TO CONFIRM against the TENtec portal's terms, which were unreachable when this package was built)"),
    "destatis_eurostat": ("Destatis GENESIS-Online tables 46321-0005, -0014, -0015, -0016, -0017 (2022-2023) and the 2023 waterway sections; Eurostat mar_go_aa, mar_sg_am_cw, tran_hv_frmod",
                          "Destatis: Datenlizenz Deutschland - Namensnennung - Version 2.0 (dl-de/by-2-0); Eurostat: free re-use with acknowledgement"),
    "pichler": ("Pichler, Pangallo, del Rio-Chanona, Lafond and Farmer (2022), input criticality survey (IHS Markit), Zenodo record of the paper",
                "CC BY 4.0 (the Zenodo record) (TO CONFIRM)"),
    "scenarios": ("Gauge records from PEGELONLINE (German Federal Waterways and Shipping Administration, WSV); six-week outlooks from the Federal Institute of Hydrology (BfG); loading tables compiled by the author from van Dorsser et al. 2020, operators' rate schedules (Contargo 2026) and the BfG/press count of August 2026; capacities from the model's baseline",
                  "PEGELONLINE: Datenlizenz Deutschland - Zero - Version 2.0 (TO CONFIRM); BfG outlook: TO CONFIRM the re-use terms of the ENS product (the files hold the weekly medians and the 25th/75th percentiles at Kaub only); compilations: CC BY 4.0"),
    "own": ("Built by the author for this study (onboarding scripts and study scripts of the code repository)", "CC BY 4.0 (this deposit)"),
}

EXCLUDED_DEFAULT = [
    ("EU/Spatial/sources/NUTS_RG_20M_*.geojson, nuts2_admin.geojson, nuts3_admin*.geojson",
     "GISCO NUTS boundaries 2021 and 2024 (1:20M, EPSG:4326, levels 2 and 3) and the per-country NUTS3 files cut from them: '(c) EuroGeographics for the administrative boundaries', GISCO terms (non-commercial use), which a CC BY deposit cannot carry. Download: https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics (NUTS_RG_20M_2024_4326_LEVL_2/3, NUTS_RG_20M_2021_4326_LEVL_2/3); nuts3_admin_<ISO3>.geojson = the level-3 polygons of each country with shapeName = NUTS code. Needed only to rebuild firms.geojson with the firm extractor, not to run the model. Re-run with --with-gisco to include them."),
    ("EU/calibration_log.md", "the calibration diary (internal working document, 230 kB). Re-run with --with-calibration-log to include it."),
    ("EU/runs/", "run logs; the run outputs of the paper are archived with the study's run tables."),
    ("EU/Transport/scenario_edge_capacities.csv", "a per-edge capacity file written by studies/rhine2026/baseline_capacities.py for the capacity-gate smoke tests of September 2026; the paper's runs do not read it (their Rhine capacities per cargo class are in scenarios/)."),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True,
                              encoding="utf-8", errors="replace").stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def paper_title() -> str:
    p = OVERLEAF / "main.tex"
    if not p.exists():
        return "TO CONFIRM (the Overleaf copy was not found when the package was built)"
    s = p.read_text(encoding="utf-8", errors="replace")
    i = s.find("\\title{")
    if i < 0:
        return "TO CONFIRM"
    j, depth = i + len("\\title{"), 1
    k = j
    while k < len(s) and depth:
        depth += {"{": 1, "}": -1}.get(s[k], 0)
        k += 1
    t = s[j:k - 1]
    t = re.sub(r"\\\\\s*", " ", t)
    t = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?", "", t)
    t = re.sub(r"[{}]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA, help="the EU folder of disrupt-sc-data")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--with-calibration-log", action="store_true")
    ap.add_argument("--with-gisco", action="store_true")
    a = ap.parse_args()

    data, repo, out = a.data.resolve(), REPO, a.out
    if not data.exists():
        sys.exit(f"data folder not found: {data}")
    out.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    roots = {"data": data, "repo": repo}
    repos = {"data": data.parent, "repo": repo}

    contents = list(CONTENTS)
    if a.with_calibration_log:
        contents.append(("EU", "data", "calibration_log.md", "the calibration diary of the scope (rounds, decisions, residuals)", "own"))
    if a.with_gisco:
        contents.append(("EU/Spatial/sources", "data", "Spatial/sources/*.geojson",
                         "GISCO NUTS boundaries 2021 and 2024 (1:20M) and the per-country NUTS3 files; (c) EuroGeographics for the administrative boundaries, GISCO non-commercial terms", "gisco"))
        SOURCES["gisco"] = ("Eurostat GISCO, NUTS 2021 and 2024, 1:20M", "(c) EuroGeographics for the administrative boundaries; GISCO terms: non-commercial use only. NOT covered by the CC BY licence of the deposit; state this in the Zenodo record or leave the files out")

    # ------------------------------------------------------------------ collect the files
    files = []      # (zip path, source path, group description, source key)
    missing = []
    for zdir, rootkey, pattern, what, src in contents:
        root = roots[rootkey]
        matches = sorted(root.glob(pattern)) if any(c in pattern for c in "*?[") else [root / pattern]
        matches = [m for m in matches if m.is_file() and "__pycache__" not in m.parts]
        if not matches:
            missing.append((rootkey, pattern))
            continue
        for m in matches:
            files.append((f"{zdir}/{m.name}", m, what, src, rootkey))
    seen = {}
    for z, m, *_ in files:
        if z in seen and seen[z] != m:
            sys.exit(f"two sources for the same zip path {z}: {seen[z]} and {m}")
        seen[z] = m

    # ------------------------------------------------------------------ provenance
    prov = {}
    for key, r in repos.items():
        rel_paths = [str(m.relative_to(r)).replace("\\", "/") for _, m, _, _, rk in files if rk == key]
        status = git(r, "status", "--porcelain", "--", *rel_paths) if rel_paths else ""
        prov[key] = {
            "remote": git(r, "remote", "get-url", "origin"),
            "commit": git(r, "rev-parse", "HEAD"),
            "commit_date": git(r, "log", "-1", "--format=%cd", "--date=short"),
            "dirty": [ln for ln in status.splitlines() if ln.strip()],
        }

    # ------------------------------------------------------------------ hashes and sizes
    rows, total = [], 0
    for z, m, what, src, rk in files:
        size = m.stat().st_size
        total += size
        rows.append({"zip": z, "src": str(m), "bytes": size, "sha256": sha256(m), "what": what, "source": src, "repo": rk})

    title = paper_title()
    zip_name = f"disruptsc_eu_rhine2026_data_v{a.version}.zip"

    # ------------------------------------------------------------------ README
    by_group = {}
    for zdir, rootkey, pattern, what, src in contents:
        by_group.setdefault(zdir, []).append((pattern, what, src))
    lines = [
        f"# DisruptSC whole-EU scope: data package of the Rhine 2026 low-water study",
        "",
        f"Version {a.version}, built {today} by `studies/rhine2026/submission/build_zenodo_package.py` of the code repository.",
        "",
        f"Paper: *{title}* (Célian Colon, IIASA, 2026; submitted). Model: DisruptSC v2, {CODE_URL} (GPL-3.0).",
        "This package holds the inputs that the model reads to reproduce the runs of the paper: the economic tables, the firm,",
        "household and external-partner agents, the multimodal transport network, the validation targets of the calibration,",
        "the scope's configuration, the study's additional data (input criticality, poolable products, inventory targets) and",
        "the scenario files (gauge profiles, loading tables, Rhine capacities). The run outputs are not in it.",
        "",
        "## Provenance",
        "",
        "| Repository | Remote | Commit | Date | Uncommitted among the files included |",
        "|---|---|---|---|---|",
    ]
    for key, label in (("data", "disrupt-sc-data (folder EU/)"), ("repo", "disrupt-sc (config, additional_data, scenarios)")):
        p = prov[key]
        dirty = "; ".join(p["dirty"]) if p["dirty"] else "none"
        lines.append(f"| {label} | {p['remote']} | `{p['commit'][:12]}` | {p['commit_date']} | {dirty} |")
    lines += [
        "",
        "The code repository is authoritative for the files copied from it (config, additional_data, scenarios); the data",
        "repository for the EU folder. The versions of the code that produced each batch of runs are listed, commit by commit,",
        "in `studies/rhine2026/forecast_manifest.md` of the code repository.",
        "",
        "## How to use",
        "",
        f"1. Clone {CODE_URL} and check out the commit above (or the release tagged for the paper); install it as its README says.",
        "2. Unpack this archive; place the `EU/` folder in the model's data root (by default the sibling folder `disrupt-sc-data/`",
        "   of the code checkout, so that `disrupt-sc-data/EU/Economic/mrio.csv` exists), `config/user_defined_EU.yaml` in the",
        "   code checkout's `config/`, and `additional_data/` and `scenarios/` in `studies/rhine2026/` (the configuration refers to",
        "   them with the `repo:` prefix).",
        "3. Run the scope as `onboarding/RUNBOOK.md` and `studies/rhine2026/README.md` of the code repository describe (an",
        "   `initial_state` run reproduces the baseline; the scenario runs of the paper are the job lists of the study folder).",
        "",
        "## Contents",
        "",
        "| Folder | File(s) | What it is | Source |",
        "|---|---|---|---|",
    ]
    for zdir, items in by_group.items():
        for pattern, what, src in items:
            lines.append(f"| `{zdir}/` | `{Path(pattern).name}` | {what} | {SOURCES[src][0]} |")
    lines += [
        "",
        f"{len(rows)} files, {total / 1048576:.1f} MB uncompressed. `CHECKSUMS.sha256` lists every file with its SHA-256; `zenodo_metadata.json`",
        "is the metadata draft of the deposit.",
        "",
        "## Licences",
        "",
        "The deposit as a whole is published under CC BY 4.0. The files derived from third-party data keep the terms of their",
        "sources, listed here; the items marked TO CONFIRM are for the author to check before upload.",
        "",
        "| Source | Terms |",
        "|---|---|",
    ]
    for key, (src, terms) in SOURCES.items():
        lines.append(f"| {src} | {terms} |")
    lines += [
        "",
        "## Left out, and why",
        "",
    ]
    for what, why in EXCLUDED_DEFAULT:
        if a.with_gisco and what.startswith("EU/Spatial/sources/NUTS"):
            continue
        if a.with_calibration_log and what.startswith("EU/calibration_log"):
            continue
        lines.append(f"- `{what}`: {why}")
    lines += [
        "",
        "## Funding",
        "",
        FUNDING,
        "",
        "## How to cite",
        "",
        f"Colon, C. ({today[:4]}). DisruptSC whole-EU scope: data package of the Rhine 2026 low-water study (v{a.version}) [Data set]. Zenodo. DOI to be assigned on upload.",
        "",
    ]
    readme = "\n".join(lines)

    # ------------------------------------------------------------------ Zenodo metadata draft (deposit API schema)
    description = (
        f"<p>Inputs of the DisruptSC model for the whole-EU scope of the study <i>{title}</i> (C. Colon, IIASA, 2026): "
        "the multi-regional input-output table (OECD ICIO 2022, 28 regions x 50 sectors, 12 external partners), the firm, household "
        "and external-partner agents, the TEN-T multimodal transport network with the Rhine chain named edge by edge, the validation "
        "targets of the calibration, the scope's configuration, the input-criticality, poolable-product and inventory-target tables, "
        "and the scenario files (Kaub gauge profiles for 2018 and 2026, loading tables, Rhine capacities per cargo class).</p>"
        f"<p>The code is at {CODE_URL} (GPL-3.0); README.md in the archive gives the provenance (repository commits), the licence of "
        "each source and the instructions to run the model on this package. Run outputs are not included.</p>"
        f"<p>Funding: {FUNDING}</p>"
    )
    related = [
        {"identifier": f"{CODE_URL}/tree/{prov['repo']['commit']}", "relation": "isSupplementTo", "resource_type": "software"},
        {"identifier": f"{DATA_URL}/tree/{prov['data']['commit']}", "relation": "isDerivedFrom", "resource_type": "dataset"},
    ]
    metadata = {
        "metadata": {
            "title": "DisruptSC whole-EU scope: data package of the Rhine 2026 low-water study",
            "upload_type": "dataset",
            "publication_date": today,
            "description": description,
            "creators": [AUTHOR],     # add "orcid": "0000-0000-0000-0000" (TO CONFIRM: the author's ORCID)
            "access_right": "open",
            "license": "cc-by-4.0",
            "keywords": ["supply chains", "agent-based model", "transport network", "Rhine", "low water", "drought",
                         "Europe", "input-output", "DisruptSC", "TEN-T"],
            "related_identifiers": related,
            "version": a.version,
            "language": "eng",
            "notes": ("The GISCO boundary files that the firm placement used are not in the archive (EuroGeographics copyright, "
                      "non-commercial terms); README.md says where to download them. Add the paper's DOI as a related identifier "
                      "(isSupplementTo) on acceptance."),
        }
    }

    # ------------------------------------------------------------------ write everything
    checksums = "\n".join(f"{r['sha256']}  {r['zip']}" for r in rows) + "\n"
    (out / "README.md").write_text(readme, encoding="utf-8")
    (out / "CHECKSUMS.sha256").write_text(checksums, encoding="utf-8")
    (out / "zenodo_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    zpath = out / zip_name
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        zf.writestr("README.md", readme)
        zf.writestr("CHECKSUMS.sha256", checksums)
        zf.writestr("zenodo_metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False))
        for r in rows:
            zf.write(r["src"], r["zip"])
    zsize = zpath.stat().st_size

    flags = [ln for ln in readme.splitlines() if "TO CONFIRM" in ln]
    report = [
        f"Zenodo package built {today}: {zpath} ({zsize / 1048576:.1f} MB zipped, {total / 1048576:.1f} MB unpacked, {len(rows)} files)",
        f"sha256 of the zip: {sha256(zpath)}",
        "",
        "Provenance:",
    ]
    for key, p in prov.items():
        report.append(f"  {key}: {p['remote']} @ {p['commit'][:12]} ({p['commit_date']}); uncommitted among included files: {'; '.join(p['dirty']) or 'none'}")
    if missing:
        report += ["", "MISSING (pattern matched nothing):"] + [f"  {rk}: {pat}" for rk, pat in missing]
    report += ["", "Largest files:"]
    for r in sorted(rows, key=lambda r: -r["bytes"])[:8]:
        report.append(f"  {r['bytes'] / 1048576:7.1f} MB  {r['zip']}")
    report += ["", "TO CONFIRM before upload (from README.md and the metadata):",
               "  - the author's ORCID (add to creators[0].orcid in zenodo_metadata.json)",
               "  - the GISCO files are left out by default (--with-gisco to include them, with their notice)",
               "  - the release tag of the code repository (the metadata points at the commit)"]
    report += [f"  - {ln.strip()}" for ln in flags]
    report += ["", "Upload steps: zenodo.org -> New upload -> Upload the zip -> Resource type Dataset -> fill title, description,",
               "creators, licence CC BY 4.0, keywords, related identifiers from zenodo_metadata.json -> Save draft -> reserve the DOI",
               "-> paste the DOI in the manuscript's Data availability statement -> Publish on acceptance (or now, with the",
               "version noted). The code: tag a release on GitHub with the Zenodo-GitHub integration switched on for the",
               "repository, which mints the code DOI; cite both in Data and Code availability."]
    report_text = "\n".join(report) + "\n"
    (out / "build_report.txt").write_text(report_text, encoding="utf-8")
    print(report_text)


if __name__ == "__main__":
    main()
