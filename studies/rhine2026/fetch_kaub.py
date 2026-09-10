"""Refresh the 2026 Kaub profile of the Rhine study from PEGELONLINE (REST API, raw 15-min W).

Daily means in legal time (Europe/Berlin), the convention of scenarios/kaub_daily_2026.csv; a day
with fewer than 90 of the 96 values is flagged PARTIAL. The weekly rows of scenarios/2026.csv are
rebuilt: a fully observed week -> status 'observed'; a week with some observed days ->
'observed+forecast' (observed days + --fill-cm for the missing days, default = persistence of the
last observed day); a later week -> the BfG 6-week ENS median when --forecast-6week is given
(status 'forecast', the 5-95 % band in the note), otherwise its previous assumption row. With
--forecast-6week the profile is continued to the last forecast week, and --extend appends
assumption weeks after that. The closure classes per week under the driver's default floors are
printed for the old and the new profile, so a schedule change is visible.

    python studies/rhine2026/fetch_kaub.py --dry-run              # show what would change
    python studies/rhine2026/fetch_kaub.py --fill-cm 26 --fill-note "ELWIS 4-day forecast of 10 Sep, 24-28 cm" \
        --forecast-6week studies/rhine2026/scenarios/bfg_6week_kaub_20260907.csv \
        --extend "2026-10-19=80,2026-10-26=95"                    # write scenarios/2026.csv + kaub_daily_2026.csv
    python studies/rhine2026/fetch_kaub.py --out-dir <dir>        # write the two files elsewhere (staging)

The REST API serves at most the last 30 days; older days come from the long-term download already
in kaub_daily_2026.csv (identical values: cross-checked 29 Aug - 4 Sep 2026). The 6-week CSV is the
BfG 'QuansBox' file (https://vorhersage.bafg.de/6-Wochen-Vorhersage/Rhein-Kaub_6Wochen_Wasserstand_QuansBox.csv).
"""
import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_rhine import DEFAULT_CARGO_TYPES, DEFAULT_CLOSURE_FLOORS, closed_classes, parse_closure_floors  # noqa: E402

SCEN = HERE / "scenarios"
API = "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/KAUB/W/measurements.json?start=P{days}D"
SOURCE = ("PEGELONLINE REST API measurements.json (ungepruefte Rohdaten, DL-DE->Zero-2.0), daily mean of "
          "15-min W values in legal time, https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/KAUB/W")
FULL_DAY = 90
DEFAULT_EXTEND_NOTE = ("assumption: recovery continuing at the trend of the BfG ENS median (about +20 cm a week); "
                       "replace with observations")


def fetch_daily(days: int) -> pd.DataFrame:
    with urllib.request.urlopen(API.format(days=days), timeout=90) as r:
        data = json.load(r)
    tz = ZoneInfo("Europe/Berlin")
    by_day = defaultdict(list)
    last = {}
    for m in data:
        ts = datetime.fromisoformat(m["timestamp"]).astimezone(tz)
        d = ts.date().isoformat()
        by_day[d].append(float(m["value"]))
        last[d] = ts.strftime("%H:%M")
    rows = [{"date": d, "kaub_cm": round(sum(v) / len(v), 1), "min": min(v), "max": max(v), "n": len(v), "last": last[d]}
            for d, v in sorted(by_day.items())]
    return pd.DataFrame(rows)


def merge_daily(existing: pd.DataFrame, fetched: pd.DataFrame, fetched_on: str) -> pd.DataFrame:
    """Existing full days are kept (the long-term download is the reference); partial days are
    replaced by the fetched value; new days are appended with the REST source note."""
    ex = existing.set_index("date")
    out = ex.copy()
    for _, r in fetched.iterrows():
        partial = r["n"] < FULL_DAY
        note = f"{SOURCE}, fetched {fetched_on}"
        if partial:
            note += f" -- PARTIAL DAY (n={int(r['n'])} of 96 values, to {r['last']})"
        keep_existing = r["date"] in ex.index and "PARTIAL" not in str(ex.loc[r["date"], "source"])
        if keep_existing:
            diff = abs(float(ex.loc[r["date"], "kaub_cm"]) - float(r["kaub_cm"]))
            if diff > 0.15:
                print(f"   note: {r['date']} long-term download {ex.loc[r['date'], 'kaub_cm']} vs REST {r['kaub_cm']} (kept the file)")
            continue
        out.loc[r["date"], "kaub_cm"] = float(r["kaub_cm"])
        out.loc[r["date"], "source"] = note
    return out.sort_index().reset_index()


