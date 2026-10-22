"""run_rhine.py: --container-water-cost / --container-water-vot (the container sensitivity pair of 22 Oct 2026, decision D1b):
override the container rate on waterways (config logistics.basic_cost.waterways.container, 0.022 USD/tkm) and the container
value of time on waterways (logistics.cost_of_time.container.waterways, 0.35 USD/t.h). Both enter the route fingerprint, so a run
that sets them must carry --cache-isolation (private caches); the script prints a warning otherwise."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/run_rhine.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
pairs = [
    ('    ap.add_argument("--restoration-days", type=float, default=None,',
     '    ap.add_argument("--container-water-cost", type=float, default=None,\n'
     '                    help="container rate on waterways, USD per ton-km (config 0.022); the container sensitivity of 22 Oct 2026 puts the "\n'
     '                         "Rhine containers on the river; changes the routes, so run with --cache-isolation")\n'
     '    ap.add_argument("--container-water-vot", type=float, default=None,\n'
     '                    help="container value of time on waterways, USD per ton-hour (config 0.35); same caveat")\n'
     '    ap.add_argument("--restoration-days", type=float, default=None,'),
    ('    if args.line_haul_km is not None or args.access_km is not None:\n',
     '    if args.container_water_cost is not None or args.container_water_vot is not None:\n'
     '        lg = config.setdefault("logistics", {})\n'
     '        if args.container_water_cost is not None:\n'
     '            bc = lg.setdefault("basic_cost", {}); ww = bc.get("waterways", 0.010)\n'
     '            if not isinstance(ww, dict):\n'
     '                ww = {"default": float(ww)}\n'
     '            ww["container"] = float(args.container_water_cost); bc["waterways"] = ww\n'
     '        if args.container_water_vot is not None:\n'
     '            cot = lg.setdefault("cost_of_time", {}); cc = cot.get("container", 1.0)\n'
     '            if not isinstance(cc, dict):\n'
     '                cc = {"default": float(cc)}\n'
     '            cc["waterways"] = float(args.container_water_vot); cot["container"] = cc\n'
     '        print(f"container sensitivity: waterway rate {lg[\'basic_cost\'][\'waterways\'].get(\'container\')} USD/tkm, "\n'
     '              f"waterway value of time {lg[\'cost_of_time\'][\'container\'].get(\'waterways\')} USD/t.h (routes rebuild: "\n'
     '              f"{\'private caches\' if args.cache_isolation else \'WARNING: no --cache-isolation, the shared caches would be rebuilt\'})")\n'
     '    if args.line_haul_km is not None or args.access_km is not None:\n'),
]
for old, new in pairs:
    n = s.count(old); assert n == 1, f"{n} x {old[:80]!r}"
    s = s.replace(old, new)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("run_rhine.py: container flags added")
