"""Job lists of the sea-rate sensitivity (11 Nov 2026; the author's answer to open point 3: "ok for a small run").

The sea rate of the paper's runs is 0.0015 USD per tonne-kilometer for every cargo. This run gives bulk the operator
costs of bulk carriers and tankers (calibration/sea_rate_by_cargo.yaml). The rate changes the routes, so the run has
its own caches (tmp/r6sea) and its own Rhine capacities, anchored on its own baseline as the reference run's are:

  jobs_20261111_searate_a.txt   searate_flows_base: two weeks on the smoke profile; builds tmp/r6sea and exports the
                                baseline flows. Then, by hand:
                                python studies/rhine2026/anchor_rhine_capacities.py <runs>/searate_flows_base --headroom 0.02 \
                                    --by-cargo --out studies/rhine2026/scenarios/rhine_capacities_anchored_r6_searate.csv
  jobs_20261111_searate_b.txt   2026_r6_bycargo_searate: the reference run with the sea rates by cargo and those capacities
                                (launch with --independent once the capacities file is there).

    python studies/rhine2026/cluster/gen_jobs_20261111_searate.py
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ref = [ln.split("|", 1)[1].strip() for ln in (HERE / "jobs_20261102_2026_bycargo.txt").read_text(encoding="utf-8").splitlines()
       if ln.strip() and not ln.lstrip().startswith("#")]
assert len(ref) == 1 and ref[0].endswith("--cache-dir r6cal"), ref
SEA = "--config-set logistics.basic_cost.maritime=@studies/rhine2026/calibration/sea_rate_by_cargo.yaml --cache-dir r6sea"
flags = ref[0].replace("--cache-dir r6cal", SEA)
CAP_OLD, CAP_NEW = "scenarios/rhine_capacities_anchored_r6_bycargo.csv", "scenarios/rhine_capacities_anchored_r6_searate.csv"
assert flags.count(CAP_OLD) == 1 and flags.count("--recovery-weeks 20") == 1
a = f"searate_flows_base | --profile smoke2w {flags.replace('--recovery-weeks 20', '--recovery-weeks 0')}\n"
b = f"2026_r6_bycargo_searate | {flags.replace(CAP_OLD, CAP_NEW)}\n"
head = "# Rhine 2026 (11 Nov 2026): sea-rate sensitivity, see gen_jobs_20261111_searate.py. Checkout /projects/disruptsc/disrupt-sc-rhine.\n"
(HERE / "jobs_20261111_searate_a.txt").write_text(head + a, encoding="utf-8", newline="\n")
(HERE / "jobs_20261111_searate_b.txt").write_text(head + b, encoding="utf-8", newline="\n")
print(a[:160]); print(b[:160])
