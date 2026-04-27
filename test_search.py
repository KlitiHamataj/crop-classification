from pystac_client import Client
from collections import Counter
from config import ROI_BBOX, DATE_RANGE, MAX_CLOUD, BANDS

catalog = Client.open("https://catalogue.dataspace.copernicus.eu/stac")

search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=ROI_BBOX,
    datetime=DATE_RANGE,
    query={"eo:cloud_cover": {"lt": MAX_CLOUD}},
    max_items=500
)

items = list(search.items())
print(f"✅ Found {len(items)} scenes")

# Summary by month
months = Counter(item.datetime.strftime("%Y-%m") for item in items)
print("\nScenes per month:")
for m in sorted(months):
    print(f"  {m}: {months[m]} scenes")

# Check available bands in first scene
print(f"\nAvailable assets in first scene:")
for band in BANDS:
    found = band in items[0].assets
    print(f"  {band}: {'✅' if found else '❌ missing'}")
    
# # Print actual asset keys from first scene
# print("\nActual asset keys in first scene:")
# for key in items[0].assets.keys():
#     print(f"  {key}")