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
    m = table(AD / f"compare_runs_batch_jobs_{date_list}_main.csv")
    p = table(AD / f"compare_runs_batch_jobs_{date_list}_paired.csv")
    rv = AD / f"compare_runs_batch_jobs_{date_list}_rev.csv"
    r = table(rv) if rv.exists() else pd.DataFrame()
    t = pd.concat([m, p] + ([r] if len(r) else []))
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
    pr = model_path(RUNS / "2018_baseline", 2018)
    put("PricedInt", r1(pr["ind_integrated_pct_months"]), "priced river with closures, x1, on the earlier table (S6)"); put("PricedNov", r1(pr["ind_Nov"]))
    # ---- structural sensitivities
    for mac, run in (("TableLowInt", f"2018_{tag}_tablelow"), ("TableHighInt", f"2018_{tag}_tablehigh"), ("SupTwoInt", f"2018_{tag}_sup2")):
        put(mac, r1(model_path(RUNS / run, 2018)["ind_integrated_pct_months"]), run)
    for mac, run in (("TableLowQ", f"2026_{tag}_tablelow"), ("TableHighQ", f"2026_{tag}_tablehigh"), ("TableLowQyy", f"2018_{tag}_tablelow"), ("TableHighQyy", f"2018_{tag}_tablehigh"),
                     ("SupTwoQ", f"2026_{tag}_sup2"), ("SupTwoQyy", f"2018_{tag}_sup2"), ("GateOnlyQ", f"2026_{tag}_gateonly"), ("SurchargeOnlyQ", f"2026_{tag}_surchargeonly")):
        put(mac, r2(m.loc[run, "DEU_%quarter"]), run)
    put("NoPoolQ", r1(m.loc[f"2026_{tag}_nopool", "DEU_%quarter"])); put("NoPoolQyy", r1(m.loc[f"2018_{tag}_nopool", "DEU_%quarter"]))
    # ---- waves
    wv = tag.replace("s", "wave")
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
    put("KaubMt", "54", "model throughput of the Kaub reach at the baseline, Mt/yr (dry bulk 22, liquid 31, containers nil)")
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
        for mac, run in (("RevRailFifty", "2026_rev_rail50"), ("RevRailHundredForty", "2026_rev_rail140"), ("RevHeadTen", "2026_rev_head10"), ("RevHeadTwentyFive", "2026_rev_head25"),
                         ("RevRestFifteen", "2026_rev_rest15"), ("RevRestSixty", "2026_rev_rest60"), ("RevFloorLow", "2026_rev_floor04"), ("RevFloorHigh", "2026_rev_floor16"),
                         ("RevDeepLocal", "2026_rev_deeplocal"), ("RevFleetWide", "2026_rev_fleetwide"), ("RevDfuel", "2026_rev_dfuel0"), ("RevServ", "2026_rev_serv45"),
                         ("RevQLow", "2026_rev_q25"), ("RevQHigh", "2026_rev_q75")):
            put(mac, r2(r.loc[run, "DEU_%quarter"]), f"{run}: {rel(run)} % against the base"); put(mac + "Rel", rel(run).replace("-", "$-$"))
        for mac, run in (("RevRailFiftyyy", "2018_rev_rail50"), ("RevRailHundredFortyyy", "2018_rev_rail140")):
            put(mac, r2(r.loc[run, "DEU_%quarter"]), f"{run}: {rel(run, B18)} % against the 2018 base"); put(mac + "Rel", rel(run, B18).replace("-", "$-$"))
        for mac, run in (("RevRailFiftyInt", "2018_rev_rail50"), ("RevRailHundredFortyInt", "2018_rev_rail140")):
            put(mac, r1(model_path(RUNS / run, 2018)["ind_integrated_pct_months"]), "2018 industrial integral, percent-months")
        put("RevDeepLocalRemoves", pct(100 * (1 - r.loc["2026_rev_deeplocal", "DEU_cum_mUSD"] / b.DEU_cum_mUSD)), "% of the loss removed by the fairway on the Kaub reach alone")
        put("RevFleetWideRemoves", pct(100 * (1 - r.loc["2026_rev_fleetwide", "DEU_cum_mUSD"] / b.DEU_cum_mUSD)))
        rsum = pd.read_csv(RUNS / "2026_rev_rail140" / "routing_summary.csv"); rsum5 = pd.read_csv(RUNS / "2026_rev_rail50" / "routing_summary.csv")
        put("ReliefBnFifty", r1(rsum5[rsum5.cargo_type.isin(["dry_bulk", "liquid_bulk"])].relief_usd.sum() / 1e3), "bn USD delivered through the 50 kt ceiling over the run")
        put("ReliefBnHundredForty", r1(rsum[rsum.cargo_type.isin(["dry_bulk", "liquid_bulk"])].relief_usd.sum() / 1e3))
    # ---- constants: the price-with-closures representation (S6) and the model size
    for mac, val, com in (("DEUlossQP", "0.54", "2026 (vintage of 10 Sep), stocks x2, priced river with closures"), ("DEUlossQyyP", "0.32", "2018, stocks x2"),
                          ("PriceIntP", "2.0", "2018 industrial shortfall, stocks x2, earlier rule"), ("PriceIntRawP", "5.0", "stocks x1, earlier rule"), ("LevFleetP", "95", "fleet lever in the price representation"),
                          ("NFirms", "12{,}719", ""), ("NLinks", "1.38", "million commercial links"), ("NRoutable", "786{,}608", ""), ("NEdges", "10{,}139", ""), ("NNodes", "6{,}767", ""), ("NRegions", "28", ""), ("NSectors", "50", "")):
        put(mac, val, com)
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
