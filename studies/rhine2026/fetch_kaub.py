"""Refresh the 2026 Kaub profile of the Rhine study from PEGELONLINE (REST API, raw 15-min W).

Daily means in legal time (Europe/Berlin), the convention of scenarios/kaub_daily_2026.csv; a day
with fewer than 90 of the 96 values is flagged PARTIAL. The weekly rows of scenarios/2026.csv are
rebuilt: a fully observed week -> status 'observed'; a week with some observed days ->
'observed+forecast' (observed days + --fill-cm for the missing days, default = persistence of the
last observed day); later weeks keep their assumption rows. The closure classes per week under the
driver's default floors are printed for the old and the new profile, so a schedule change is visible.

    python studies/rhine2026/fetch_kaub.py --dry-run              # show what would change
    python studies/rhine2026/fetch_kaub.py --fill-cm 24           # write, filling the open week with 24 cm
    python studies/rhine2026/fetch_kaub.py --out-dir <dir>        # write the two files elsewhere (staging)

The REST API serves at most the last 30 days; older days come from the long-term download already
in kaub_daily_2026.csv (identical values: cross-checked 29 Aug - 4 Sep 2026).
"""
import argparse
import json
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime
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


def rebuild_profile(profile: pd.DataFrame, daily: pd.DataFrame, fill_cm: float | None) -> pd.DataFrame:
    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["partial"] = d["source"].str.contains("PARTIAL")
    d = d.set_index("date")
    last_full = d[~d["partial"]]["kaub_cm"].iloc[-1]
    fill = last_full if fill_cm is None else fill_cm
    fill_note = "persistence of the last observed day" if fill_cm is None else "--fill-cm"
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
                                f"remaining {7 - len(v)} days at {fill:.0f} cm ({fill_note}); {prev}"})
        else:
            out.append({"week_start": r["week_start"], "kaub_cm": r["kaub_cm"], "status": r["status"], "note": r["note"]})
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="days of 15-min data to fetch (API maximum 30)")
    ap.add_argument("--fill-cm", type=float, default=None, help="gauge assumed for the missing days of the open week")
    ap.add_argument("--profile", default="2026")
    ap.add_argument("--out-dir", default=str(SCEN), help="where to write kaub_daily_<profile>.csv and <profile>.csv")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    fetched_on = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    fetched = fetch_daily(args.days)
    print(f"fetched {len(fetched)} days ({fetched['date'].iloc[0]} to {fetched['date'].iloc[-1]}, {fetched_on}):")
    print(fetched.to_string(index=False))

    daily_path = SCEN / f"kaub_daily_{args.profile}.csv"
    existing = pd.read_csv(daily_path)
    daily = merge_daily(existing, fetched, fetched_on)
    profile = pd.read_csv(SCEN / f"{args.profile}.csv")
    new = rebuild_profile(profile, daily, args.fill_cm)

    floors = parse_closure_floors(DEFAULT_CLOSURE_FLOORS)
    cts = list(DEFAULT_CARGO_TYPES)
    tab = pd.DataFrame({
        "week_start": profile["week_start"], "old_cm": profile["kaub_cm"], "old_status": profile["status"],
        "new_cm": new["kaub_cm"], "new_status": new["status"],
        "old_closed": [",".join(closed_classes(c, floors, cts)) or "-" for c in profile["kaub_cm"]],
        "new_closed": [",".join(closed_classes(c, floors, cts)) or "-" for c in new["kaub_cm"]],
    })
    print()
    print(f"weekly profile {args.profile} (closure floors {DEFAULT_CLOSURE_FLOORS}):")
    print(tab.to_string(index=False))
    changed = tab[(tab["old_cm"] != tab["new_cm"]) | (tab["old_closed"] != tab["new_closed"])]
    print(f"{len(changed)} week(s) changed; schedule changed for {int((tab['old_closed'] != tab['new_closed']).sum())} week(s)")

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
