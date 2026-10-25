"""run_rhine.py --config-set, third pass (26 Oct 2026): a filepaths.* override is resolved like the loader resolves the
config's own paths (plain relative -> the scope's data folder; repo: prefix -> the code repo; absolute unchanged) and must
exist, else the run stops at once with a clear message. Round 2 failed on the cluster because the raw relative string
'Transport/tagged/transport.gpkg' was handed to the network builder after the loader had already resolved the originals."""
from pathlib import Path

P = Path("C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc/studies/rhine2026/run_rhine.py")
s = P.read_text(encoding="utf-8"); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
old = '''        node[keys[-1]] = val
        print(f"config override: {path} = {val!r}" + ("" if args.cache_isolation else "  (no --cache-isolation: fine only for run-time keys)"))
'''
new = '''        if keys[0] == "filepaths" and isinstance(val, str):
            from disruptsc import paths as _paths
            from disruptsc.config import resolve_repo_prefix as _rrp
            resolved = _rrp(val)
            val = Path(resolved) if resolved is not val else (Path(val) if Path(val).is_absolute() else _paths.get_data_path(args.scope) / val)
            if not val.exists():
                raise SystemExit(f"--config-set {path}: {val} does not exist (pull the data repo on this machine?)")
        node[keys[-1]] = val
        print(f"config override: {path} = {val!r}" + ("" if args.cache_isolation else "  (no --cache-isolation: fine only for run-time keys)"))
'''
assert s.count(old) == 1
s = s.replace(old, new)
if "from pathlib import Path" not in s:
    s = s.replace("import argparse\n", "import argparse\nfrom pathlib import Path\n", 1)
P.write_text(s.replace("\n", nl), encoding="utf-8"); print("run_rhine.py: filepaths overrides resolved and checked")
