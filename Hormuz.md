# Hormuz Strait Blockade — Food & Import Price Impacts on Gulf States

## Context

DisruptSC is a spatial agent-based supply chain model that combines MRIO economics with
multi-modal transport networks to estimate cascading impacts of transport disruptions on
prices, production, and consumption. The ECA and Armenia applications demonstrate two
modes: criticality scanning and disruption scenario analysis. This document describes how to
apply the same framework to estimate how a Hormuz Strait blockade would raise food (and
other commodity) prices in Gulf states, by making the strait a breakable maritime edge in
the transport network.

---

## Scope

**Countries modeled explicitly (7 core):**
- UAE, QAT, KWT, BHR, OMN, SAU, IRQ
- IRN optional (its economy is structurally different; may complicate MRIO)

**External trade blocs (country agents, not fully modeled):**
- IND (India — major food exporter to Gulf)
- PAK (Pakistan — food/labor)
- EAS (East Asia — manufactured goods)
- EUR (Europe — processed food, machinery)
- ROW (Rest of World)
- AFR (Africa — some food)

**Key sectors (start lean, expand):**
- AGR (agriculture/food, primary)
- FOD (food processing)
- MAN (manufacturing — general imports)
- TRD (wholesale/retail — for price propagation to consumers)
- ENE (energy — optional; Gulf exports oil, but this affects domestic fuel costs for transport)

---

## Disruption Configuration

The Hormuz Strait is represented as a **named maritime edge** (`maritime-HORMUZ`)
connecting Gulf ports (UAE/Abu Dhabi, Dubai, QAT/Doha, KWT/Kuwait City, BHR/Manama,
IRQ/Basra) to the Indian Ocean. A `transport_disruption` blocks this edge for a range of
durations.

**Disruption YAML skeleton:**
```yaml
disruptions:
  - type: transport_disruption
    description_type: edge_attributes
    attribute: name
    values: [maritime-HORMUZ]
    start_time: 1
    duration: 30   # varied in sensitivity analysis
```

**Sensitivity analysis on duration:** [7, 14, 30, 60, 90, 180, 365] days

**Alternative routes that must exist in the network:**

| Route | Description | Applies to |
|---|---|---|
| Saudi East-West + Red Sea (Jeddah) | Overland road to Red Sea port | SAU only |
| Cape of Good Hope reroute | Maritime +12,000 km detour | All states (expensive) |
| Suez/Red Sea + Aqaba | Shorter alternative for European/American goods | SAU, JOR corridor |
| Air freight | Ultra-high cost, small volume | Perishables only |

The model will naturally find least-cost alternatives once Hormuz is blocked, **if these
alternative maritime edges and road links exist in the network**.

---

## Data Required

### 1. MRIO Table — `Economic/mrio.csv`

**Format:** Square matrix, region-sector × region-sector, mUSD/year (or /day)
**Resolution needed:** 7 Gulf states + ~5–6 external blocs × ~6–10 sectors

**Best sources (in order of preference):**

| Source | Coverage | Sectors | Notes |
|---|---|---|---|
| **GTAP 11** | All Gulf states | 65 sectors | Best coverage, requires license |
| **OECD TiVA 2023** | UAE, SAU, KWT, OMN, BHR, QAT | 45 sectors | Free, from ICIO |
| **UN Comtrade + EORA26** | All | 26 sectors | Free, lower quality |
| **World Bank WITS** | Bilateral trade data | HS codes → map to sectors | Requires concordance |

**Practical recommendation:** Use OECD TiVA bilateral trade flows + domestic IO tables from
Gulf national statistics offices (UAE, QAT, SAU publish these) to construct a custom MRIO.
Start with EORA26 as a quick baseline.

**Key data point needed:** Food import dependency ratio per country (what % of food is
imported and from where). Publicly available from FAO FAOSTAT.

### 2. Sector Table — `Economic/sector_table.csv`

Columns: `region_sector, type, usd_per_ton, share_exporting_firms`

**USD/ton values for key commodities (approximate):**
- Cereals/grains: ~250 USD/ton
- Rice: ~400 USD/ton
- Vegetables/fruit: ~700–1,500 USD/ton
- Live animals/meat: ~2,000–5,000 USD/ton
- Processed food: ~1,500–3,000 USD/ton
- Manufacturing: ~5,000–20,000 USD/ton

