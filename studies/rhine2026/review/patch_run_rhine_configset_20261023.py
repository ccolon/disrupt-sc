"""run_rhine.py: --config-set PATH=VALUE (repeatable), a generic override of any config key for the recalibration rounds of
23 Oct 2026: PATH is dotted (logistics.basic_cost.waterways.container), VALUE is JSON if it parses as JSON, else YAML, else a
string; dict values replace the whole node (so a per-cargo or attribute-keyed dict is written in full). Overrides are printed
and land in the run's parameters.yaml like every other config value. They enter the cache fingerprint when they touch the
network, agents or routes, so candidate runs carry --cache-isolation."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/run_rhine.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
pairs = [
    ('    ap.add_argument("--container-water-cost", type=float, default=None,',
     '    ap.add_argument("--config-set", action="append", default=[], metavar="PATH=VALUE",\n'
     '                    help="override a config key (dotted path; JSON, else YAML value; repeatable): the recalibration rounds of 23 Oct 2026, "\n'
     '                         "e.g. --config-set logistics.basic_cost.waterways.container=0.015; a dict value replaces the node; "\n'
     '                         "network/route keys need --cache-isolation")\n'
     '    ap.add_argument("--container-water-cost", type=float, default=None,'),
    ('    if args.container_water_cost is not None or args.container_water_vot is not None:\n',
     '    for item in args.config_set:\n'
     '        import json as _json\n'
     '        import yaml as _yaml\n'
     '        path, _, raw = item.partition("=")\n'
     '        if not path or not _:\n'
     '            raise SystemExit(f"--config-set expects PATH=VALUE, got {item!r}")\n'
     '        try:\n'
     '            val = _json.loads(raw)\n'
     '        except ValueError:\n'
     '            val = _yaml.safe_load(raw)\n'
     '        node = config\n'
     '        keys = path.split(".")\n'
     '        for k in keys[:-1]:\n'
     '            if not isinstance(node.get(k), dict):\n'
     '                node[k] = {}\n'
     '            node = node[k]\n'
     '        node[keys[-1]] = val\n'
     '        print(f"config override: {path} = {val!r}" + ("" if args.cache_isolation else "  (no --cache-isolation: fine only for run-time keys)"))\n'
     '    if args.container_water_cost is not None or args.container_water_vot is not None:\n'),
]
for old, new in pairs:
    n = s.count(old); assert n == 1, f"{n} x {old[:80]!r}"
    s = s.replace(old, new)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("run_rhine.py: --config-set added")