def parse_forecast_6week(path) -> tuple[str, dict[str, dict]]:
    """BfG QuansBox CSV -> (issue date, {week_start iso: {p5, p25, median, p75, p95}})."""
    issued, rows = "?", {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            m = re.search(r"Vorhersage vom (\d{4}-\d{2}-\d{2})", line)
            if m:
                issued = m.group(1)
            continue
        parts = line.split(";")
        if len(parts) < 6 or " - " not in parts[0]:
            continue
        start = datetime.strptime(parts[0].split(" - ")[0].strip(), "%d.%m.%Y").date().isoformat()
        rows[start] = {"p5": float(parts[1]), "p25": float(parts[2]), "median": float(parts[3]),
                       "p75": float(parts[4]), "p95": float(parts[5])}
    return issued, rows


def parse_extend(raw: str | None) -> list[tuple[str, float]]:
    if not raw:
        return []
    out = []
    for item in raw.split(","):
        d, cm = item.split("=")
        out.append((pd.Timestamp(d.strip()).date().isoformat(), float(cm)))
    return sorted(out)


def rebuild_profile(profile: pd.DataFrame, daily: pd.DataFrame, fill_cm: float | None, fill_note: str | None = None,
                    forecast: tuple[str, dict] | None = None, extend: list[tuple[str, float]] | None = None,
                    extend_note: str = DEFAULT_EXTEND_NOTE) -> pd.DataFrame:
    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["partial"] = d["source"].str.contains("PARTIAL")
    d = d.set_index("date")
    last_full = d[~d["partial"]]["kaub_cm"].iloc[-1]
    fill = last_full if fill_cm is None else fill_cm
    fill_src = fill_note or ("persistence of the last observed day" if fill_cm is None else "--fill-cm")
    issued, fc = forecast if forecast else ("?", {})

    def forecast_row(ws: str, prev: str) -> dict:
        q = fc[ws]
        return {"week_start": ws, "kaub_cm": q["median"], "status": "forecast",
                "note": f"BfG 6-week forecast issued {issued}: ENS median {q['median']:.0f} cm "
                        f"(5-95 % {q['p5']:.0f} to {q['p95']:.0f}, 25-75 % {q['p25']:.0f} to {q['p75']:.0f}); {prev}"}

    out = []
    for _, r in profile.iterrows():
        w0 = pd.Timestamp(r["week_start"])
        v = d[(d.index >= w0) & (d.index < w0 + pd.Timedelta(days=7))]
        prev = f"previous value {r['kaub_cm']} ({r['status']})"
        if len(v) == 7 and not v["partial"].any():
            out.append({"week_start": r["week_start"], "kaub_cm": round(float(v["kaub_cm"].mean()), 1), "status": "observed",
                        "note": f"PEGELONLINE daily means (raw 15-min data, DL-DE->Zero-2.0), weekly mean; daily min "
                                f"{v['kaub_cm'].min():.0f}, max {v['kaub_cm'].max():.0f}; {prev}"})
        elif len(v) > 0:
            obs = ", ".join(f"{x:.0f}" for x in v["kaub_cm"])
            partial_tag = ", last day partial" if bool(v["partial"].iloc[-1]) else ""
            est = (float(v["kaub_cm"].sum()) + fill * (7 - len(v))) / 7
            out.append({"week_start": r["week_start"], "kaub_cm": round(est, 1), "status": "observed+forecast",
                        "note": f"{v.index[0].date()} to {v.index[-1].date()} observed daily means ({obs}{partial_tag}), "
                                f"remaining {7 - len(v)} days at {fill:.0f} cm ({fill_src}); {prev}"})
        elif r["week_start"] in fc:
            out.append(forecast_row(r["week_start"], prev))
        else:
            out.append({"week_start": r["week_start"], "kaub_cm": r["kaub_cm"], "status": r["status"], "note": r["note"]})

    def next_week(ws: str) -> str:
        return (pd.Timestamp(ws) + pd.Timedelta(days=7)).date().isoformat()

    while next_week(out[-1]["week_start"]) in fc:                      # continue to the last forecast week
        ws = next_week(out[-1]["week_start"])
        out.append(forecast_row(ws, "new week"))
    for ws, cm in extend or []:                                         # then the tail assumption
        if ws <= out[-1]["week_start"]:
            raise SystemExit(f"--extend week {ws} is not after the last profile week {out[-1]['week_start']}")
        if ws != next_week(out[-1]["week_start"]):
            raise SystemExit(f"--extend week {ws} does not follow {out[-1]['week_start']} (weeks must be consecutive Mondays)")
        out.append({"week_start": ws, "kaub_cm": cm, "status": "assumption", "note": extend_note})
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="days of 15-min data to fetch (API maximum 30)")
    ap.add_argument("--fill-cm", type=float, default=None, help="gauge assumed for the missing days of the open week")
    ap.add_argument("--fill-note", default=None, help="source of --fill-cm, written into the week's note")
    ap.add_argument("--forecast-6week", default=None, help="BfG 6-week QuansBox CSV: ENS medians for the weeks without observations")
    ap.add_argument("--extend", default=None, help="assumption weeks after the forecast, 'YYYY-MM-DD=cm,...' (consecutive Mondays)")
    ap.add_argument("--extend-note", default=DEFAULT_EXTEND_NOTE)
    ap.add_argument("--profile", default="2026")
    ap.add_argument("--out-dir", default=str(SCEN), help="where to write kaub_daily_<profile>.csv and <profile>.csv")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    fetched_on = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    fetched = fetch_daily(args.days)
    print(f"fetched {len(fetched)} days ({fetched['date'].iloc[0]} to {fetched['date'].iloc[-1]}, {fetched_on}):")
    print(fetched.tail(10).to_string(index=False))

    daily_path = SCEN / f"kaub_daily_{args.profile}.csv"
    existing = pd.read_csv(daily_path)
    daily = merge_daily(existing, fetched, fetched_on)
    profile = pd.read_csv(SCEN / f"{args.profile}.csv")
    forecast = parse_forecast_6week(args.forecast_6week) if args.forecast_6week else None
    if forecast:
        print(f"6-week forecast issued {forecast[0]}: weeks {', '.join(forecast[1])}")
    new = rebuild_profile(profile, daily, args.fill_cm, args.fill_note, forecast, parse_extend(args.extend), args.extend_note)

    floors = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    cts = list(DEFAULT_CARGO_TYPES)
    old = profile.set_index("week_start")

    def closed(cm) -> str:
        return "-" if pd.isna(cm) else (",".join(closed_classes(cm, floors, cts)) or "open")

    tab = pd.DataFrame({
        "week_start": new["week_start"],
        "old_cm": [old["kaub_cm"].get(ws, float("nan")) for ws in new["week_start"]],
        "old_status": [old["status"].get(ws, "(new)") for ws in new["week_start"]],
        "new_cm": new["kaub_cm"], "new_status": new["status"],
    })
    tab["old_closed"] = [closed(c) for c in tab["old_cm"]]
    tab["new_closed"] = [closed(c) for c in tab["new_cm"]]
    print()
    print(f"weekly profile {args.profile} (closure floors {DEFAULT_CLOSURE_FLOORS}; t = row + 1):")
    print(tab.to_string(index=False))
    changed = int(((tab["old_cm"] != tab["new_cm"]) & ~(tab["old_cm"].isna() & tab["new_cm"].isna())).sum())
    print(f"{changed} week(s) changed, {len(new) - len(profile)} added; schedule changed for "
          f"{int((tab['old_closed'] != tab['new_closed']).sum())} week(s)")

    if args.dry_run:
        print("dry run: nothing written")
        return
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    daily.to_csv(out_dir / f"kaub_daily_{args.profile}.csv", index=False)
    new.to_csv(out_dir / f"{args.profile}.csv", index=False)
    print(f"written {out_dir / f'kaub_daily_{args.profile}.csv'} and {out_dir / f'{args.profile}.csv'}")


if __name__ == "__main__":
    main()
