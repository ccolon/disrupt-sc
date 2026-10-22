"""run_rhine.py --config-set, second pass: VALUE may be @<yaml file> (the launcher wraps the payload in single quotes, so job
lines cannot carry quoted JSON; the round files live in studies/rhine2026/calibration/), and the overrides are applied right
after the config is loaded, so that --dry-run prints them too."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/run_rhine.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
block_start = s.index("    for item in args.config_set:\n")
block_end = s.index("    if args.container_water_cost is not None or args.container_water_vot is not None:\n")
block = s[block_start:block_end]
s = s[:block_start] + s[block_end:]
block = block.replace(
    "        try:\n            val = _json.loads(raw)\n        except ValueError:\n            val = _yaml.safe_load(raw)\n",
    "        if raw.startswith(\"@\"):\n"
    "            with open(raw[1:], encoding=\"utf-8\") as fh:\n"
    "                val = _yaml.safe_load(fh)\n"
    "        else:\n"
    "            try:\n                val = _json.loads(raw)\n            except ValueError:\n                val = _yaml.safe_load(raw)\n")
anchor = "    config = load_config(args.scope)\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + block)
s = s.replace('help="override a config key (dotted path; JSON, else YAML value; repeatable)',
              'help="override a config key (dotted path; VALUE = JSON, else YAML, or @<yaml file>; repeatable)')
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("run_rhine.py: --config-set moved after load_config, @file values")