Source: UN Comtrade unit values or FAO price data.

### 3. Maritime Transport Network — `Transport/maritime_edges.geojson`

**Edges needed (LineString geometries, WGS84):**

| Edge name | From | To | Notes |
|---|---|---|---|
| `maritime-HORMUZ` | Gulf ports | Gulf of Oman | **The blocked edge** |
| `maritime-GULF-UAE` | Abu Dhabi/Dubai port | Hormuz entry | Internal Gulf leg |
| `maritime-GULF-QAT` | Doha port | Hormuz entry | |
| `maritime-GULF-KWT` | Kuwait port | Hormuz entry | |
| `maritime-GULF-BHR` | Manama port | Hormuz entry | |
| `maritime-GULF-SAU` | Dammam port | Hormuz entry | |
| `maritime-GULF-IRQ` | Basra/Umm Qasr | Hormuz entry | |
| `maritime-OMAN-SEA` | Muscat/Sohar | Indian Ocean | Oman has direct access |
| `maritime-REDSEA-N` | Jeddah | Suez | SAU alternative |
| `maritime-REDSEA-S` | Gulf of Aden | Red Sea | |
| `maritime-INDIAN-W` | Indian Ocean | Gulf of Oman | Connects India/Asia |
| `maritime-CAPE` | Indian Ocean | Atlantic | Long reroute alternative |

**Data source:** OpenStreetMap maritime layer + manual construction of key strait segments.
Tools: QGIS for digitizing, overpy/osmnx for OSM extraction.

Port coordinates (lat/lon): World Port Index (NIMA/NGA, free download).

### 4. Road Network — `Transport/roads_edges.geojson`

Need internal road networks of Gulf states for domestic distribution:
- OpenStreetMap extract for UAE, QAT, SAU, KWT, BHR, OMN, IRQ
- Filter to primary + trunk roads (sufficient for inter-city flows)
- Cross-border roads: Saudi-UAE, Saudi-Kuwait, Saudi-Bahrain (King Fahd Causeway), UAE-Oman

**Tool:** `osmnx` Python library.

### 5. Multimodal Transfer Points — `Transport/multimodal_edges.geojson`

Short edges connecting road network nodes to port nodes (road ↔ maritime transfer).

Key ports: Jebel Ali (UAE), Khalifa (UAE), Hamad (QAT), Shuaiba (KWT), Dammam (SAU),
Sohar (OMN), Salalah (OMN — critical Red Sea bypass), Jeddah (SAU).

### 6. Spatial Data

**`Spatial/countries.geojson`** — Entry points for external trade partners:
- India entry point: Strait of Hormuz / Indian Ocean node
- Europe entry point: Suez Canal / Red Sea node
- East Asia entry: Indian Ocean east node

**`Spatial/households.geojson`** — Population centers in each Gulf state:
- UAE: Abu Dhabi, Dubai, Sharjah
- SAU: Riyadh, Jeddah, Dammam
- QAT: Doha
- KWT: Kuwait City
- BHR: Manama
- OMN: Muscat
- IRQ: Baghdad, Basra

Source: GPW (Gridded Population of the World) or UN World Urbanization Prospects.

---

## Key Assumptions

| Assumption | Value | Justification |
|---|---|---|
| Gulf states import ~80–90% of food | 80–90% | FAO data |
| Hormuz handles ~90% of Gulf maritime imports | 90% | IEA, port statistics |
| Alternative Cape route adds ~14,000 km | +14,000 km | Geography |
| Maritime freight rate increase on reroute | ×3–5× | Distance-proportional + insurance |
| Saudi Red Sea bypass partially available | 20–30% of Saudi imports | Jeddah Islamic Port capacity |
| Oman has direct Indian Ocean access | Full bypass | Geography — Muscat outside Gulf |
| Air freight volume ceiling | ~1–2% of food by weight | Aircraft weight constraints |
| Blockade duration range for sensitivity | 7–365 days | Political scenario range |
| No war damage to domestic infrastructure | Clean blockade | Scope limitation |

---

## Code Changes Required

**No core model logic changes expected.** The framework already supports:
- Maritime transport mode
- Named edge disruptions
- Sensitivity analysis on duration
- Monte Carlo for stochasticity

