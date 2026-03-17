"""Inspect the Global2 maritime network for edges in/near the Gulf region."""
import json

with open(r"C:\Users\Celian\OneDrive\DisruptSC\disrupt-sc\data\Global2\Transport\maritime_edges.geojson") as f:
    data = json.load(f)

print(f"Total features: {len(data['features'])}")
print(f"Properties keys: {list(data['features'][0]['properties'].keys())}")

# Gulf bounding box: lon 30-70, lat 5-35 (generous to capture Indian Ocean approaches)
gulf_bbox = (30, 5, 70, 35)

def coords_in_bbox(coords, bbox):
    lon_min, lat_min, lon_max, lat_max = bbox
    for c in coords:
        lon, lat = c[0], c[1]
        if lon_min <= lon <= lon_max and lat_min <= lat <= lat_max:
            return True
    return False

gulf_edges = []
for i, feat in enumerate(data['features']):
    coords = feat['geometry']['coordinates']
    if coords_in_bbox(coords, gulf_bbox):
        props = feat['properties']
        gulf_edges.append((i, props['km'], coords))

print(f"\nEdges with at least one vertex in Gulf bbox (lon 30-70, lat 5-35): {len(gulf_edges)}")
print()
for idx, km, coords in gulf_edges:
    start = coords[0]
    end = coords[-1]
    print(f"  Feature {idx:>3}: ({start[0]:8.2f}, {start[1]:7.2f}) -> ({end[0]:8.2f}, {end[1]:7.2f})  km={km:.0f}")

# Also check narrower Gulf bbox (lon 47-60, lat 22-30) for Persian Gulf specifically
pg_bbox = (47, 22, 60, 30)
pg_edges = []
for i, feat in enumerate(data['features']):
    coords = feat['geometry']['coordinates']
    if coords_in_bbox(coords, pg_bbox):
        props = feat['properties']
        pg_edges.append((i, props['km'], coords))

print(f"\nEdges with vertex inside Persian Gulf (lon 47-60, lat 22-30): {len(pg_edges)}")
for idx, km, coords in pg_edges:
    start = coords[0]
    end = coords[-1]
    print(f"  Feature {idx:>3}: ({start[0]:8.2f}, {start[1]:7.2f}) -> ({end[0]:8.2f}, {end[1]:7.2f})  km={km:.0f}")
