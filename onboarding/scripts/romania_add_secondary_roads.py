"""Add secondary roads (3 fine regions only) to the Romania road network.

raw L2 national roads + secondary-class edges from the L3 extraction clipped
to the 18 fine counties -> joint tnclean -> finalize -> new domestic
transport.gpkg (rail/ww/maritime layers carried over) ready for the
multimodal build and the TEN-T extension.
Run steps split so tnclean (slow) runs via CLI per KI-08.
"""
import sys
import geopandas as gpd
import pandas as pd

DATA = r"C:/Users/Celian/OneDrive/DisruptSC/transport/transnet/data-romania"
SPA = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Spatial"

step = sys.argv[1]

if step == "merge":
    l2 = gpd.read_file(DATA + "/Romania_raw.gpkg", layer="roads")
    l3 = gpd.read_file(DATA + "/Romania_raw_L3.gpkg", layer="roads")
    sec = l3[l3["class"] == "secondary"].copy()
    adm1 = gpd.read_file(SPA + "/sources/ROU_adm1.geojson")
    FINE = {"BIHOR","BISTRITA-NASAUD","CLUJ","MARAMURES","SATU MARE","SALAJ","BACAU","BOTOSANI","IASI",
            "NEAMT","SUCEAVA","VASLUI","BRAILA","BUZAU","CONSTANTA","GALATI","TULCEA","VRANCEA"}
    region = adm1[adm1.shapeName.isin(FINE)].union_all()
    sec = sec[sec.geometry.intersects(region)]
    print(f"L2 roads {len(l2)}, secondary in 3 regions {len(sec)} (of {len(l3)-len(l2)} secondary nationally)")
    comb = gpd.GeoDataFrame(pd.concat([l2, sec], ignore_index=True), crs=l2.crs)
    comb.to_file(DATA + "/Romania_raw_L2plus.gpkg", layer="roads", driver="GPKG")
    print(f"merged raw roads: {len(comb)} -> Romania_raw_L2plus.gpkg")

elif step == "assemble":
    import shutil
    tdir = r"C:/Users/Celian/OneDrive/DisruptSC/disrupt-sc-data/Romania/Transport"
    # new domestic gpkg: finalized new roads + carried-over other layers
    new_roads = gpd.read_file(DATA + "/Romania_roads_L2plus_final.gpkg", layer="roads")
    out = tdir + "/transport.gpkg"
    import os
    if os.path.exists(out):
        os.remove(out)
    new_roads.to_file(out, layer="roads", driver="GPKG")
    for layer in ("railways", "waterways", "maritime"):
        g = gpd.read_file(tdir + "/transport_domestic.gpkg", layer=layer)
        drop = [c for c in ("foreign", "country_code") if c in g.columns]
        g = g.drop(columns=drop)
        g.to_file(out, layer=layer, driver="GPKG")
    print("assembled domestic transport.gpkg:",
          {l: len(gpd.read_file(out, layer=l)) for l in ("roads","railways","waterways","maritime")})
