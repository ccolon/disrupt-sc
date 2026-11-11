r"""fetch_kaub.py, 11 November 2026: three inputs for the profile of the season as observed (run once; exact anchors).

  --staged DIR          raw 15-minute JSON files of the REST service saved earlier (scenarios/staging_20261111): the
                        service keeps 31 days, so days fetched on another date are merged from the saved files;
  --long-term FILE      a file of the station's long-term raw download (JSON or CSV of 15-minute values), for the days
                        that the REST service no longer serves; it is the reference for those days, as in June 2026;
  --forecast-14day CSV  the BfG 14-day forecast (daily medians): the missing days of the open week, a partial day
                        included, and every later week that it covers in full; weeks beyond it keep the 6-week outlook.
    python patch_fetch_kaub_20261111.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from si_patchlib import Doc  # noqa: E402

d = Doc(HERE.parent / "fetch_kaub.py")

# ---- docstring ---------------------------------------------------------------------------------------------------------
d.sub('''    python studies/rhine2026/fetch_kaub.py --out-dir <dir>        # write the two files elsewhere (staging)
''',
      '''    python studies/rhine2026/fetch_kaub.py --out-dir <dir>        # write the two files elsewhere (staging)
    python studies/rhine2026/fetch_kaub.py --staged studies/rhine2026/scenarios/staging_20261111 \\
        --long-term <file of the station's long-term download> \\
        --forecast-14day studies/rhine2026/scenarios/bfg_14day_kaub_20261111.csv \\
        --forecast-6week studies/rhine2026/scenarios/bfg_6week_kaub_20261109.csv   # the season as observed (11 Nov 2026)

11 Nov 2026: --staged merges raw 15-minute files of the REST service saved on an earlier day; --long-term merges a file
of the station's long-term raw download (the days that the REST service no longer serves); --forecast-14day takes the
daily medians of the BfG 14-day forecast (https://vorhersage.bafg.de/14-Tage-Vorhersage/Kaub_Quantile_25700100.csv) for
the missing days of the open week, a partial day included, and for every later week that it covers in full.
''')

# ---- daily means from any list of 15-minute measurements ---------------------------------------------------------------
d.sub('''def fetch_daily(days: int) -> pd.DataFrame:
    with urllib.request.urlopen(API.format(days=days), timeout=90) as r:
        data = json.load(r)
    tz = ZoneInfo("Europe/Berlin")
''',
      '''def fetch_daily(days: int) -> pd.DataFrame:
    with urllib.request.urlopen(API.format(days=days), timeout=90) as r:
        data = json.load(r)
    return daily_means(data)


def read_measurements(path: Path) -> list[dict]:
    """15-minute measurements of a saved file: the REST service's JSON (a list of {timestamp, value}), the long-term
    download as JSON (the same list, possibly under a key) or as CSV (timestamp;value, decimal comma allowed)."""
    path = Path(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            lists = [v for v in data.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
            if len(lists) != 1:
                raise SystemExit(f"{path.name}: {len(lists)} lists of measurements found, expected one")
            data = lists[0]
        out = []
        for m in data:
            ts = m.get("timestamp") or m.get("time") or m.get("datetime")
            val = m.get("value") if "value" in m else m.get("wert")
            if ts is None or val is None:
                continue
            out.append({"timestamp": ts, "value": float(val)})
        return out
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = re.split(r"[;,\\t]", line.strip(), maxsplit=1)
        if len(parts) != 2:
            continue
        try:
            ts = datetime.fromisoformat(parts[0].strip().strip('"'))
            val = float(parts[1].strip().strip('"').replace(",", "."))
        except ValueError:
            continue
        out.append({"timestamp": ts.isoformat(), "value": val})
    return out


def daily_means(data: list[dict]) -> pd.DataFrame:
    """Daily means in legal time of a list of {timestamp, value}; duplicate timestamps count once."""
    tz = ZoneInfo("Europe/Berlin")
    data = list({m["timestamp"]: m for m in data}.values())
''')

d.sub('''def parse_extend(raw: str | None) -> list[tuple[str, float]]:''',
      '''def parse_forecast_14day(path) -> tuple[str, dict[str, dict]]:
    """BfG 14-day quantile CSV (daily means) -> (issue date, {date iso: {p5, p25, median, p75, p95}})."""
    issued, rows, cols = "?", {}, None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            m = re.search(r"Wasserstandsvorhersage vom (\\d{4}-\\d{2}-\\d{2})", line)
            if m:
                issued = m.group(1)
            continue
        parts = [p.strip() for p in line.split(";")]
        if parts[0] == "Datum":
            cols = {name: i for i, name in enumerate(parts)}
            continue
        if cols is None or len(parts) < len(cols):
            continue
        day = datetime.strptime(parts[0].split(" ")[0], "%d.%m.%Y").date().isoformat()
        rows[day] = {"p5": float(parts[cols["5%"]]), "p25": float(parts[cols["25%"]]), "median": float(parts[cols["50%"]]),
                     "p75": float(parts[cols["75%"]]), "p95": float(parts[cols["95%"]])}
    return issued, rows


def parse_extend(raw: str | None) -> list[tuple[str, float]]:''')

# ---- the profile: the 14-day forecast for the open week and the weeks it covers ------------------------------------
d.sub('''def rebuild_profile(profile: pd.DataFrame, daily: pd.DataFrame, fill_cm: float | None, fill_note: str | None = None,
                    forecast: tuple[str, dict] | None = None, extend: list[tuple[str, float]] | None = None,
                    extend_note: str = DEFAULT_EXTEND_NOTE) -> pd.DataFrame:''',
      '''def rebuild_profile(profile: pd.DataFrame, daily: pd.DataFrame, fill_cm: float | None, fill_note: str | None = None,
                    forecast: tuple[str, dict] | None = None, extend: list[tuple[str, float]] | None = None,
                    extend_note: str = DEFAULT_EXTEND_NOTE, forecast14: tuple[str, dict] | None = None) -> pd.DataFrame:''')
d.sub('''    issued, fc = forecast if forecast else ("?", {})

    def forecast_row(ws: str, prev: str) -> dict:''',
      '''    issued, fc = forecast if forecast else ("?", {})
    issued14, fc14 = forecast14 if forecast14 else ("?", {})

    def days_of(ws: str) -> list[str]:
        return [(pd.Timestamp(ws) + pd.Timedelta(days=i)).date().isoformat() for i in range(7)]

    def forecast14_row(ws: str, prev: str) -> dict:
        med = [fc14[x]["median"] for x in days_of(ws)]
        lo, hi = min(fc14[x]["p5"] for x in days_of(ws)), max(fc14[x]["p95"] for x in days_of(ws))
        return {"week_start": ws, "kaub_cm": round(float(np.mean(med)), 1), "status": "forecast",
                "note": f"BfG 14-day forecast issued {issued14}: mean of the daily medians ({', '.join(f'{x:.0f}' for x in med)} cm; "
                        f"5-95 % of the days {lo:.0f} to {hi:.0f}); {prev}"}

    def forecast_row(ws: str, prev: str) -> dict:''')
d.sub('''        elif len(v) > 0:
            obs = ", ".join(f"{x:.0f}" for x in v["kaub_cm"])''',
      '''        elif len(v) > 0 and fc14 and all(x in fc14 for x in days_of(r["week_start"])
                                         if pd.Timestamp(x) not in v.index[~v["partial"]]):
            # the open week with the 14-day forecast: full observed days, then the daily medians (a partial day included)
            full = v[~v["partial"]]
            if len(full) == 0:
                out.append(forecast14_row(r["week_start"], prev))
                continue
            rest = [x for x in days_of(r["week_start"]) if pd.Timestamp(x) not in full.index]
            med = [fc14[x]["median"] for x in rest]
            est = (float(full["kaub_cm"].sum()) + float(np.sum(med))) / 7
            obs = ", ".join(f"{x:.0f}" for x in full["kaub_cm"])
            out.append({"week_start": r["week_start"], "kaub_cm": round(est, 1), "status": "observed+forecast",
                        "note": f"{full.index[0].date()} to {full.index[-1].date()} observed daily means ({obs}), remaining "
                                f"{len(rest)} days at the daily medians of the BfG 14-day forecast issued {issued14} "
                                f"({', '.join(f'{x:.0f}' for x in med)} cm); {prev}"})
        elif len(v) > 0:
            obs = ", ".join(f"{x:.0f}" for x in v["kaub_cm"])''')
d.sub('''        elif r["week_start"] in fc:
            out.append(forecast_row(r["week_start"], prev))
        else:''',
      '''        elif fc14 and all(x in fc14 for x in days_of(r["week_start"])):
            out.append(forecast14_row(r["week_start"], prev))
        elif r["week_start"] in fc:
            out.append(forecast_row(r["week_start"], prev))
        else:''')

# ---- main: the new inputs --------------------------------------------------------------------------------------------
d.sub('''    ap.add_argument("--forecast-6week", default=None, help="BfG 6-week QuansBox CSV: ENS medians for the weeks without observations")
''',
      '''    ap.add_argument("--forecast-6week", default=None, help="BfG 6-week QuansBox CSV: ENS medians for the weeks without observations")
    ap.add_argument("--forecast-14day", default=None, help="BfG 14-day quantile CSV: daily medians for the open week and the weeks it covers in full")
    ap.add_argument("--staged", default=None, help="folder of raw 15-minute JSON files of the REST service saved earlier (kaub_15min_*.json)")
    ap.add_argument("--long-term", default=None, help="file of the station's long-term raw download (JSON or CSV), the reference for older days")
    ap.add_argument("--no-fetch", action="store_true", help="do not call the REST service (rebuild from the saved files only)")
''')
d.sub('''    fetched_on = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    fetched = fetch_daily(args.days)
    print(f"fetched {len(fetched)} days ({fetched['date'].iloc[0]} to {fetched['date'].iloc[-1]}, {fetched_on}):")
    print(fetched.tail(10).to_string(index=False))

    daily_path = SCEN / f"kaub_daily_{args.profile}.csv"
    existing = pd.read_csv(daily_path)
    daily = merge_daily(existing, fetched, fetched_on)
''',
      '''    fetched_on = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
    daily_path = SCEN / f"kaub_daily_{args.profile}.csv"
    daily = pd.read_csv(daily_path)
    if args.long_term:                              # the reference for the days the REST service no longer serves
        lt = daily_means(read_measurements(Path(args.long_term)))
        have = set(daily.loc[~daily["source"].str.contains("PARTIAL"), "date"])
        lt = lt[(lt["n"] >= FULL_DAY) & ~lt["date"].isin(have)]
        add = pd.DataFrame({"date": lt["date"], "kaub_cm": lt["kaub_cm"], "source": LONG_TERM_SOURCE + f", downloaded {fetched_on[:10]}"})
        daily = pd.concat([daily[~daily["date"].isin(set(add["date"]))], add]).sort_values("date").reset_index(drop=True)
        print(f"long-term download {Path(args.long_term).name}: {len(add)} full days added"
              + (f" ({add['date'].iloc[0]} to {add['date'].iloc[-1]})" if len(add) else ""))
    if args.staged:
        files = sorted(Path(args.staged).glob("kaub_15min_*.json"))
        staged = daily_means([m for f in files for m in read_measurements(f)])
        when = datetime.fromtimestamp(max(f.stat().st_mtime for f in files), ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%d %H:%M")
        daily = merge_daily(daily, staged, when)
        print(f"staged files ({len(files)}, saved {when}): {len(staged)} days ({staged['date'].iloc[0]} to {staged['date'].iloc[-1]})")
    if not args.no_fetch:
        fetched = fetch_daily(args.days)
        print(f"fetched {len(fetched)} days ({fetched['date'].iloc[0]} to {fetched['date'].iloc[-1]}, {fetched_on}):")
        print(fetched.tail(10).to_string(index=False))
        daily = merge_daily(daily, fetched, fetched_on)
    dd = pd.to_datetime(daily["date"])
    gaps = sorted(set(pd.date_range(dd.min(), dd.max()).date) - set(dd.dt.date))
    if gaps:
        print(f"WARNING: {len(gaps)} day(s) missing in the daily record, {gaps[0]} to {gaps[-1]}")
''')
d.sub('''    new = rebuild_profile(profile, daily, args.fill_cm, args.fill_note, forecast, parse_extend(args.extend), args.extend_note)
''',
      '''    forecast14 = parse_forecast_14day(args.forecast_14day) if args.forecast_14day else None
    if forecast14:
        print(f"14-day forecast issued {forecast14[0]}: days {min(forecast14[1])} to {max(forecast14[1])}")
    new = rebuild_profile(profile, daily, args.fill_cm, args.fill_note, forecast, parse_extend(args.extend), args.extend_note,
                          forecast14)
''')
d.sub('''FULL_DAY = 90
''',
      '''LONG_TERM_SOURCE = ("PEGELONLINE WSV long-term raw download (ungepruefte Rohdaten, DL-DE->Zero-2.0), daily mean of 15-min W "
                    "values in legal time, https://www.pegelonline.wsv.de/gast/stammdaten?pegelnr=25700100")
FULL_DAY = 90
''')
d.sub('''import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_rhine import''',
      '''import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_rhine import''')
d.save()
