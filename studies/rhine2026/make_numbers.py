"""Write the manuscript's numbers.tex from the study's outputs (7 Oct 2026, the batch on the rebuilt loading table).

Every macro of the paper is computed here from the compare tables of the batch (main, paired, sensitivities), the firm
tables of the packed runs, the link-level run's validation outputs, the profiles and the loading table, and the
benchmark module; the few constants that are not outputs (model size, the earlier price-with-closures representation,
the Destatis figure) are listed at the end. Rerun after every batch:

    python studies/rhine2026/make_numbers.py [--tag s07] [--overleaf <repo>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
AD = HERE / "additional_data"
RUNS = Path("C:/dsc_runs/rhine2026")
OVERLEAF = Path("C:/Users/Celian/OneDrive/DisruptSC/Paper_Rhine2026/git-overleaf/6aaa98617957ab816097822f")
sys.path.insert(0, str(HERE))
from read_batch_20261007 import table, firm_losses  # noqa: E402
from matched_estimand_2018 import model_path  # noqa: E402
from benchmark_ademmer import record, EVENT_MONTHS  # noqa: E402

LEVERS = ["stock7", "deep20", "fleet", "stock7t", "package"]
WORDS = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven"}


def r1(x):
    return f"{x:.1f}"


def r2(x):
    return f"{x:.2f}"


def pct(x):
    return f"{int(np.floor(x + 0.5))}"          # half up


def main(tag: str, overleaf: Path, date_list: str):
    # 2 Nov 2026: the batch of 7 October named its revision runs 2026_rev_*, its 15-day waves wave09_* and its waves
    # wave07_*, in lists of three dates; a later batch carries one tag in every name (2026_<tag>_rail50, wave_<tag>_A,
    # wave_<tag>_A_rest15) and one list date (--lists), so the names and the table dates are derived here.
    old_naming = tag == "s07"
    REV = "rev" if old_naming else tag
    WV9 = "wave09" if old_naming else f"wave_{tag}"
    cross_date = "20261009" if old_naming else date_list
    norail_date = "20261020" if old_naming else date_list
    m = table(AD / f"compare_runs_batch_jobs_{date_list}_main.csv")
    p = table(AD / f"compare_runs_batch_jobs_{date_list}_paired.csv")
    rv = AD / f"compare_runs_batch_jobs_{date_list}_rev.csv"
    r = table(rv) if rv.exists() else pd.DataFrame()
    lv = AD / f"compare_runs_batch_jobs_{date_list}_ladder.csv"
    ld = table(lv) if lv.exists() else pd.DataFrame()
    t = pd.concat([m, p] + ([r] if len(r) else []) + ([ld] if len(ld) else []))
    B, B18 = f"2026_{tag}_base", f"2018_{tag}_base"
    q26 = m.loc[B, "DEU_cum_mUSD"] / m.loc[B, "DEU_%quarter"]
    q18 = m.loc[B18, "DEU_cum_mUSD"] / m.loc[B18, "DEU_%quarter"]
    M = {}       # macro -> (value string, comment)

    def put(name, val, comment=""):
        M[name] = (val, comment)

    # ---- 2026 baseline
    b = m.loc[B]
    put("DEUlossBn", r1(b.DEU_cum_mUSD / 1e3), "bn USD, cumulated German value-added loss")
    put("DEUlossQ", r2(b["DEU_%quarter"]), "% of a quarter of German value added")
    fd = firm_losses(RUNS / B); de = fd[fd.region == "DEU"]; tot = de.loss.sum()
    ind = de[de.sector.str[:1].isin(list("BCDE"))]
    put("IndQ", r2(ind.loss.sum() / q26), "industry (NACE B-E) part, % of a quarter")
    put("IndustryShare", pct(100 * ind.loss.sum() / tot), "% of the German gross loss in industry (B-E)")
    put("DEUpeakWeek", r1(b["DEU_peak_%week"]), f"% of a week of German value added at the peak (week {int(b.DEU_peak_week)})")
    put("EUlossBn", r1(b.EU_cum_mUSD / 1e3), "bn USD, the 28 economies")
    put("ConsLossBn", r1(b.cons_loss_cum_mUSD / 1e3), "bn USD, household consumption loss")
    w = de.groupby("time_step").loss.sum()
    put("EarlyWaveQ", r2(w.loc[1:6].sum() / q26), "weeks 1-6 (22 June - 2 August), % of a quarter")
    put("AugWaveQ", r2(w.loc[7:11].sum() / q26), "August trough (weeks 7-11), all sectors")
    put("AugWaveIndQ", r2(ind[ind.time_step.between(7, 11)].loss.sum() / q26), "industry part of the August trough")
    put("AugWaveEurBn", r1(ind[ind.time_step.between(7, 11)].loss.sum() / 1e3 * 0.92), "EUR bn, industry part of the August trough (0.92 EUR per USD)")
    put("AutumnWaveQ", r2(w.loc[12:19].sum() / q26), "autumn trough (weeks 12-19, 7 September - 1 November)")
    e26 = [p.loc[f"2026_{tag}_seed{s}_base", "DEU_%quarter"] for s in range(1, 11)] + [b["DEU_%quarter"]]
    put("EnsMean", r2(np.mean(e26)), "ensemble of 11 supply-chain draws, mean"); put("EnsSd", r2(np.std(e26, ddof=1))); put("EnsMin", r2(min(e26))); put("EnsMax", r2(max(e26)))
    put("EnsMeanBn", r1(np.mean(e26) * q26 / 1e3), "bn USD, the ensemble mean of the German loss (22 Oct 2026: the headline is the mean over the eleven networks)")
    eu26 = [p.loc[f"2026_{tag}_seed{s}_base", "EU_cum_mUSD"] for s in range(1, 11)] + [b.EU_cum_mUSD]
    put("EUlossEnsBn", r1(np.mean(eu26) / 1e3), "bn USD, the 28 economies, mean over the eleven networks")
    put("DEUnetBn", r1(b.DEU_net_mUSD / 1e3), "bn USD, German net loss (backlog left at the end of the run + the perishable sectors), reference network")
    put("CorridorFirmsBelow", r1(b["firms<99%_peak_%"]), "% of firms below 99 % of baseline output at the peak")
    rec = de[de.sector.str[:1].isin(list("ABCF"))].loss.sum()
    put("PerishableShare", pct(100 * (1 - rec / tot)), "% of the German gross loss in the sectors that cannot catch up (D, E, G-T)")
    grp = de.sector.map(lambda s: "A" if s[0] == "A" else ("I" if s[0] in "BCDE" else ("F" if s[0] == "F" else "S")))
    g = de.groupby(grp).loss.sum() / tot * 100
    put("ShareConstruction", pct(g.get("F", 0)), "F construction, % of the German gross loss")
    put("ShareAgri", pct(g.get("A", 0)), "A agriculture"); put("ShareServices", pct(g.get("S", 0)), "G-T services")
    put("ShareUtilities", pct(100 * de[de.sector.isin(["D", "E"])].loss.sum() / tot), "D+E utilities, inside industry")
    sec = de.groupby("sector").loss.sum() / tot * 100
    for mac, s in (("ShareLogistics", "H52"), ("ShareLandTransport", "H49"), ("SharePower", "D"), ("ShareChemicals", "C20"),
                   ("ShareHospitality", "I"), ("ShareShipping", "H50"), ("ShareRefining", "C19"), ("ShareCement", "C23")):
        put(mac, pct(sec.get(s, 0)), s)
    put("NetShare", pct(100 * b.DEU_net_mUSD / b.DEU_cum_mUSD), "German net loss as % of gross")
    put("DelayCost", f"{b.DEU_delay_mUSD:,.0f}", "mUSD")
    lf = pd.read_csv(RUNS / f"2026_{tag}_full" / "link_flows_disrupted.csv.gz")
    dl = lf[(lf.buyer_region == "DEU") & (lf.time_step >= 1)]
    short = (dl.base_realized - dl.realized_delivery).clip(lower=0).sum(); wh = dl.withheld_by_transport.sum()
    put("TransportWithheldShare", pct(100 * wh / short), f"% of the delivery shortfall of German buyers withheld at the river ({wh:,.0f} of {short:,.0f} mUSD)")
    put("DEUmissBn", r1(short / 1e3), "bn USD of deliveries that German buyers miss over the event")
    put("DEUwithheldBn", r1(wh / 1e3), "of which withheld at the river")
    put("NonDEshare", pct(100 * (1 - b.DEU_cum_mUSD / b.EU_cum_mUSD)), "% of the loss of the 28 economies outside Germany")
    put("FRAlossBn", r1(b.FRA_cum_mUSD / 1e3))
    # ---- 2018
    b18 = m.loc[B18]
    fd18 = firm_losses(RUNS / B18); de18 = fd18[fd18.region == "DEU"]; tot18 = de18.loss.sum()
    ind18 = de18[de18.sector.str[:1].isin(list("BCDE"))]
    put("DEUlossQyy", r2(b18["DEU_%quarter"]), "2018, % of a quarter, all sectors"); put("DEUlossBnyy", r1(b18.DEU_cum_mUSD / 1e3))
    put("IndQyy", r2(ind18.loss.sum() / q18), "industry part"); put("IndustryShareyy", pct(100 * ind18.loss.sum() / tot18))
    put("DEUpeakWeekyy", r1(b18["DEU_peak_%week"]), f"% of a week, week {int(b18.DEU_peak_week)}")
    e18 = [m.loc[f"2018_{tag}_seed{s}", "DEU_%quarter"] for s in range(1, 11)] + [b18["DEU_%quarter"]]
    put("EnsMeanyy", r2(np.mean(e18))); put("EnsSdyy", r2(np.std(e18, ddof=1))); put("EnsMinyy", r2(min(e18))); put("EnsMaxyy", r2(max(e18)))
    rec18 = de18[de18.sector.str[:1].isin(list("ABCF"))].loss.sum()
    put("PerishableShareyy", pct(100 * (1 - rec18 / tot18)))
    g18 = de18.groupby(de18.sector.map(lambda s: "A" if s[0] == "A" else ("I" if s[0] in "BCDE" else ("F" if s[0] == "F" else "S")))).loss.sum() / tot18 * 100
    put("ShareServicesyy", pct(g18.get("S", 0)))
    # ---- the 2018 industrial path and the record
    mp = model_path(RUNS / B18, 2018)
    for mo in ("Aug", "Sep", "Oct", "Nov", "Dec"):
        put(f"Ind{mo}", r1(mp[f"ind_{mo}"]), f"model, monthly shortfall of German industrial production, % ({mp[f'ind_{mo}']:.2f})")
    put("ModelInt", r1(mp["ind_integrated_pct_months"]), "percent-months, reference draw")
    ints = [mp["ind_integrated_pct_months"]] + [model_path(RUNS / f"2018_{tag}_seed{s}", 2018)["ind_integrated_pct_months"] for s in range(1, 11)]
    rt, rs = record(2018, 1)
    put("ModelIntEnsMean", r1(np.mean(ints))); put("ModelIntEnsSd", r1(np.std(ints, ddof=1))); put("ModelIntEnsMin", r1(min(ints))); put("ModelIntEnsMax", r1(max(ints)))
    put("DrawsInBand", WORDS[sum(rs["p16"] <= v <= rs["p84"] for v in ints)], f"draws inside the record's 16-84 % band {rs['p16']:.2f}-{rs['p84']:.2f} (of eleven)")
    put("DrawsInWideBand", WORDS[sum(rs["p2_5"] <= v <= rs["p97_5"] for v in ints)], "inside the 95 % band")
    ev = rt[rt.month.isin(EVENT_MONTHS[2018])]
    for mo, v in zip(("Aug", "Sep", "Oct", "Nov", "Dec"), ev.central):
        put(f"Rec{mo}", r2(v))
    put("RecordInt", r1(rs["integral"]), "percent-months, the published dynamic specification (column 1)")
    put("RecordIntLow", r1(rs["p16"])); put("RecordIntHigh", r1(rs["p84"])); put("RecordIntLowW", r1(rs["p2_5"])); put("RecordIntHighW", r1(rs["p97_5"]))
    _, s3 = record(2018, 3, draws=1); put("RecordIntNoLag", r1(s3["integral"]), "contemporaneous-only specification (column 3)")
    put("RecordQ", r2(rs["integral"] * 0.25 / 3), "the record's industry channel in % of a quarter"); put("RecordQLow", r2(rs["p16"] * 0.25 / 3)); put("RecordQHigh", r2(rs["p84"] * 0.25 / 3))
    put("ExPostLow", "0.3"); put("ExPostHigh", "0.4")
    # ---- the stock ladder: the rebuilt-table runs if they exist, else the ladder of 28 Sep (earlier table)
    lad = {1.25: f"2018_{tag}_inv125", 1.5: f"2018_{tag}_inv150", 2.0: f"2018_{tag}_inv200"}
    if all((RUNS / v / "firm_data.csv").exists() for v in lad.values()) and all(v in t.index for v in lad.values()):
        src = "the ladder on the rebuilt table"
        lq = {k: t.loc[v, "DEU_%quarter"] for k, v in lad.items()}; li = {k: model_path(RUNS / v, 2018)["ind_integrated_pct_months"] for k, v in lad.items()}
    else:
        src = "LADDER OF 28 SEP ON THE EARLIER TABLE (rerun pending: jobs_20261007_ladder.txt)"
        old = table(AD / "compare_runs_batch_20260929_gs1paper.csv") if (AD / "compare_runs_batch_20260929_gs1paper.csv").exists() else None
        lq = {1.25: 0.76, 1.5: 0.59, 2.0: 0.38}
        li = {k: model_path(RUNS / v, 2018)["ind_integrated_pct_months"] for k, v in {1.25: "2018_gs_inv125", 1.5: "2018_gs_inv150", 2.0: "2018_gs"}.items()}
    put("LadderA", r2(lq[1.25]), f"x1.25, all sectors, % of a quarter ({src})"); put("LadderB", r2(lq[1.5])); put("LadderD", r2(lq[2.0]))
    put("LadderIntA", r1(li[1.25]), "x1.25, industrial shortfall, percent-months"); put("LadderIntB", r1(li[1.5])); put("LadderIntD", r1(li[2.0]))
    # the alternative river (the priced river with closures): the rerun of 3 Nov 2026 on the per-class calibration when its
    # runs carry firm data (2018_<tag>_priced, _priced_inv150, _priced_inv200), else the first version's runs of 22-28 Sep
    priced = {1.0: f"2018_{tag}_priced", 1.5: f"2018_{tag}_priced_inv150", 2.0: f"2018_{tag}_priced_inv200"}
    if not all((RUNS / v / "firm_data.csv").exists() for v in priced.values()):
        priced = {1.0: "2018_baseline", 1.5: "2018_inv150", 2.0: "2018_pipe"}
    pr = model_path(RUNS / priced[1.0], 2018)
    put("PricedInt", r1(pr["ind_integrated_pct_months"]), f"priced river with closures, x1 ({priced[1.0]}; S6)"); put("PricedNov", r1(pr["ind_Nov"]))
    put("PricedIntB", r1(model_path(RUNS / priced[1.5], 2018)["ind_integrated_pct_months"]), f"priced river with closures, x1.5 ({priced[1.5]})")
    put("PricedIntC", r1(model_path(RUNS / priced[2.0], 2018)["ind_integrated_pct_months"]), f"priced river with closures, x2 ({priced[2.0]})")
    # ---- structural sensitivities
    for mac, run in (("TableLowInt", f"2018_{tag}_tablelow"), ("TableHighInt", f"2018_{tag}_tablehigh"), ("SupTwoInt", f"2018_{tag}_sup2")):
        put(mac, r1(model_path(RUNS / run, 2018)["ind_integrated_pct_months"]), run)
    for mac, run in (("TableLowQ", f"2026_{tag}_tablelow"), ("TableHighQ", f"2026_{tag}_tablehigh"), ("TableLowQyy", f"2018_{tag}_tablelow"), ("TableHighQyy", f"2018_{tag}_tablehigh"),
                     ("SupTwoQ", f"2026_{tag}_sup2"), ("SupTwoQyy", f"2018_{tag}_sup2"), ("GateOnlyQ", f"2026_{tag}_gateonly"), ("SurchargeOnlyQ", f"2026_{tag}_surchargeonly")):
        put(mac, r2(m.loc[run, "DEU_%quarter"]), run)
    put("NoPoolQ", r1(m.loc[f"2026_{tag}_nopool", "DEU_%quarter"])); put("NoPoolQyy", r1(m.loc[f"2018_{tag}_nopool", "DEU_%quarter"]))
    # ---- waves
    wv = tag.replace("s", "wave") if old_naming else f"wave_{tag}"
    A, Bw = m.loc[f"{wv}_A", "DEU_%quarter"], m.loc[f"{wv}_B", "DEU_%quarter"]; base = b["DEU_%quarter"]
    put("WaveAQ", r2(A), "first wave alone"); put("WaveBQ", r2(Bw), "second wave alone"); put("WaveSumQ", r2(A + Bw))
    put("WaveBafterAQ", r2(base - A), "what the second wave adds after the first"); put("WaveBratio", r2((base - A) / Bw))
    put("WaveInterShare", pct(100 * (base - A - Bw) / (A + Bw)), "interaction without a gap, % of the sum")
    gaps = {k: m.loc[f"{wv}_AB_gap{k}", "DEU_%quarter"] for k in (1, 2, 4, 8)}
    put("WaveInterOne", pct(100 * (gaps[1] - A - Bw) / (A + Bw))); put("WaveInterTwo", pct(100 * (gaps[2] - A - Bw) / (A + Bw)))
    put("WaveInterFour", pct(100 * (gaps[4] - A - Bw) / (A + Bw))); put("WaveInterEight", f"{100 * (gaps[8] - A - Bw) / (A + Bw):.1f}", "signed")
    flat = m.loc[f"{wv}_flat", "DEU_%quarter"]
    put("FlatQ", r2(flat), "the same capacity shortfall spread evenly"); put("TroughPremium", pct(100 * (base / flat - 1)), "% by which the season exceeds the flat profile")
    # ---- levers
    for lev in LEVERS:
        ref = 100 * (1 - m.loc[f"2026_{tag}_{lev}", "DEU_cum_mUSD"] / b.DEU_cum_mUSD)
        pairs = [100 * (1 - p.loc[f"2026_{tag}_seed{s}_{lev}", "DEU_cum_mUSD"] / p.loc[f"2026_{tag}_seed{s}_base", "DEU_cum_mUSD"]) for s in range(1, 11)]
        name = {"stock7": "Stock", "deep20": "Deep", "fleet": "Fleet", "stock7t": "StockT", "package": "Package"}[lev]
        put(f"Lev{name}", pct(ref), f"{lev}: German gross loss avoided, % of the base, reference draw")
        put(f"Lev{name}Range", f"{pct(min(pairs))}--{pct(max(pairs))}", "range over ten paired draws")
        put(f"Lev{name}Avg", pct(float(np.mean(pairs + [ref]))), "mean over the eleven networks (reference + ten paired draws)")
        put(f"LevEU{name}", pct(100 * (1 - m.loc[f"2026_{tag}_{lev}", "EU_cum_mUSD"] / b.EU_cum_mUSD)))
    up = sum(p.loc[f"2026_{tag}_seed{s}_fleet", "DEU_peak_%week"] > p.loc[f"2026_{tag}_seed{s}_base", "DEU_peak_%week"] for s in range(1, 11))
    put("FleetPeak", r1(m.loc[f"2026_{tag}_fleet", "DEU_peak_%week"]), f"peak week under the fleet lever, % of a week (base {b['DEU_peak_%week']:.2f}); the peak rises in {up} of 10 further draws")
    put("FleetPeakUpDraws", WORDS[up])
    put("StockAvoidedBn", r1((b.DEU_cum_mUSD - m.loc[f"2026_{tag}_stock7", "DEU_cum_mUSD"]) / 1e3), "bn USD avoided by one week of stocks")
    put("StockTAvoidedBn", r1((b.DEU_cum_mUSD - m.loc[f"2026_{tag}_stock7t", "DEU_cum_mUSD"]) / 1e3))
    # ---- the river
    dt = pd.read_csv(HERE / "scenarios" / "draught_table.csv")
    lfn = lambda cm: float(np.interp(cm, dt.kaub_cm, dt.load_factor, left=dt.load_factor.iloc[0], right=1.0))
    for year, macs in ((2026, {"Jun": "KaubPassJun", "Jul": "KaubPassJul", "Aug": "KaubPassAug", "Sep": "KaubPassSep", "Oct": "KaubPassOct", "Nov": "KaubPassNov"}),
                       (2018, {"Jul": "KaubPassJulyy", "Aug": "KaubPassAugyy", "Sep": "KaubPassSepyy", "Oct": "KaubPassOctyy", "Nov": "KaubPassNovyy", "Dec": "KaubPassDecyy"})):
        prof = pd.read_csv(HERE / "scenarios" / f"{year}.csv"); days = {}
        for _, rr in prof.iterrows():
            w0 = pd.Timestamp(rr.week_start)
            for k in range(7):
                days[w0 + pd.Timedelta(days=k)] = lfn(float(rr.kaub_cm))
        d = pd.Series(days); mm = d.groupby(d.index.strftime("%b")).mean()
        for mo, mac in macs.items():
            put(mac, pct(100 * mm.get(mo, np.nan)), f"{year}: % of the normal tonnage past Kaub, monthly mean of the loading table")
        if year == 2026:
            put("KaubMinWeek", pct(100 * d.min()), "% of the normal tonnage in the worst week (the floor below 5 cm)")
    # ---- the Kaub throughput at the baseline, by cargo class (2 Nov 2026): from the t=0 flow file of the reference run or of the
    # link-level run (weekly tons x 52, the largest feature of the reach, as anchor_rhine_capacities.py reads it); the first
    # version's runs were packed without the flow file, so its figure stays as a constant
    kf = next((RUNS / r_ / "transport_edges_with_flows_0.geojson" for r_ in (B, f"2026_{tag}_full")
               if (RUNS / r_ / "transport_edges_with_flows_0.geojson").exists()), None)
    if kf is not None:
        import json as _json
        kb = {}
        for f_ in _json.load(open(kf, encoding="utf-8"))["features"]:
            pp = f_["properties"]
            if str(pp.get("name") or "") == "rhine_mainz_koblenz" and float(pp.get("flow_total_tons") or 0.0) > kb.get("flow_total_tons", -1.0):
                kb = {k: float(pp.get(k) or 0.0) for k in ("flow_total_tons", "tons_container", "tons_dry_bulk", "tons_liquid_bulk")}
        kmt = {k: v * 52 / 1e6 for k, v in kb.items()}
        put("KaubMt", pct(kmt["flow_total_tons"]), f"model throughput of the Kaub reach at the baseline, Mt/yr (dry bulk {kmt['tons_dry_bulk']:.1f}, liquid {kmt['tons_liquid_bulk']:.1f}, containers {kmt['tons_container']:.1f}; {kf.parent.name})")
        put("KaubContMt", r1(kmt["tons_container"]), "containers through Kaub at the baseline, Mt/yr (CCNR: roughly 10)")
        put("KaubDryMt", r1(kmt["tons_dry_bulk"]), "dry bulk through Kaub at the baseline, Mt/yr"); put("KaubLiquidMt", r1(kmt["tons_liquid_bulk"]), "liquid bulk")
        put("KaubContShare", pct(100 * kmt["tons_container"] / kmt["flow_total_tons"]), "% of the Kaub tonnage that is containers at the baseline (CCNR: about a sixth)")
    else:
        put("KaubMt", "54", "model throughput of the Kaub reach at the baseline, Mt/yr (dry bulk 22, liquid 31, containers nil; constant: no flow file in the packed runs)")
    put("DestatisNovyy", "34", "Destatis: German inland-waterway tonnage, November 2018, % year on year")
    gt = {}
    for line in (RUNS / f"{B}.log").read_text(encoding="utf-8", errors="replace").splitlines():
        mt = re.search(r"Capacity gate t=(\d+):.*cut ([\d,]+) t, re-sent ([\d,]+) t", line)
        if mt:
            gt[int(mt.group(1))] = (float(mt.group(2).replace(",", "")), float(mt.group(3).replace(",", "")))
    put("ResentShare", pct(100 * sum(v[1] for k, v in gt.items() if 12 <= k <= 19) / sum(v[0] for k, v in gt.items() if 12 <= k <= 19)), "% of the tonnage cut at the gates that finds another route, trough weeks 12-19")
    # ---- prices: the Kaub-crossing links in the worst week, and the economy-wide share
    vo = pd.read_csv(RUNS / f"2026_{tag}_full" / "validation_outputs.csv"); vo = vo[vo.group == "kaub"]
    worst = vo[vo.cargo_type == "liquid_bulk"].set_index("time_step").price_ratio_p50.idxmax()
    vw = vo[vo.time_step == worst].set_index("cargo_type")
    put("WorstWeek", str(int(worst)), "the week of the highest Kaub-crossing price rise")
    put("PriceMedianDry", pct(100 * (vw.loc["dry_bulk", "price_ratio_p50"] - 1)), f"% delivered-price rise of the Kaub-crossing dry bulk still delivered, median, week {worst}")
    put("PriceMedianWet", pct(100 * (vw.loc["liquid_bulk", "price_ratio_p50"] - 1)))
    put("PriceNinthDry", pct(100 * (vw.loc["dry_bulk", "price_ratio_p90"] - 1))); put("PriceNinthWet", pct(100 * (vw.loc["liquid_bulk", "price_ratio_p90"] - 1)))
    put("PriceMax", r1(max(vw.loc["dry_bulk", "price_ratio_max"], vw.loc["liquid_bulk", "price_ratio_max"])), "maximum, as a multiple")
    v0 = vo[vo.time_step == 0].set_index("cargo_type")
    put("KaubDeliveredDry", pct(100 * vw.loc["dry_bulk", "delivered_tons"] / v0.loc["dry_bulk", "delivered_tons"]), "% of the baseline tonnage the Kaub-crossing dry-bulk shippers deliver in the worst week")
    put("KaubDeliveredWet", pct(100 * vw.loc["liquid_bulk", "delivered_tons"] / v0.loc["liquid_bulk", "delivered_tons"]))
    pc = pd.read_csv(RUNS / f"2026_{tag}_full" / "price_by_cargo.csv")
    econ = pc.groupby("time_step").apply(lambda g: (g.delivered_value * g.share_value_above_1pct).sum() / g.delivered_value.sum(), include_groups=False)
    tw = int(econ.idxmax()); pw = pc[pc.time_step == tw].set_index("cargo_type")
    put("PriceShareEconomy", r1(100 * econ.max()), f"% of ALL value delivered on the network in week {tw} paying > 1 % above its baseline price")
    put("PriceShareLiquid", r1(100 * pw.loc["liquid_bulk", "share_value_above_1pct"])); put("PriceShareDry", r1(100 * pw.loc["dry_bulk", "share_value_above_1pct"])); put("PriceShareContainer", r1(100 * pw.loc["container", "share_value_above_1pct"]))
    put("ContainerValueShare", pct(100 * pw.loc["container", "delivered_value"] / pw.delivered_value.sum()), "% of the delivered value that is containers")
    # ---- the revision sensitivities (jobs_20261007_rev.txt)
    if len(r):
        def rel(run, base=B):
            return pct(100 * (r.loc[run, "DEU_%quarter"] / m.loc[base, "DEU_%quarter"] - 1))
        for mac, run in (("RevRailFifty", f"2026_{REV}_rail50"), ("RevRailHundredForty", f"2026_{REV}_rail140"), ("RevHeadTen", f"2026_{REV}_head10"), ("RevHeadTwentyFive", f"2026_{REV}_head25"),
                         ("RevRestFifteen", f"2026_{REV}_rest15"), ("RevRestSixty", f"2026_{REV}_rest60"), ("RevFloorLow", f"2026_{REV}_floor04"), ("RevFloorHigh", f"2026_{REV}_floor16"),
                         ("RevDeepLocal", f"2026_{REV}_deeplocal"), ("RevFleetWide", f"2026_{REV}_fleetwide"), ("RevDfuel", f"2026_{REV}_dfuel0"), ("RevServ", f"2026_{REV}_serv45"),
                         ("RevQLow", f"2026_{REV}_q25"), ("RevQHigh", f"2026_{REV}_q75")):
            put(mac, r2(r.loc[run, "DEU_%quarter"]), f"{run}: {rel(run)} % against the base"); put(mac + "Rel", rel(run).replace("-", "$-$"))
            put(mac + "Abs", rel(run).lstrip("-"), "the same change without its sign")
        for mac, run in (("RevRailFiftyyy", f"2018_{REV}_rail50"), ("RevRailHundredFortyyy", f"2018_{REV}_rail140")):
            put(mac, r2(r.loc[run, "DEU_%quarter"]), f"{run}: {rel(run, B18)} % against the 2018 base"); put(mac + "Rel", rel(run, B18).replace("-", "$-$"))
            put(mac + "Abs", rel(run, B18).lstrip("-"), "the same change without its sign")
        for mac, run in (("RevRailFiftyInt", f"2018_{REV}_rail50"), ("RevRailHundredFortyInt", f"2018_{REV}_rail140")):
            put(mac, r1(model_path(RUNS / run, 2018)["ind_integrated_pct_months"]), "2018 industrial integral, percent-months")
        put("RevDeepLocalRemoves", pct(100 * (1 - r.loc[f"2026_{REV}_deeplocal", "DEU_cum_mUSD"] / b.DEU_cum_mUSD)), "% of the loss removed by the fairway on the Kaub reach alone")
        put("RevFleetWideRemoves", pct(100 * (1 - r.loc[f"2026_{REV}_fleetwide", "DEU_cum_mUSD"] / b.DEU_cum_mUSD)))
        rsum = pd.read_csv(RUNS / f"2026_{REV}_rail140" / "routing_summary.csv"); rsum5 = pd.read_csv(RUNS / f"2026_{REV}_rail50" / "routing_summary.csv")
        put("ReliefBnFifty", r1(rsum5[rsum5.cargo_type.isin(["dry_bulk", "liquid_bulk"])].relief_usd.sum() / 1e3), "bn USD delivered through the 50 kt ceiling over the run")
        put("ReliefBnHundredForty", r1(rsum[rsum.cargo_type.isin(["dry_bulk", "liquid_bulk"])].relief_usd.sum() / 1e3))
    # ---- constants: the price-with-closures representation (S6) and the model size
    for mac, val, com in (("DEUlossQP", "0.54", "2026 (vintage of 10 Sep), stocks x2, priced river with closures"), ("DEUlossQyyP", "0.32", "2018, stocks x2"),
                          ("PriceIntP", "2.0", "2018 industrial shortfall, stocks x2, earlier rule"), ("PriceIntRawP", "5.0", "stocks x1, earlier rule"), ("LevFleetP", "95", "fleet lever in the price representation"),
                          ("NFirms", "12{,}719", ""), ("NLinks", "1.38", "million commercial links"), ("NRoutable", "786{,}608", ""), ("NEdges", "10{,}139", ""), ("NNodes", "6{,}767", ""), ("NRegions", "28", ""), ("NSectors", "50", "")):
        put(mac, val, com)
    # ---- the review of 8 October 2026 (review_checks_20261008.py): forecast vintage, lever ordering, index bridge, anatomy
    sep = AD / "compare_runs_batch_jobs_20260930_main.csv"
    if sep.exists():
        ts = table(sep)
        if "2026_s30_base" in ts.index:
            put("ForecastSepQ", r2(ts.loc["2026_s30_base", "DEU_%quarter"]), "the forecast as first issued on 30 Sep 2026, on the loading table of September (2026_s30_base)")
    av = pd.DataFrame({k: [100 * (1 - p.loc[f"2026_{tag}_seed{s}_{k}", "DEU_cum_mUSD"] / p.loc[f"2026_{tag}_seed{s}_base", "DEU_cum_mUSD"]) for s in range(1, 11)] for k in LEVERS})
    single = av[["stock7", "deep20", "fleet", "stock7t"]]
    put("StocksBeatFairwayDraws", WORDS[int((av.stock7 > av.deep20).sum())], "of the ten further draws in which stocks +7 days avoids more than the fairway")
    put("FleetLastDraws", WORDS[int((single.idxmin(axis=1) == "fleet").sum())], "draws in which the fleet avoids the least of the four single levers")
    put("FleetBeatsTargetedDraws", WORDS[int((av.fleet > av.stock7t).sum())], "draws in which the fleet avoids more than the targeted stocks")
    put("TargetedBehindBothDraws", WORDS[int(((av.stock7t < av.stock7) & (av.stock7t < av.deep20)).sum())], "draws in which the targeted week is behind both stocks and fairway")
    put("PeakBase", r2(b["DEU_peak_%week"]), "peak week of the reference run, % of a week"); put("PeakFleet", r2(m.loc[f"2026_{tag}_fleet", "DEU_peak_%week"]), "peak week with the low-water fleet")
    from review_checks_20261008 import industrial_series, monthly as monthly_days, FIRST as FIRST_DAY, MONTHS18, MONTHS26
    for yr, run, months, suf in ((2018, B18, MONTHS18, "yy"), (2026, B, MONTHS26, "")):
        pw, _, sw = industrial_series(RUNS / run)
        mp_, ms_ = monthly_days(pw, FIRST_DAY[yr], months), monthly_days(sw, FIRST_DAY[yr], months)
        put(f"IndProdInt{suf}", r1(sum(mp_.values())), f"{yr} industrial integral, production-weighted (percent-months)")
        put(f"IndVAInt{suf}", r1(sum(ms_.values())), f"{yr} industrial integral, sector shortfall rates weighted by sector value added (the production-index convention)")
        put(f"IndVAMaxDiff{suf}", r1(max(abs(mp_[k] - ms_[k]) for k in months)), "largest monthly difference between the two aggregations (points)")
    grp_of = lambda s: "A" if s[0] == "A" else ("I" if s[0] in "BCDE" else ("F" if s[0] == "F" else "S"))
    put("RatioBase", r1(tot / ind.loss.sum()), "German loss over its industrial part, reference run")
    for mac, run in (("Serv", f"2026_{REV}_serv45"), ("Dfuel", f"2026_{REV}_dfuel0"), ("RailFifty", f"2026_{REV}_rail50"), ("RailHundredForty", f"2026_{REV}_rail140")):
        if (RUNS / run / "firm_data.csv").exists():
            fx = firm_losses(RUNS / run); dx = fx[(fx.region == "DEU") & (fx.time_step >= 1)]; tx = dx.loss.sum()
            gx = dx.groupby(dx.sector.map(grp_of)).loss.sum() / tx * 100
            put(f"ShareServices{mac}", pct(gx.get("S", 0)), f"{run}: G-T share of the German gross loss"); put(f"ShareIndustry{mac}", pct(gx.get("I", 0)), "B-E")
            put(f"ShareConstruction{mac}", pct(gx.get("F", 0)), "F"); put(f"ShareUtilities{mac}", pct(100 * dx[dx.sector.isin(["D", "E"])].loss.sum() / tx), "D+E")
            put(f"Ratio{mac}", r1(100 / max(gx.get("I", 0), 1e-9)), "German loss over its industrial part")
    for mac, run in (("Fifty", f"2026_{REV}_rail50"), ("HundredForty", f"2026_{REV}_rail140")):
        rs = RUNS / run / "routing_summary.csv"
        if rs.exists():
            g = pd.read_csv(rs).groupby("cargo_type").relief_usd.sum()
            put(f"ReliefLiquidShare{mac}", pct(100 * g.get("liquid_bulk", 0) / g.sum()), f"{run}: % of the relief value that is liquid bulk")
    # ---- signed calendar-quarter measures (review of 12 Oct, E4): shortfall minus the catch-up above baseline, by quarter
    from matched_estimand_2018 import _series, FIRST as FIRST_DAY2
    fdq = pd.read_csv(RUNS / B / "firm_data.csv", usecols=["time_step", "firm", "region", "sector", "production"])
    b0q = fdq[fdq.time_step == 0].set_index("firm")["production"]
    fdq = fdq[(fdq.region == "DEU") & (fdq.time_step >= 1)].copy(); fdq["base"] = fdq.firm.map(b0q)
    from va_shares import add_va_share as _avs
    _avs(fdq, RUNS / B)
    wk_signed = ((fdq.base - fdq.production) * fdq.va_share).groupby(fdq.time_step).sum()
    wk_gross = ((fdq.base - fdq.production).clip(lower=0) * fdq.va_share).groupby(fdq.time_step).sum()
    wk_base = (fdq.base * fdq.va_share).groupby(fdq.time_step).sum()
    def by_quarter(w):
        days = {}
        for t, v in w.items():
            w0 = FIRST_DAY2[2026] + pd.Timedelta(days=7 * (int(t) - 1))
            for k in range(7):
                days[w0 + pd.Timedelta(days=k)] = float(v)
        d = pd.Series(days); qtr = d.index.to_period("Q").astype(str)
        return {q: float(d[qtr == q].mean()) for q in ("2026Q3", "2026Q4")}
    sq, gq = by_quarter(100 * wk_signed / wk_base), by_quarter(100 * wk_gross / wk_base)
    put("SignedQthree", r2(sq["2026Q3"]).replace("-", "$-$"), "signed German value-added change, Q3 2026, % of the quarter's baseline (shortfall minus catch-up)")
    put("SignedQfour", r2(sq["2026Q4"]).replace("-", "$-$"), "Q4 2026"); put("GrossQthree", r2(gq["2026Q3"]), "gross (clipped) loss, Q3 2026"); put("GrossQfour", r2(gq["2026Q4"]), "Q4 2026")
    s_idx = _series(RUNS / B)[0]
    iq = by_quarter(s_idx)
    put("IndSignedQthree", r2(iq["2026Q3"]).replace("-", "$-$"), "industry, index measure, signed, Q3 2026"); put("IndSignedQfour", r2(iq["2026Q4"]).replace("-", "$-$"), "Q4 2026")
    # ---- the surcharge bill (20 Oct 2026): extra payments on deliveries, pass-through included, from the link-level run
    lfp = RUNS / f"2026_{tag}_full" / "link_flows_disrupted.csv.gz"
    if lfp.exists():
        lf2 = pd.read_csv(lfp, usecols=["time_step", "buyer_region", "realized_delivery", "price_ratio"]); lf2 = lf2[lf2.time_step >= 1]
        ex = lf2.realized_delivery * (lf2.price_ratio - 1.0)
        put("SurchargeBillBn", r1(ex.sum() / 1e3), "bn USD of extra payments on deliveries over the 2026 run, all 28 economies, pass-through included")
        put("SurchargeBillDEUBn", r1(ex[lf2.buyer_region == "DEU"].sum() / 1e3), "of which on deliveries to German buyers")
    # ---- the corridor firms (20 Oct 2026): German firms within 50 km of the Rhine chain producing below 99 % of baseline at the peak
    ftab = RUNS / B / "firm_table.geojson"; etab = RUNS / B / "transport_edges.geojson"
    if ftab.exists() and etab.exists():
        import json
        import geopandas as gpd
        from shapely.geometry import Point, shape
        from shapely.ops import unary_union
        ej = json.load(open(etab, encoding="utf-8"))
        rhine = unary_union([shape(f["geometry"]) for f in ej["features"] if str(f["properties"].get("name", "")).startswith("rhine_")])
        fj = json.load(open(ftab, encoding="utf-8"))
        ft = gpd.GeoDataFrame([{"id": f["properties"]["id"], "region": f["properties"]["region"], "geometry": Point(f["properties"]["long"], f["properties"]["lat"])} for f in fj["features"]], crs="EPSG:4326")
        rh = gpd.GeoSeries([rhine], crs="EPSG:4326").to_crs(3035).iloc[0]
        ft = ft.to_crs(3035); ft["dist_km"] = ft.geometry.distance(rh) / 1e3
        near = set(ft[(ft.region == "DEU") & (ft.dist_km <= 50)].id)
        pk = int(b.DEU_peak_week)
        fpk = pd.read_csv(RUNS / B / "firm_data.csv", usecols=["time_step", "firm", "region", "production"])
        b0p = fpk[fpk.time_step == 0].set_index("firm").production
        for wk, suf in ((pk, ""), (7, "Aug")):  # week 7 = 3-9 August, the week the DIHK survey of 29 July-4 August closed
            at = fpk[(fpk.time_step == wk) & (fpk.region == "DEU")].copy(); at["base"] = at.firm.map(b0p)
            at = at[at.base > 0]
            sel = at[at.firm.isin(near)]
            put("CorridorFirmsBelowRhine" + suf, r1(100 * (sel.production < 0.99 * sel.base).mean()), f"% of the {len(sel)} German firms within 50 km of the Rhine producing below 99 % of baseline in week {wk}")
            put("CorridorStopRhine" + suf, r1(100 * (sel.production < 0.5 * sel.base).mean()), f"% of them producing below half of baseline in week {wk}")
            put("CorridorFirmsBelowDEU" + suf, r1(100 * (at.production < 0.99 * at.base).mean()), f"the same share over all German firms, week {wk}")
    # ---- the no-rail runs (jobs_20261020_norail.txt): no bulk may use rail as an alternative
    nr = AD / f"compare_runs_batch_jobs_{norail_date}_norail.csv"
    if nr.exists():
        tn = table(nr)
        for mac, run, base in (("RevNoRail", f"2026_{REV}_norail", B), ("RevNoRailyy", f"2018_{REV}_norail", B18)):
            if run in tn.index:
                relv = pct(100 * (tn.loc[run, "DEU_%quarter"] / m.loc[base, "DEU_%quarter"] - 1))
                put(mac, r2(tn.loc[run, "DEU_%quarter"]), f"{run}: {relv} % against the base"); put(mac + "Rel", relv.replace("-", "$-$")); put(mac + "Abs", relv.lstrip("-"))
    # ---- the batch of 9 October 2026 (jobs_20261009_cross.txt): the levers under the 50 kt rail ceiling, the waves at 15 days
    cx = AD / f"compare_runs_batch_jobs_{cross_date}_cross.csv"
    if cx.exists() and len(r):
        c = table(cx)
        b50 = r.loc[f"2026_{REV}_rail50", "DEU_cum_mUSD"]
        b0c = m.loc[B, "DEU_cum_mUSD"]; rail_alone = b0c - b50
        put("RailAloneBn", r1(rail_alone / 1e3), "bn USD avoided by the 50 kt rail relief alone")
        for mac, k in (("CrossStockRail", "stock7"), ("CrossDeepRail", "deep20"), ("CrossFleetRail", "fleet"), ("CrossStockTRail", "stock7t")):
            run = f"2026_{REV}_rail50_{k}"
            if run in c.index:
                put(mac, pct(100 * (1 - c.loc[run, "DEU_cum_mUSD"] / b50)), f"{run}: % of the rail-50 base's loss avoided")
                alone = b0c - m.loc[f"2026_{tag}_{k}", "DEU_cum_mUSD"]; both = b0c - c.loc[run, "DEU_cum_mUSD"]
                put(mac.replace("Rail", "AloneBn"), r1(alone / 1e3), f"bn USD avoided by the lever alone"); put(mac.replace("Rail", "OnRailBn"), r1((both - rail_alone) / 1e3), "bn USD avoided by the lever on top of the rail relief")
                put(mac.replace("Rail", "Overlap"), pct(100 * (1 - both / (alone + rail_alone))), "% by which the two together avoid less than the sum of their separate benefits")
        if all(k in c.index for k in (f"{WV9}_A_rest15", f"{WV9}_B_rest15", f"{WV9}_AB_gap2_rest15", f"{WV9}_AB_gap4_rest15")):
            a15, b15 = c.loc[f"{WV9}_A_rest15", "DEU_%quarter"], c.loc[f"{WV9}_B_rest15", "DEU_%quarter"]
            s15 = r.loc[f"2026_{REV}_rest15", "DEU_%quarter"]
            put("WaveARest", r2(a15), "wave A alone at a 15-day refill time, % of a quarter"); put("WaveBRest", r2(b15)); put("WaveSumRest", r2(a15 + b15))
            put("WaveSeqRest", r2(s15), f"the sequence without a gap at 15 days (2026_{REV}_rest15)")
            put("WaveInterRest", pct(100 * (s15 / (a15 + b15) - 1)).replace("-", "$-$"), "% more than the sum, 15 days, no gap")
            put("WaveGapTwoRest", pct(100 * (c.loc[f"{WV9}_AB_gap2_rest15", "DEU_%quarter"] / (a15 + b15) - 1)).replace("-", "$-$"), "gap of 2 weeks, 15 days")
            put("WaveGapFourRest", pct(100 * (c.loc[f"{WV9}_AB_gap4_rest15", "DEU_%quarter"] / (a15 + b15) - 1)).replace("-", "$-$"), "gap of 4 weeks, 15 days")
            put("WaveGapTwoRestAbs", pct(100 * (1 - c.loc[f"{WV9}_AB_gap2_rest15", "DEU_%quarter"] / (a15 + b15))), "% less than the sum, gap of 2 weeks, 15 days")
            put("WaveGapFourRestAbs", pct(100 * (1 - c.loc[f"{WV9}_AB_gap4_rest15", "DEU_%quarter"] / (a15 + b15))), "gap of 4 weeks")
    # ---- the pending literals of the gate (5 Nov 2026): model outputs that the manuscript wrote as numbers, now
    # computed here (review/pending_fixes_20261105.yaml, applied by review/patch_pending_20261105.py). Each section runs
    # in its own function, so its variables cannot overwrite the ones above, and _put_once refuses to redefine a macro
    # with another value.
    def _put_once(name, val, comment=""):
        if name in M and M[name][0] != val:
            raise ValueError(f"\\{name} defined twice: {M[name][0]!r} and {val!r}")
        put(name, val, comment)
    # -- main text (residuals on the Rhine, peak weeks, France, catch-up, forecast misses ...)
    def _pending_main():
        put = _put_once
        # inside 'if kf is not None:' of the river block, after put("KaubContShare", ...); _json is imported there.
        # The Rhine residuals of the baseline (SI S2): reach tonnage as flow_score.py computes it (km-weighted mean over
        # the edges of each rhine_* reach, weekly tons x 52) against the normal-year counts of rhine_capacities.csv.
        # This block also writes LowerRhineGapMax, DeltaGapMin, DeltaGapMax, UpperRhineShareMin, UpperRhineShareMax.
        acc = {}
        for f_ in _json.load(open(kf, encoding="utf-8"))["features"]:
            pp = f_["properties"]; nm = str(pp.get("name") or "")
            if nm.startswith("rhine_"):
                km_ = float(pp.get("km") or 0.0); a_ = acc.setdefault(nm, [0.0, 0.0])
                a_[0] += float(pp.get("flow_total_tons") or 0.0) * 52 / 1e6 * km_; a_[1] += km_
        cnt = pd.read_csv(HERE / "scenarios" / "rhine_capacities.csv").set_index("name").mt_per_year
        rat = {k: (v[0] / v[1]) / cnt[k] for k, v in acc.items() if v[1] > 0 and k in cnt.index}
        LOWER = ["rhine_duisburg", "rhine_duisburg_wesel", "rhine_wesel", "rhine_wesel_emmerich", "rhine_emmerich", "rhine_emmerich_nijmegen", "rhine_nijmegen", "rhine_nijmegen_tiel"]
        DELTA = ["rhine_tiel", "rhine_tiel_dordrecht", "rhine_dordrecht", "rhine_dordrecht_rotterdam"]
        UPPER = ["rhine_basel", "rhine_strasbourg", "rhine_karlsruhe"]
        put("LowerRhineGapMin", pct(100 * (1 - max(rat[k] for k in LOWER))), "% below the normal-year count, the Lower Rhine from Duisburg to Nijmegen (km-weighted reach tonnage, as flow_score.py; rhine_capacities.csv), smallest gap")
        put("LowerRhineGapMax", pct(100 * (1 - min(rat[k] for k in LOWER))), "largest gap (Duisburg)")
        put("DeltaGapMin", pct(100 * (1 - max(rat[k] for k in DELTA))), "% below the count, the Waal from Tiel and the delta to Rotterdam, smallest gap")
        put("DeltaGapMax", pct(100 * (1 - min(rat[k] for k in DELTA))), "largest gap")
        put("UpperRhineShareMin", pct(100 * min(rat[k] for k in UPPER)), "% of the count at Basel, Strasbourg and Karlsruhe (the cross-sections of SI S2), smallest")
        put("UpperRhineShareMax", pct(100 * max(rat[k] for k in UPPER)), "largest")
        # written by the LowerRhineGapMin block
        # written by the LowerRhineGapMin block (proposal of 'The Lower Rhine north of Duisburg ...')
        # after put("PricedIntC", ...) (the priced river block); 'priced' and 'rt' (record(2018, 1)) are defined above.
        from matched_estimand_2018 import FIRST as FIRST_PK
        fpr = firm_losses(RUNS / priced[1.0]); wpr = fpr[(fpr.region == "DEU") & (fpr.time_step >= 1)].groupby("time_step").loss.sum()
        on = int(wpr[wpr > 0.01 * wpr.max()].index.min()); d_on = FIRST_PK[2018] + pd.Timedelta(days=7 * (on - 1))
        put("PricedOnsetDate", f"{d_on.day}~{d_on.strftime('%B')}", f"first week of German loss in the priced river with closures ({priced[1.0]}, week {on}, > 1 % of its worst week)")
        rec0 = pd.Timestamp(next(mo for mo, v in zip(rt.month, rt.central) if mo in EVENT_MONTHS[2018] and v > 0) + "-01")
        put("PricedOnsetLagMonths", r1((d_on - rec0).days / 30.44), f"months from the first day of the benchmark's first month of shortfall ({rec0:%B}) to that week")
        # written by the PricedOnsetDate block
        # after the ensemble lines of the 2026 baseline (put("EnsMeanBn", ...)); also writes DEUpeakDate and EnsMedian.
        from matched_estimand_2018 import FIRST as FIRST_PK

        def wk_date(y, t):
            d_ = FIRST_PK[y] + pd.Timedelta(days=7 * (int(t) - 1))
            return f"{d_.day}~{d_.strftime('%B')}"

        pk26 = [int(p.loc[f"2026_{tag}_seed{s}_base", "DEU_peak_week"]) for s in range(1, 11)] + [int(b.DEU_peak_week)]
        put("DEUpeakDate", wk_date(2026, b.DEU_peak_week), f"Monday of the peak week of the reference run (week {int(b.DEU_peak_week)}; week 1 = 22 June 2026)")
        put("PeakDateFirst", wk_date(2026, min(pk26)), f"earliest peak week over the eleven networks (week {min(pk26)})")
        put("PeakDateLast", wk_date(2026, max(pk26)), f"latest peak week over the eleven networks (week {max(pk26)})")
        put("EnsMedian", r2(np.median(e26)), "2026, median of the eleven networks, % of a quarter")
        # written by the PeakDateFirst block
        # written by the PeakDateFirst block (proposal of 'with the peak in the week of 5 or 12 October ...')
        # after put("WaveInterEight", ...)
        put("WaveInterEightAbs", f"{abs(100 * (gaps[8] - A - Bw) / (A + Bw)):.1f}", "the same, without its sign")
        # in the river block, after the loading-table loop (after put("KaubMinWeek", ...), outside the loop)
        put("SurchargeMax", r1(1 / dt.load_factor.min()), "the largest freight multiplier of the model: the inverse of the lowest loading share (below 5 cm)")
        # after put("FRAlossBn", ...); fd = firm_losses(RUNS / B) holds every region. Also writes FRARoadShare, ESPlossBn, AUTlossBn, NLDlossBn.
        fr = fd[(fd.region == "FRA") & (fd.time_step >= 1)]; frt = fr.loss.sum()
        put("FRAFoodShare", pct(100 * fr[fr.sector.isin(["A01", "C10T12"])].loss.sum() / frt), "% of France's gross loss in crops (A01) and the food industry (C10-12)")
        put("FRARoadShare", pct(100 * fr[fr.sector == "H49"].loss.sum() / frt), "% of France's gross loss in land transport (H49)")
        for cc in ("ESP", "AUT", "NLD"):
            put(f"{cc}lossBn", r1(fd[fd.region == cc].loss.sum() / 1e3), f"bn USD, {cc} gross value-added loss, reference network (firm_data)")
        # written by the FRAFoodShare block
        # written by the FRAFoodShare block (proposal of 'three-fifths in its food chain ...')
        # after put("EnsMeanyy", ...) of the 2018 block (e18 defined on the line before)
        put("EnsMedianyy", r2(np.median(e18)), "2018, median of the eleven networks, % of a quarter")
        # anywhere in main(), e.g. after the Rhine residuals; the same file si_tables.ports_table reads
        pf = pd.read_csv(RUNS / "r6_h01_feeder3" / "flow_score" / "ports.csv")
        pf = pf[pf.model_mt.notna() & pf.eurostat_mt.notna() & (pf.scored.astype(str).str.lower() == "true")]
        nwin = int(((pf.model_mt / pf.eurostat_mt - 1).abs() <= 0.30).sum())
        put("PortsWithinThirty", WORDS.get(nwin, str(nwin)), f"of the {len(pf)} largest seaports with a connector (the forty of Eurostat 2023 less two) within 30 % of the Eurostat tonnage (r6_h01_feeder3/flow_score/ports.csv, the source of Table S-ports)")
        # in the river block after the loading-table loop (dt and lfn defined there); also writes DailyTurnedAwayyy
        for year, suf in ((2026, ""), (2018, "yy")):
            prof_ = pd.read_csv(HERE / "scenarios" / f"{year}.csv")
            dly = pd.read_csv(HERE / "scenarios" / f"kaub_daily_{year}.csv", parse_dates=["date"]).set_index("date").kaub_cm
            aw = ad_ = 0.0; nw = 0
            for _, rw in prof_.iterrows():
                days_ = [pd.Timestamp(rw.week_start) + pd.Timedelta(days=k) for k in range(7)]
                if all(x in dly.index for x in days_):
                    aw += 1 - lfn(float(rw.kaub_cm)); ad_ += 1 - np.mean([lfn(float(dly[x])) for x in days_]); nw += 1
            put(f"DailyTurnedAway{suf}", r1(abs(100 * (ad_ / aw - 1))), f"{year}: % change of the tonnage turned away at Kaub (sum of 1 - loading share over the {nw} weeks with seven daily gauges) when the share is computed day by day and averaged over the week instead of read at the weekly mean gauge; signed {100 * (ad_ / aw - 1):+.2f}")
        # written by the DailyTurnedAway block
        # after put("ShareUtilities", ...) of the 2026 baseline (de = German firm losses with base, production, vs); also writes CatchUpLastM, CatchUpDecay, CatchUpTailShare
        gd = de[de.sector.str[:1].isin(list("ABCF")) & (de.time_step >= 1)]
        catch = ((gd.production - gd.base) * gd.vs).clip(lower=0).groupby(gd.time_step).sum()
        t0c, t1c = len(pd.read_csv(HERE / "scenarios" / "2026.csv")) + 1, int(catch.index.max())   # first recovery week, last week of the run
        dec = (catch[t1c] / catch[t0c]) ** (1 / (t1c - t0c))
        put("CatchUpFirstM", f"{catch[t0c]:.0f}", f"mUSD a week, German catch-up production of goods and construction (A-C, F, above baseline, value-added weights), week {t0c}")
        put("CatchUpLastM", r1(catch[t1c]), f"the same, week {t1c}")
        put("CatchUpDecay", pct(100 * (1 - dec)), f"% by which it falls a week, geometric mean of weeks {t0c}-{t1c}")
        put("CatchUpTailShare", r1(100 * catch[t1c] * dec / (1 - dec) / b.DEU_net_deferrable_mUSD), "% of the backlog left at the end (DEU_net_deferrable_mUSD) that the geometric tail after the last week would add")
        # written by the CatchUpFirstM block
        # written by the CatchUpFirstM block (proposal of 'decays from 300 million USD ...')
        # after the signed-quarter block (the same computation as si_tables.prospective_sectors_table); also writes ProspRefOct, ProspChemAug, ProspChemOct
        from matched_estimand_2018 import monthly_from_weekly, FIRST as FIRST_MS
        for code, nm in (("C19", "Ref"), ("C20", "Chem")):
            sub = de[(de.sector == code) & (de.time_step >= 1)]
            s_ = 100 * (sub.base - sub.production).groupby(sub.time_step).sum() / sub.base.groupby(sub.time_step).sum()
            mo_, _ = monthly_from_weekly(s_, FIRST_MS[2026], ["2026-08", "2026-10"])
            put(f"Prosp{nm}Aug", pct(mo_["2026-08"]), f"{code}: German production shortfall, August 2026, % (Table S-prospective sectors, {mo_['2026-08']:.1f})")
            put(f"Prosp{nm}Oct", pct(mo_["2026-10"]), f"{code}: October 2026 ({mo_['2026-10']:.1f})")
        # written by the ProspRefAug block
    _pending_main()
    # -- SI S1-S2 (the baseline against the freight statistics, from flow_score)
    def _pending_si_a():
        put = _put_once
        # ---- the baseline against the freight statistics (SI S2, 5 Nov 2026): the tables of onboarding/scripts/flow_score.py on
        # the batch's baseline. The batch runs were not scored; r6_h01_feeder3, the round-6 base the batch was built on, has the
        # same t=0 flows to the ton (transport_edges_with_flows_0 and transport_nodes identical; flow_score rerun on a copy of
        # 2026_r6_bycargo_base byte-identical, 5 Nov 2026), so its folder stands in until the base run carries a flow_score/.
        FS = RUNS / B / "flow_score"
        if not FS.exists():
            FS = RUNS / {"s07": "2026_s07_flows"}.get(tag, "r6_h01_feeder3") / "flow_score"
        fsum = pd.read_csv(FS / "summary.csv").set_index("block").loc["OVERALL"]
        put("FlowScore", r2(fsum.mean_abs_log10), f"flow score of the baseline: weighted mean |log10| model/observation over {int(fsum.n_items)} items ({FS.parent.name})")
        put("FlowScoreFirst", r2(pd.read_csv(RUNS / "2026_s07_flows" / "flow_score" / "summary.csv").set_index("block").loc["OVERALL", "mean_abs_log10"]), "the same for the first version's baseline (2026_s07_flows)")
        # inland modal split by country, % of tonne-km road / rail / waterway (Eurostat 2023 in the comment; the text quotes it)
        fcm = pd.read_csv(FS / "country_modal_split.csv").set_index("geo")
        for cc in ("DE", "NL", "BE", "FR", "AT", "CH", "PL", "IT"):
            for col, md in (("ROAD", "Road"), ("RAIL", "Rail"), ("IWW", "Iww")):
                put(f"Modal{cc}{md}", pct(fcm.loc[cc, f"model_{col}"]), f"{cc}: % of inland tkm by {md.lower()} at the baseline ({fcm.loc[cc, f'model_{col}']:.1f}; Eurostat 2023 {fcm.loc[cc, f'target_{col}']:.1f})")
        put("NLTkmBn", pct(fcm.loc["NL", "model_bn_tkm"]), "bn tkm of inland transport on the Dutch edges at the baseline (Eurostat 2023: 110.8)")
        # Germany by cargo class on the German edges, % of tonne-km road / rail / waterway: general cargo = NST manufacturing
        # (containers), dry bulk = agriculture + mining, liquid bulk = oil and gas; the NST target aggregated the same way
        fns = pd.read_csv(FS / "nst_modal_split.csv")
        fns = fns[(fns.cc == "DE") & (fns.category != "TOTAL")].copy()
        fns["cls"] = fns.category.map({"manufacturing": "General", "agriculture": "Dry", "mining": "Dry", "oil_and_gas": "Liquid"})
        for cls, g_ in fns.groupby("cls"):
            tk = g_.groupby("mode")[["model_bn_tkm", "target_bn_tkm"]].sum(); sh = 100 * tk / tk.sum()
            for md, nm in (("roads", "Road"), ("railways", "Rail"), ("waterways", "Iww")):
                put(f"Cargo{cls}{nm}", pct(sh.loc[md, "model_bn_tkm"]), f"Germany, {cls.lower()} cargo: % of tkm by {nm.lower()} on the German edges ({sh.loc[md, 'model_bn_tkm']:.1f}; NST target {sh.loc[md, 'target_bn_tkm']:.1f})")
        # the Rhine sections, Mt/yr (km-weighted mean of the reach), against the CCNR counts and estimates (in the comment);
        # one decimal below 5 Mt, as the text writes Basel
        frh = pd.read_csv(FS / "rhine.csv").set_index("name")
        for nm in ("rhine_basel", "rhine_strasbourg", "rhine_karlsruhe", "rhine_mannheim_mainz", "rhine_koblenz", "rhine_bonn", "rhine_koeln",
                   "rhine_duisburg", "rhine_emmerich", "rhine_tiel", "rhine_dordrecht_rotterdam"):
            v = frh.loc[nm, "model_mt"]
            put("Rhine" + "".join(w.capitalize() for w in nm.split("_")[1:]) + "Mt", r1(v) if v < 5 else pct(v), f"{nm}: Mt/yr at the baseline (CCNR {frh.loc[nm, 'normal_mt']:g})")
        fsel = frh.index[list(frh.index).index("rhine_mannheim"): list(frh.index).index("rhine_emmerich") + 1]
        put("RhineDevMaxPct", pct(100 * (frh.loc[fsel, "model_mt"] / frh.loc[fsel, "normal_mt"] - 1).abs().max()), "largest % gap between model and CCNR from Mannheim to Emmerich")
        # the German waterway sections (Destatis 46321-0014, 2023, in the comment): the busiest section of each waterway, Mt/yr;
        # integers, the Wesel-Datteln canal with one decimal as the text writes it
        fbs = pd.read_csv(FS / "basins.csv"); fbs = fbs[fbs.cc == "DE"].set_index("waterway")
        put("DEWaterTkmBn", r1(fbs.loc["ALL", "bn_tkm"]), f"bn tkm on the German waterways at the baseline (Eurostat 2023: {fbs.loc['ALL', 'bn_tkm_per_year']:g})")
        for ww, mac in (("Rhine", "BasinRhineMt"), ("Main", "BasinMainMt"), ("Neckar", "BasinNeckarMt"), ("Danube", "BasinDanubeMt"), ("Rhein-Herne-Kanal", "BasinRheinHerneMt"),
                        ("Elbe", "BasinElbeMt"), ("Moselle", "BasinMoselleMt"), ("Wesel-Datteln-Kanal", "BasinWeselDattelnMt"), ("Dortmund-Ems-Kanal", "BasinDortmundEmsMt"),
                        ("Mittellandkanal", "BasinMittellandMt"), ("Weser", "BasinWeserMt"), ("Kuestenkanal-Hunte", "BasinKuestenMt")):
            v = fbs.loc[ww, "max_mt"]
            put(mac, r1(v) if ww == "Wesel-Datteln-Kanal" else pct(v), f"{ww}: Mt/yr on its busiest section at the baseline (Destatis 2023 {fbs.loc[ww, 'mt_per_year']:g})")
        fnl = pd.read_csv(FS / "basins.csv").set_index(["waterway", "cc"])
        put("NLWaterTkmBn", r1(fnl.loc[("ALL", "NL"), "bn_tkm"]), f"bn tkm on the Dutch waterways at the baseline (Eurostat 2023: {fnl.loc[('ALL', 'NL'), 'bn_tkm_per_year']:g})")
        # the seaports (the rows of Table tab:ports, si_tables.ports_table): Mt/yr through the port's connectors (Eurostat 2023 gross
        # weight handled in the comment; the text quotes it)
        fpt = pd.read_csv(FS / "ports.csv").set_index("rep_mar")
        for code, mac in (("NL_0NLRTM", "Rotterdam"), ("BE_0BE003", "Antwerp"), ("DE_1DEHAM", "Hamburg"), ("NL_0NLAMS", "Amsterdam"), ("PL_0PLGDN", "Gdansk"),
                          ("ES_2ESALG", "Algeciras"), ("FR_1FR001", "Havre"), ("FR_2FRMRS", "Marseille"), ("ES_2ESVLC", "Valencia"), ("ES_2ESBCN", "Barcelona"),
                          ("IT_0ITTRS", "Trieste"), ("IT_0ITGOA", "Genoa"), ("EL_0GRPIR", "Piraeus"), ("PT_0PTSIE", "Sines"), ("DE_1DEBRV", "Bremerhaven"),
                          ("NL_0NLZSP", "Zeeland"), ("IT_0ITGIT", "GioiaTauro"), ("FR_1FRDKK", "Dunkirk"), ("SE_2SEGOT", "Gothenburg"), ("ES_1ESBIO", "Bilbao"),
                          ("BE_0BEGNE", "Ghent"), ("DE_1DEWVN", "Wilhelmshaven"), ("FR_1FRNTE", "Nantes"), ("IE_0IEDUB", "Dublin"), ("BG_0BGBOJ", "Burgas"),
                          ("PL_0PLSZZ", "Szczecin"), ("NO_0NOOSL", "Oslo"), ("ES_2ESAGP", "Malaga")):
            put(f"Port{mac}Mt", pct(fpt.loc[code, "model_mt"]), f"{mac} ({code}): Mt/yr at the baseline ({fpt.loc[code, 'model_mt']:.1f}; Eurostat 2023 {fpt.loc[code, 'eurostat_mt']:.1f})")
        lagoon = ["IT_0ITVCE", "IT_0ITCHI", "IT_0ITMNF", "IT_0ITPNG"]
        put("PortLagoonMt", pct(fpt.loc[lagoon, "model_mt"].sum()), f"Venice, Chioggia, Monfalcone and Porto Nogaro together, Mt/yr (Eurostat 2023 {fpt.loc[lagoon, 'eurostat_mt'].sum():.1f})")
        fsec = fpt[(fpt.scored.astype(str).str.lower() != "true") & fpt.n_terminals.notna()]
        put("SecPortsN", str(len(fsec)), "gazetteer ports outside the top forty with a connector (flow_score secondary ports)")
        put("SecPortsMt", pct(fsec.model_mt.sum()), "Mt/yr landed at them at the baseline"); put("SecPortsObsMt", pct(fsec.eurostat_mt.sum()), "Eurostat 2023 gross weight handled at them, Mt")
        fss = pd.read_csv(FS / "short_sea.csv", index_col=0)
        put("DeepSeaShare", pct(fss.loc["EU27_2020", "model_dss_pct_from_gateways"]), f"% of the maritime tonnage on deep-sea lanes at the baseline (Eurostat EU27 2023: {fss.loc['EU27_2020', 'eurostat_dss_pct']:g})")
        # the gate at Kaub in the trough of 2018 (S2, 5 Nov 2026): kt a week at the loading factor of the trough weeks (Kaub 29-32 cm
        # in late October and November 2018: the table's 0.30 at 30 cm) for the capacity of the CCNR file, a single capacity anchored
        # on the model's total and the per-class capacities (rhine_mainz_koblenz; anchor_rhine_capacities.py)
        if (HERE / "scenarios" / f"rhine_capacities_anchored_{tag}.csv").exists():
            f18 = lfn(30.0)
            kc = {k: pd.read_csv(HERE / "scenarios" / f"rhine_capacities{k}.csv").set_index("name").loc["rhine_mainz_koblenz"] for k in ("", "_anchored_r6", f"_anchored_{tag}")}
            put("GateFleetKt", f"{10 * round(kc[''].tons_per_day * 7 * f18 / 1e4):.0f}", f"kt/week the fleet carries past Kaub at factor {f18:.2f} (CCNR file {kc[''].tons_per_day:,.0f} t/day; to the ten)")
            put("GateSingleKt", pct(kc["_anchored_r6"].tons_per_day * 7 * f18 / 1e3), f"kt/week a single capacity anchored on the total lets through ({kc['_anchored_r6'].tons_per_day:,.0f} t/day)")
            kb_ = kc[f"_anchored_{tag}"]
            put("GateBulkKt", pct((kb_.tons_per_day_dry_bulk + kb_.tons_per_day_liquid_bulk) * 7 * f18 / 1e3), f"kt/week the per-class capacities allow the bulk ({kb_.tons_per_day_dry_bulk:,.0f} dry + {kb_.tons_per_day_liquid_bulk:,.0f} liquid t/day)")
    _pending_si_a()
    # -- SI S3-S10 (gate log, daily loading, channels, supplier weights, stationarity, Kaub links ...)
    def _pending_si_b():
        put = _put_once
        # ==== the pending literals of the gate, SI S3-S8 (5 Nov 2026) ====
        # ---- [A] the gate at Kaub week by week (S3 allocation, S4 flat profile and conservation; Table si_gate): cut, re-sent
        # and withheld at the gates of the Rhine chain from the run's log, in the profile weeks and the recovery weeks
        def gate_log(run_):
            g_ = {}
            for line_ in (RUNS / f"{run_}.log").read_text(encoding="utf-8", errors="replace").splitlines():
                mt_ = re.search(r"Capacity gate t=(\d+):.*cut ([\d,]+) t, re-sent ([\d,]+) t, blocked ([\d,]+) t", line_)
                if mt_ and float(mt_.group(2).replace(",", "")) > 0:
                    g_[int(mt_.group(1))] = tuple(float(mt_.group(i).replace(",", "")) for i in (2, 3, 4))
            return g_
        n_prof26 = len(pd.read_csv(HERE / "scenarios" / "2026.csv"))
        gl26 = gate_log(B)
        w_prof = sorted(t_ for t_ in gl26 if t_ <= n_prof26); w_rec = sorted(t_ for t_ in gl26 if t_ > n_prof26)
        w_ep = [t_ for t_ in w_prof if 7 <= t_ <= 9 or 12 <= t_ <= 19]          # the August episode and the autumn trough
        rs26 = {t_: 100 * v_[1] / v_[0] for t_, v_ in gl26.items()}             # re-sent share of the week's cut, %
        for suf_, ws_ in (("", w_prof), ("First", w_prof[:3]), ("Last", w_prof[-3:]), ("Ep", w_ep)):
            put(f"GateResent{suf_}Min", pct(min(rs26[t_] for t_ in ws_)), f"% of the week's cut at the Rhine gates that is re-sent, lowest over weeks {ws_} ({B} log)")
            put(f"GateResent{suf_}Max", pct(max(rs26[t_] for t_ in ws_)), "highest")
        gsum = lambda gl_, ws_, i: sum(gl_[t_][i] for t_ in ws_) / 1e6
        put("GateResentRec", pct(100 * gsum(gl26, w_rec, 1) / gsum(gl26, w_rec, 0)), "% of the cut re-sent in the recovery weeks")
        put("GateWeeks", str(len(gl26)), "run weeks in which the gates cut (profile + recovery)"); put("GateRecWeeks", str(len(w_rec)), "recovery weeks in which the gates cut")
        put("GateCutMt", r1(gsum(gl26, gl26, 0)), "Mt cut at the gates over the season (Table si_gate caption)"); put("GateResentMt", r1(gsum(gl26, gl26, 1)), "Mt re-sent")
        put("GateHeldMt", r1(gsum(gl26, gl26, 2)), "Mt withheld over the season"); put("GateHeldProfMt", r1(gsum(gl26, w_prof, 2)), "Mt withheld in the profile weeks")
        put("GateHeldRecMt", r1(gsum(gl26, w_rec, 2)), "Mt withheld in the recovery weeks")
        glf = gate_log(f"{wv}_flat")
        put("FlatCutMt", r1(gsum(glf, glf, 0)), f"Mt cut at the gates under the flat profile ({wv}_flat log)"); put("FlatResentMt", r1(gsum(glf, glf, 1)), "Mt re-sent")
        put("FlatHeldMt", r1(gsum(glf, glf, 2)), "Mt withheld under the flat profile")
        put("FlatHeldDiff", pct(100 * (1 - gsum(glf, glf, 2) / gsum(gl26, gl26, 2))), "% by which the flat profile withholds less tonnage than the season")
        # ---- [B] day-by-day loading against weekly means (S3 loading table): tonnage turned away in week-equivalents over the
        # profile weeks covered by the daily gauge files, on the current loading table (lfn)
        dd_ = {}
        for yr_ in (2018, 2026):
            pf_ = pd.read_csv(HERE / "scenarios" / f"{yr_}.csv")
            dy_ = pd.read_csv(HERE / "scenarios" / f"kaub_daily_{yr_}.csv", parse_dates=["date"]).set_index("date").kaub_cm
            wk_ = da_ = 0.0
            for _, rr_ in pf_.iterrows():
                days_ = [pd.Timestamp(rr_.week_start) + pd.Timedelta(days=k_) for k_ in range(7)]
                if all(d_ in dy_.index for d_ in days_):
                    wk_ += 1 - lfn(float(rr_.kaub_cm)); da_ += float(np.mean([1 - lfn(float(dy_.loc[d_])) for d_ in days_]))
            dd_[yr_] = 100 * (da_ / wk_ - 1)
        put("DailyLoadingDiff", r1(max(abs(v_) for v_ in dd_.values())), f"% change of the tonnage turned away when the loading share is taken day by day, largest of the two years (2018 {dd_[2018]:+.2f}, 2026 {dd_[2026]:+.2f}; weeks with daily gauges)")
        # ---- [C] the two channels at the routing level (S4; Table si_channels): routing_summary.csv totals over the 2026 run
        for suf_, run_ in (("", B), ("Gate", f"2026_{tag}_gateonly"), ("Sur", f"2026_{tag}_surchargeonly")):
            rsm_ = pd.read_csv(RUNS / run_ / "routing_summary.csv")
            bk_ = rsm_[rsm_.cargo_type.isin(["dry_bulk", "liquid_bulk"])]; ct_ = rsm_[rsm_.cargo_type == "container"]
            put(f"ChanBulkAlt{suf_}Bn", r1(bk_.alternative_usd.sum() / 1e3), f"{run_}: bn USD of bulk that leaves its normal route for an alternative")
            put(f"ChanContAlt{suf_}Bn", r1(ct_.alternative_usd.sum() / 1e3), f"{run_}: bn USD of containers that leave their normal route")
            if suf_ != "Sur":
                put(f"ChanBulkHeld{suf_}Bn", r1(bk_.capacity_blocked_usd.sum() / 1e3), f"{run_}: bn USD of bulk withheld by the capacity gate")
        # ---- [D] supplier weights of the Kaub-served German buyers through the season (S4; revision_diagnostics.supplier_weights)
        # on the link-level run: buyers with a supplier pair cut at Kaub in the August episode (weeks 7-9), share of their offered
        # deliveries from those pairs at the start (t=0), the end of the first wave (t=10), the second episode (t=19), after (t=40)
        kw_ = lf[lf.buyer_region == "DEU"].copy()
        kkey_ = ["seller_region", "seller_sector", "buyer_region", "buyer_sector"]
        kdep_ = kw_[kw_.time_step.isin([7, 8, 9]) & (kw_.capacity_blocked > 0)].groupby(kkey_).size().index
        kw_["kaub"] = kw_.set_index(kkey_).index.isin(kdep_)
        kbuy_ = kw_[kw_.kaub].groupby(["buyer_region", "buyer_sector"]).size().index
        kw_ = kw_[kw_.set_index(["buyer_region", "buyer_sector"]).index.isin(kbuy_)]
        put("SupWeightBuyers", str(len(kbuy_)), f"German buyer region-sectors with a supplier pair cut at Kaub in weeks 7-9 (2026_{tag}_full)")
        for suf_, st_ in (("Start", 0), ("WaveEnd", 10), ("Second", 19), ("After", 40)):
            x_ = kw_[kw_.time_step == st_]
            put(f"SupWeight{suf_}", r1(100 * x_[x_.kaub].delivery_offered.sum() / x_.delivery_offered.sum()), f"% of their offered deliveries from those pairs, week {st_}")
        # ---- [E] stationarity of the undisturbed baseline (S4, S10; stationarity_check.py): six weeks at 250 cm, constraint off.
        # STAT_RUN is the check run of 5 Oct 2026 (inputs before the per-class calibration) until it is rerun on the r6 inputs
        STAT_RUN = RUNS / "stationarity6w"
        sd_ = pd.read_csv(STAT_RUN / "firm_data.csv", usecols=["time_step", "firm", "production", "production_target", "input_stock"])
        s0_ = sd_[sd_.time_step == 0].set_index("firm"); mat_ = s0_.index[s0_.production > 0.01]          # > 10,000 USD a week
        tmax_ = int(sd_.time_step.max()); sT_ = sd_[sd_.time_step == tmax_].set_index("firm")
        tdev_ = max(abs(sd_[sd_.time_step == t_].production.sum() / s0_.production.sum() - 1) for t_ in range(1, tmax_ + 1))
        gap_ = (sT_.production_target - sT_.production) / sT_.production_target.clip(lower=1e-12)
        ism_ = sT_.index.isin(mat_)
        rel_ = sT_.production / s0_.production
        stk_ = (sT_.input_stock / s0_.input_stock).replace([np.inf, -np.inf], np.nan)
        put("StatFirms", f"{len(mat_):,}".replace(",", "{,}"), f"firms producing more than 10,000 USD a week at t=0 ({STAT_RUN.name})")
        put("StatTotalDevPpm", r2(1e6 * tdev_), "largest deviation of total production from its initial value over the run, parts per million")
        put("StatBelow", WORDS[int((gap_[ism_] > 1e-6).sum())], f"of those firms, below their production target in week {tmax_}")
        put("StatBelowPct", pct(100 * (1 - rel_[ism_].min())), "% below its initial production, the lowest of those firms")
        put("StatStockLow", f"{100 * (stk_[ism_].min() - 1):+.1f}".replace("-", "$-$"), f"% deviation of the input inventories from t=0, lowest, week {tmax_}")
        put("StatStockHigh", f"{100 * (stk_[ism_].max() - 1):+.1f}".replace("-", "$-$"), "highest")
        put("StatDrift", str(int((gap_[~ism_] > 1e-6).sum())), f"smaller agents below target in week {tmax_} (the drift at the numerical floor)")
        # ---- [F] the bounded substitution by rail (S4, S8; Table si_rail_weeks): the cut bulk that found an eligible rail route in
        # the profile weeks of the two 50 kt runs, rounded to 10 kt
        offr_ = []
        for yr_, run_ in ((2026, f"2026_{REV}_rail50"), (2018, f"2018_{REV}_rail50")):
            np_ = len(pd.read_csv(HERE / "scenarios" / f"{yr_}.csv"))
            for line_ in (RUNS / f"{run_}.log").read_text(encoding="utf-8", errors="replace").splitlines():
                mt_ = re.search(r"Capacity gate t=(\d+):.*relief ([\d,]+) t of ([\d,]+) t offered", line_)
                if mt_ and int(mt_.group(1)) <= np_ and float(mt_.group(3).replace(",", "")) > 0:
                    offr_.append(float(mt_.group(3).replace(",", "")) / 1e3)
        put("RailOfferedMin", f"{10 * np.floor(min(offr_) / 10 + 0.5):.0f}", f"kt a week: the least cut bulk offered to rail in a profile week of the 50 kt runs ({min(offr_):.1f}, rounded to 10 kt)")
        put("RailOfferedMax", f"{10 * np.floor(max(offr_) / 10 + 0.5):.0f}", f"the most ({max(offr_):.1f})")
        # ---- [G] what crosses Kaub (S5): the Kaub-crossing links of the link-level run at the baseline (v0: validation_outputs.csv,
        # group kaub, t=0), the services' missing refined fuel and the French buyers (link_flows_disrupted.csv.gz)
        put("KaubLinks", f"{int(v0.n.sum()):,}".replace(",", "{,}"), f"commercial links whose baseline route crosses Kaub (2026_{tag}_full)")
        put("KaubWeekMt", r2(v0.delivered_tons.sum() / 1e6), "Mt a week that they carry at the baseline")
        fu_ = dl[dl.buyer_sector.isin(["H49", "H52", "D", "H50"]) & (dl.seller_sector == "C19")]
        fs_ = (fu_.base_realized - fu_.realized_delivery).clip(lower=0)
        put("FuelWithheldShare", pct(100 * np.minimum(fu_.withheld_by_transport, fs_).sum() / fs_.sum()),
            "% of the refined fuel that German hauliers, logistics, power and shipping miss which is withheld at the river (withheld capped at the week's shortfall; uncapped as TransportWithheldShare: "
            f"{100 * fu_.withheld_by_transport.sum() / fs_.sum():.0f})")
        fr_ = lf[(lf.buyer_region == "FRA") & (lf.time_step >= 1)]
        put("FRAFarmWithheldBn", r1(fr_[(fr_.seller_sector == "A01") & (fr_.buyer_sector == "C10T12")].withheld_by_transport.sum() / 1e3), "bn USD of farm products to the French food industry withheld at the river")
        frd_ = fr_[fr_.seller_region == "DEU"]
        put("FRAfromDEUBn", r1((frd_.base_realized - frd_.realized_delivery).clip(lower=0).sum() / 1e3), "bn USD of deliveries from German suppliers that French buyers miss")
        # ---- [H] the priced river with closures (S6, S9): December and the November at twice the inventories
        prC_ = model_path(RUNS / priced[2.0], 2018)
        put("PricedNovC", r1(prC_["ind_Nov"]), f"priced river with closures, x2, November ({priced[2.0]})")
        put("PricedDec", r1(pr["ind_Dec"]), f"priced river with closures, x1, December ({priced[1.0]})")
        put("PricedDecShare", pct(100 * pr["ind_Dec"] / pr["ind_Nov"]), "December over November of the priced river, x1, %")
        # ---- [I] run counts of the batch (S7; Table si_runs): the rows of the compare tables of the job lists
        alt_date = None if old_naming else "20261103"
        nr_ = {}
        for suf_, f_ in (("Main", f"compare_runs_batch_jobs_{date_list}_main.csv"), ("Paired", f"compare_runs_batch_jobs_{date_list}_paired.csv"),
                         ("Rev", f"compare_runs_batch_jobs_{date_list}_rev.csv"), ("Ladder", f"compare_runs_batch_jobs_{date_list}_ladder.csv"),
                         ("Cross", f"compare_runs_batch_jobs_{cross_date}_cross.csv"), ("NoRail", f"compare_runs_batch_jobs_{norail_date}_norail.csv"),
                         ("Alt", f"compare_runs_batch_jobs_{alt_date}_altriver.csv")):
            if (AD / f_).exists():
                nr_[suf_] = len(table(AD / f_)); put(f"NRuns{suf_}", str(nr_[suf_]), f"runs of {f_}")
        put("NRuns", str(sum(nr_.values())), "runs of Table si_runs")
    _pending_si_b()
    lines = [f"% Key numbers of the paper, generated by studies/rhine2026/make_numbers.py from the batch of {date_list} (run names {tag}): the river as a",
             "% quantity constraint with the voyage surcharge, stocks at their evidence values, crude and gas by pipeline, construction a",
             "% non-storable input, the loading table rebuilt on its ledger (6 Oct 2026); the 2026 profile of 30 Sep (observations to 29 Sep,",
             "% the BfG outlook of 28 Sep, 23 weeks). Do not edit by hand: rerun the script after a batch.",
             "% \\finalbatch{} in the text marks the 2026 numbers of the forecast that the revision after the event replaces."]
    for k, (v, c) in M.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}" + (f"  % {c}" if c else ""))
    (overleaf / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"numbers.tex written: {len(M)} macros; ladder source: {src}")
    for k in ("DEUlossQ", "IndQ", "EnsMean", "DEUlossQyy", "ModelInt", "ModelIntEnsMean", "DrawsInBand", "LevStock", "LevDeep", "LevFleet", "LevStockT", "WaveInterShare", "FlatQ", "RevRailFifty", "RevRailHundredForty", "PriceShareEconomy", "ShareServices"):
        if k in M:
            print(f"  {k} = {M[k][0]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="s07")
    ap.add_argument("--lists", default="20261007", help="date of the job lists (compare_runs_batch_jobs_<date>_main.csv ...)")
    ap.add_argument("--overleaf", default=str(OVERLEAF))
    a = ap.parse_args()
    main(a.tag, Path(a.overleaf), a.lists)
