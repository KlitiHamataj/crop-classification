import requests
from config import COPERNICUS_USER, COPERNICUS_PASS

resp = requests.post(
    "https://identity.dataspace.copernicus.eu/auth/realms/CDSE"
    "/protocol/openid-connect/token",
    data={
        "client_id"  : "cdse-public",
        "grant_type" : "password",
        "username"   : COPERNICUS_USER,
        "password"   : COPERNICUS_PASS,
    },
    timeout=30
)

if resp.status_code == 200:
    token = resp.json()["access_token"]
    print("✅ Authentication successful!")
    print(f"Token (first 50 chars): {token[:50]}...")
else:
    print(f"❌ Authentication failed: {resp.status_code}")
    print(resp.json())