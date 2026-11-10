"""Read a CLIMADA river-flood hazard (one event) without CLIMADA, check the v3 road footprint, write a small extract.

Made 10 Nov 2026 for Fig. 1 of the Cambodia paper (node E_dir): the depth behind the v3 footprint is the hazard file of
the GloFAS forecast of 27 Sep 2023 (Elisa Nobile's climada-disruptsc on the cluster). The cluster's climada_env no
longer loads (its libraries point to a home folder that is gone), so this reads the HDF5 with h5py and pickle and runs
in the dsc environment. The output grid is disrupt-sc-data/Cambodia/Hazard/glofas_fc20230927_depth.npz (see the
README there for provenance and the check).

Usage (cluster):
    python climada_depth.py \
        /projects/disruptsc/climada-disruptsc/output/Cambodia/flood_hazard/hazard-forecast/flood_hazard-2023/hazard_flood_2023-09-27.hdf5 \
        /projects/disruptsc/disrupt-sc_cambodia_v2/data/Cambodia/Transport/roads_edges_with_disruptions_v3.geojson \
        depth_20230927
writes depth_20230927_grid.npz and depth_20230927_edges.csv and prints the check.
"""
import hashlib
import pickle
import sys

import geopandas as gpd
import h5py
import numpy as np
from scipy.sparse import csr_matrix

HAZ, V3, OUT = sys.argv[1:4]
# JRC Asia road damage curve and Pregnolato disruption curve, as in climada-disruptsc/functions.py
DMG_X = np.array([0, 0.5, 1, 1.5, 2, 3, 4, 5, 30.])
DMG_Y = np.array([0, 0.21, 0.37, 0.60, 0.71, 0.81, 0.89, 0.97, 1.0])
DIS_X = np.array([0, 0.3, 0.5, 1, 1.5, 2, 5, 30.])
DIS_Y = np.array([0, 0, 1, 1, 1, 1, 1, 1.])

f = h5py.File(HAZ, "r")
c = f["centroids"]
items = [x.decode() for x in c["block0_items"][:]]
vals = pickle.loads(bytes(np.asarray(c["block0_values"][0])))
print("centroid block", items, vals.shape)
geom = vals[items.index("geometry")] if vals.shape[0] == len(items) else vals[:, items.index("geometry")]
lon = np.array([p.x for p in geom])
lat = np.array([p.y for p in geom])
n = lon.size
I = csr_matrix((f["intensity/data"][:], f["intensity/indices"][:], f["intensity/indptr"][:]), shape=(1, n))
depth = np.asarray(I.toarray()).ravel().astype("float32")
print("event", f["event_name"][:], "date", f["date"][:], "units", f["units"][:], "n", n, "nnz", I.nnz, "max", depth.max())
ux, uy = np.unique(lon), np.unique(lat)
dx, dy = np.median(np.diff(ux)), np.median(np.diff(uy))
print("grid", ux.size, uy.size, ux.size * uy.size == n, "dx", dx, "dy", dy, "lon", ux.min(), ux.max(), "lat", uy.min(), uy.max())
col = np.rint((lon - ux.min()) / dx).astype(int)
row = np.rint((uy.max() - lat) / dy).astype(int)
nx, ny = col.max() + 1, row.max() + 1
grid = np.zeros((ny, nx), dtype="float32")
grid[row, col] = depth
print("grid shape", grid.shape, "max dev lon", np.abs(ux.min() + col * dx - lon).max(), "lat", np.abs(uy.max() - row * dy - lat).max())
# The centroids' region_id and on_land are 0 / False everywhere in this file (checked 10 Nov 2026): no country mask here.


def cell_depth(x, y):
    j = np.rint((x - ux.min()) / dx).astype(int)
    i = np.rint((uy.max() - y) / dy).astype(int)
    ok = (i >= 0) & (i < ny) & (j >= 0) & (j < nx)
    out = np.zeros(x.size, dtype="float32")
    out[ok] = grid[i[ok], j[ok]]
    return out


roads = gpd.read_file(V3)
m = roads.to_crs(32648)
rows = []
for k, (rid, g, b) in enumerate(zip(roads["id"], m.geometry, roads["flood_disruption"])):
    L = g.length
    npt = max(int(np.ceil(L / 500.0)), 1) + 1
    pts = [g.interpolate(t) for t in np.linspace(0, L, npt)]
    ll = gpd.GeoSeries(pts, crs=32648).to_crs(4326)
    d = cell_depth(ll.x.to_numpy(), ll.y.to_numpy())
    dmg = np.interp(d, DMG_X, DMG_Y)
    dis = np.interp(d, DIS_X, DIS_Y)
    seg = L / 1000.0 / npt
    rows.append((rid, b, L / 1000.0, d.max(), dmg.max(), dis.max(), (dmg >= 0.5).sum() * seg, (d > 0).sum() * seg, npt))
import pandas as pd
t = pd.DataFrame(rows, columns=["id", "flood_disruption", "km", "depth_max", "dmg_max", "dis_max", "km_dmg50", "km_wet", "npts"])
hit = t["flood_disruption"].notna()
dam = t["dmg_max"] >= 0.5
print("edges", len(t), "v3", hit.sum(), "damaged (any basin)", dam.sum(), "v3 & damaged", (hit & dam).sum())
print("v3 km", round(t.loc[hit, "km"].sum(), 1), "v3 km_dmg50", round(t.loc[hit, "km_dmg50"].sum(), 1), "v3 km_wet", round(t.loc[hit, "km_wet"].sum(), 1))
print(t.loc[hit].sort_values(["flood_disruption", "id"]).round(3).to_string(index=False))
print("damaged but not v3:", len(t.loc[dam & ~hit]), "km", round(t.loc[dam & ~hit, "km"].sum(), 1))
t.to_csv(OUT + "_edges.csv", index=False)
# compact extract: the grid, north-up, cell-centre origin
np.savez_compressed(OUT + "_grid.npz", depth=grid, lon0=ux.min(), lat0=uy.max(), dx=dx, dy=dy)
for p in (HAZ, OUT + "_grid.npz", OUT + "_edges.csv"):
    print("sha256", hashlib.sha256(open(p, "rb").read()).hexdigest(), p)