**New files to create (analogous to ECA):**

```
data/Gulf/
├── Economic/
│   ├── mrio.csv
│   ├── sector_table.csv
│   └── usd_per_ton.csv
├── Transport/
│   ├── roads_edges.geojson
│   ├── maritime_edges.geojson
│   ├── multimodal_edges.geojson
│   └── (railways_edges.geojson — optional, minor role in Gulf)
└── Spatial/
    ├── countries.geojson
    └── households.geojson

config/parameters/user_defined_Gulf.yaml
```

**Minor potential code change to verify:** Check that the disruption executor correctly
handles maritime blockades where **all** edges connecting a sub-region are cut (vs. a
single road edge among many alternatives). The ECA scenario disrupts one railway line
among several alternatives; Hormuz disrupts **the only entry point** for most Gulf states.
This is a more total disruption and may expose edge cases in the rerouting logic.

**File to check:** `src/disruptsc/network/transport_network.py` — confirm that when no
viable route exists, the model gracefully records unmet demand (import shortfall) rather
than crashing.

---

## Config Sketch — `user_defined_Gulf.yaml`

```yaml
scope: Gulf
time_resolution: day
t_final: 90                  # 3-month baseline run; vary for sensitivity

transport_modes: [roads, maritime]  # railways minor in Gulf; add if data available
capacity_constraint: "off"   # like ECA — focus on cost signal, not physical caps

io_cutoff: 0.05
cutoff_firm_output: 500      # kUSD
cutoff_household_demand: 500

logistics:
  speeds:
    roads: 80                # Gulf highways, km/h
    maritime: 20             # Container ships, km/h
  cost_per_ton_km:
    roads: 0.08
    maritime: 0.004          # Lower than ECA — larger ocean-going vessels
  border_fees:
    roads: 35
    maritime: 15             # Standard port handling, USD/ton
  cost_of_time: 0.45         # USD/hour/ton

disruptions:
  - type: transport_disruption
    description_type: edge_attributes
    attribute: name
    values: [maritime-HORMUZ]
    start_time: 1
    duration: 30

sensitivity:
  parameter: disruptions[0].duration
  values: [7, 14, 30, 60, 90, 180, 365]
```

---

## Expected Outputs & Metrics

| Metric | Description |
|---|---|
| `household_consumption_loss` per country | Welfare impact of import shortfall |
| `price_increase_pct` per sector per country | % rise in food/import prices |
| `import_shortfall_tons` | Physical volume unmet due to rerouting delay/cost |
| `rerouting_cost_increase` | Extra freight cost (USD) — direct price signal |
| `recovery_dynamics` | How quickly imports resume via alternative routes |

**Primary output of interest:** Price increase % for food sectors in each Gulf state,
as a function of blockade duration.

---

## Recommended Execution Sequence

1. **Quick baseline** — Use EORA26 MRIO (free) + manually digitized Hormuz maritime
   edge + simplified household spatial data. Run a single 30-day disruption. Validate
   that import flows drop and prices rise. Ignore fine geographic detail.

2. **Improved MRIO** — Upgrade to GTAP or OECD TiVA for better sectoral resolution on
   food sub-sectors. Validate against FAO food import dependency statistics.

3. **Full sensitivity analysis** — Sweep disruption durations [7–365 days]. Add Monte
   Carlo if uncertainty on alternative route capacity is important.

4. **Policy scenarios** (optional) — Compare impact with vs. without Saudi Red Sea bypass,
   with vs. without strategic food reserves (modeled as extra inventory days in the config).

---

## Critical Files to Reference

| File | Role |
|---|---|
| `config/parameters/default.yaml` | All available parameters |
| `config/parameters/user_defined_ECA.yaml` | Template for new Gulf config |
| `src/disruptsc/disruption/disruption.py` | Verify blockade disruption type works |
| `src/disruptsc/network/transport_network.py` | Verify graceful handling of full route cut |
| `src/disruptsc/model/agent_builders/country.py` | How external trade partners are built |
| `data/ECA/Transport/maritime_edges.geojson` | Template for maritime edge structure |
| `data/ECA/Economic/mrio_BS_MC.csv` | Template for MRIO format |
