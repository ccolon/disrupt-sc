# macroMIP s1 — DisruptSC

DisruptSC's contribution to the **macroMIP s1** stylized-forcing round (indirect
economic impacts of climate-related shocks transmitting internationally via
trade). Protocol: *protocol stylized shock experiment v1-2* (2026-03-17).

## Experiment matrix

A no-forcing baseline plus three single-country productivity shocks, each in a
temporary (one-year pulse) and a persistent variant (`sfid = sq`, primary
magnitudes):

| key | id | forcing |
|-----|----|---------|
| `exp0`  | `0`        | baseline, no forcing |
| `exp1p` / `exp1t` | `1-p-sq-0` / `1-t-sq-0` | Spain labour productivity: −4% agriculture+construction, −1% all other sectors |
| `exp2p` / `exp2t` | `2-p-sq-0` / `2-t-sq-0` | France agriculture productivity **+4%** |
| `exp3p` / `exp3t` | `3-p-sq-0` / `3-t-sq-0` | Germany manufacturing capital productivity −5% |

Forcing starts one model-year in (an unforced year first). At monthly resolution:
`start_time = 13`, temporary `duration = 12`, horizon `t_final = 120` (10 years).
Shocks are `productivity_shock`s targeted by `region` + `sector_type`.

## Build setting — "Option A" (locked)

`flow_coverage = 0.9`, `nb_suppliers_per_input = 1`, `with_transport = False`,
virtual ROW, `seed = 0`.

The firm-level supply chain only carries international trade in the long tail of
small MRIO cells, so `flow_coverage` trades transmission fidelity against
density/runtime. `0.9` keeps **~72%** of the MRIO's 13.3% international
intermediate trade at ~80 s/step (~2.7 h/experiment). `nb_suppliers_per_input`
does **not** affect international representation (it picks firms *within* an
already-fixed input region) — keep it at 1. See the project notes for the full
`flow_coverage → international-share` table.

## Running

Prerequisites: the `dsc` conda env (`pip install -e .`) and the data at
`$DISRUPT_SC_DATA_PATH/macroMIP` (or `../disrupt-sc-data/macroMIP`).

Locally, one experiment:

```bash
python scripts/run_macromip.py --experiment exp3t        # fc 0.9, monthly, 120 steps
python scripts/run_macromip.py --all                     # full matrix, sequential
```

On SLURM (one task per experiment, ~2.7 h each, isolated builds):

```bash
export DISRUPT_SC_DATA_PATH=/path/to/disrupt-sc-data
sbatch studies/macromip/slurm/run_array.sbatch
```

Edit the `module load` / `source activate` lines in the sbatch for your cluster.

## Outputs

Each `runs/macromip/<exp>/` holds the raw per-step CSVs (`firm_data.csv`,
`link_data.csv`, `household_data.csv`, ...), `run_metadata.json`, and the
macroMIP submission file produced by the adapter:

```bash
python -m disruptsc.reporting.macromip --run-dir runs/macromip/<exp>
```

The adapter emits `[id]-DisruptSC.csv` in macroMIP long format (GDP, Output,
Value Added, Imports, Exports, Household Consumption, Investment, CPI, PPI ×
country × sector × year, quantity + monetary), aggregated to annual. Relative
effects are computed against `exp0`.

## Model notes / caveats

This round required fixing three latent bugs (all merged): firm-capacity
disruption recovery, sub-buffer shock binding, and — the decisive one — firm
input receipt under `with_transport: False` (without which the no-shock baseline
collapsed; macroMIP is the first scope to run transport-off). Caveats carried in
the submission metadata: DisruptSC is demand-constrained with one-sided
(cost-push) prices, so the **positive** supply shock (Exp 2) shows ≈0 quantity
effect and no price relief; **Investment** has no model counterpart (reported
`NA`); transmission magnitude reflects the ~72% international-trade capture.
