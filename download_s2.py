import boto3, time, re
from io import BytesIO
from tqdm import tqdm
from botocore.client import Config
from pystac_client import Client
from azure.storage.blob import BlobServiceClient
from config import *

# ── Copernicus S3 client ───────────────────────────────────────────────────
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url        = "https://eodata.dataspace.copernicus.eu",
        aws_access_key_id   = S3_ACCESS_KEY,
        aws_secret_access_key = S3_SECRET_KEY,
        config              = Config(signature_version="s3v4"),
        region_name         = "default"
    )

# ── Azure Blob client ──────────────────────────────────────────────────────
def get_container_client():
    conn = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={STORAGE_ACCOUNT};"
        f"AccountKey={STORAGE_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    return BlobServiceClient.from_connection_string(conn).get_container_client(CONTAINER_NAME)

def blob_exists(cc, blob_name):
    try:
        cc.get_blob_client(blob_name).get_blob_properties()
        return True
    except:
        return False

# ── Download one band via S3 and upload to Azure Blob ─────────────────────
def download_band(item, band, s3, cc):
    asset = item.assets.get(band)
    if not asset:
        return "missing"

    date_str  = item.datetime.strftime("%Y%m%d")
    tile      = item.properties.get("s2:mgrs_tile", "XX")
    blob_path = f"raw/{tile}/{date_str}_{band}.tif"

    if blob_exists(cc, blob_path):
        return "skipped"

    # Convert s3://eodata/path/to/file.jp2 → bucket=eodata, key=path/to/file.jp2
    s3_path = asset.href  # s3://eodata/Sentinel-2/...
    s3_path = s3_path.replace("s3://eodata/", "")
    bucket  = "eodata"

    try:
        obj      = s3.get_object(Bucket=bucket, Key=s3_path)
        data     = BytesIO(obj["Body"].read())
        cc.get_blob_client(blob_path).upload_blob(data, overwrite=True)
        return "ok"
    except Exception as e:
        return f"error_{str(e)[:50]}"

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("Connecting to Copernicus S3...")
    s3 = get_s3_client()
    cc = get_container_client()

    print("Searching scenes...")
    catalog = Client.open("https://catalogue.dataspace.copernicus.eu/stac")
    search  = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=ROI_BBOX,
        datetime=DATE_RANGE,
        query={"eo:cloud_cover": {"lt": MAX_CLOUD}},
        max_items=500
    )
    items = list(search.items())
    print(f"Found {len(items)} scenes × {len(BANDS)} bands = {len(items)*len(BANDS)} files\n")

    done = skipped = errors = 0
    total = len(items) * len(BANDS)

    with tqdm(total=total, unit="band") as pbar:
        for item in items:
            date_str = item.datetime.strftime("%Y-%m-%d")
            cloud    = item.properties.get("eo:cloud_cover", "?")
            tile     = item.properties.get("s2:mgrs_tile", "XX")
            tqdm.write(f"Scene: {date_str}  tile={tile}  cloud={cloud}%")

            for band in BANDS:
                result = download_band(item, band, s3, cc)

                if result == "ok":
                    done += 1
                elif result == "skipped":
                    skipped += 1
                else:
                    errors += 1
                    tqdm.write(f"  {band}: {result}")

                pbar.set_postfix(done=done, skipped=skipped, errors=errors)
                pbar.update(1)

            time.sleep(0.2)

    print(f"\n{'='*50}")
    print(f"   Done!")
    print(f"   Uploaded : {done}")
    print(f"   Skipped  : {skipped}")
    print(f"   Errors   : {errors}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()