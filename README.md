# DisruptSC

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/ccolon/disrupt-sc/releases/tag/v2.0.0)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen)](https://ccolon.github.io/disrupt-sc)
[![License](https://img.shields.io/github/license/ccolon/disrupt-sc)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/ccolon/disrupt-sc)](https://github.com/ccolon/disrupt-sc/issues)

**Spatial agent-based model for supply chain disruption analysis**

_DisruptSC_ simulates the economic impact of supply chain disruptions using spatial transport networks, multi-regional input-output data, and agent-based modeling. It analyzes transport infrastructure failures, natural disasters, productivity shocks, and other disruptions across countries and regions.

> **v2.0 is a major release.** The module layout, CLI entry point, and several config keys changed. If you are upgrading from v1, read [MIGRATION.md](MIGRATION.md). The legacy v1 line is preserved on the [`legacy/v1`](https://github.com/ccolon/disrupt-sc/tree/legacy/v1) branch and tagged [`v1-last-submodule`](https://github.com/ccolon/disrupt-sc/releases/tag/v1-last-submodule).

## Quick Start

### Install

```bash
git clone https://github.com/ccolon/disrupt-sc.git
cd disrupt-sc

conda env create -f dsc-environment.yml
conda activate dsc

pip install -e .
```

### Run the bundled demo

The repo ships with a small demo scope, `Testkistan`, under `examples/data/Testkistan/`. No extra download required.

```bash
# Sanity-check the demo inputs
validate-inputs Testkistan

# Baseline equilibrium
disruptsc Testkistan

# Disruption scenario
disruptsc Testkistan --simulation_type disruption
```

### Use your own data

Full regional scopes (ECA, Ecuador, Gulf, Cambodia, …) live in a separate data repo. Point DisruptSC at a data folder either by cloning it next to this repo:

```bash
cd ..
git clone <data-repo-url> disrupt-sc-data
cd disrupt-sc
disruptsc ECA
```

…or by setting an environment variable:

```bash
# PowerShell
$env:DISRUPT_SC_DATA_PATH = "C:\path\to\disrupt-sc-data"
# bash/zsh
export DISRUPT_SC_DATA_PATH=/path/to/disrupt-sc-data
```

Resolution order: `DISRUPT_SC_DATA_PATH` → sibling `../disrupt-sc-data` → bundled `examples/data/`.

You also need a scope parameter file. Only the bundled `Testkistan` scope ships with one (`config/user_defined_Testkistan.yaml`). For any other scope, create a gitignored personal file `config/user_defined_<scope>.local.yaml` with the paths and options for your data folder.

## What's in v2

- **Pipeline architecture.** The monolithic `Model` class and `Parameters` loader are gone. Initialization (`init_pipeline/`) and execution (`run_pipeline/`) are organized as explicit stages — easier to cache, resume, and reason about.
- **Frozen, typed parameter bundles.** `TransportParams`, `SimParams`, `AgentParams`, `LogisticsParams` dataclasses replace the v1 `Parameters` object. Config loading is a flat `dict` + dataclass build step.
- **Unified transport graph.** Transport data is now consumed from `transport.gpkg` + `multimodal.gpkg` rather than one GeoJSON per mode.
- **Alternative routing + capacity-aware costs.** Rerouting under disruption, price-increase thresholds, LP-based flow assignment, capacity constraints.
- **Local-first config.** Only `Testkistan`'s scope YAML ships with the repo. For any other scope, drop a gitignored `config/user_defined_<scope>.local.yaml` pointing at your own data folder — the model picks it up automatically.
- **Bundled demo data.** No submodule required to run the model out of the box.

See [MIGRATION.md](MIGRATION.md) for the full list of changes from v1.

## Documentation

Full documentation: **[https://ccolon.github.io/disrupt-sc](https://ccolon.github.io/disrupt-sc)**

- **[Getting Started](https://ccolon.github.io/disrupt-sc/getting-started/)** – install, data setup, first simulation
- **[User Guide](https://ccolon.github.io/disrupt-sc/user-guide/)** – parameters, data modes, inputs and outputs
- **[Architecture](https://ccolon.github.io/disrupt-sc/architecture/)** – model design, agents, networks, disruptions

## Key Features

- **Spatial multimodal transport**: roads, rail, maritime, airways, waterways, pipelines
- **Agent-based economy**: firms, households, and countries with spatial disaggregation from MRIO data
- **Disruption scenarios**: transport-edge failures, capital destruction, productivity shocks, capacity shocks
- **Monte Carlo support**: configurable `mc_repetitions` for disruption and initial-state runs
- **Input validation**: comprehensive data-quality checks before simulation

## Legacy v1

The last v1 release lives at:

- Branch: [`legacy/v1`](https://github.com/ccolon/disrupt-sc/tree/legacy/v1)
- Tag: [`v1-last-submodule`](https://github.com/ccolon/disrupt-sc/releases/tag/v1-last-submodule)

v1 is no longer actively developed. Bug reports and feature requests on v1 will generally be directed to v2.

## Contributing & Support

- **Issues**: [Report bugs or request features](https://github.com/ccolon/disrupt-sc/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/ccolon/disrupt-sc/discussions)
- **Get involved**: see [contributor guidelines](https://ccolon.github.io/disrupt-sc/contacts/)

## Citation

If you use _DisruptSC_, please cite:

Colon, C., Hallegatte, S., & Rozenberg, J. (2021). Criticality analysis of a country's transport network via an agent-based supply chain model. *Nature Sustainability*, 4(3), 209–215.

```bibtex
@article{colon2021disruptsc,
  author  = {Celian Colon and Stephane Hallegatte and Julie Rozenberg},
  title   = {Criticality analysis of a country's transport network via an agent-based supply chain model},
  journal = {Nature Sustainability},
  volume  = {4},
  pages   = {209--215},
  year    = {2021},
  doi     = {10.1038/s41893-020-00649-4},
  url     = {https://www.nature.com/articles/s41893-020-00649-4}
}
```

```bibtex
@software{disruptsc_software,
  title  = {DisruptSC: Spatial Agent-Based Model for Supply Chain Disruption Analysis},
  author = {Celian Colon},
  year   = {2026},
  url    = {https://github.com/ccolon/disrupt-sc}
}
```
