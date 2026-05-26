import os
import requests
from dotenv import load_dotenv

load_dotenv()

ors_key = os.getenv('OPENROUTES_API_KEY')
liq_key = os.getenv('LOCATIONIQ_API_KEY')

def test_profile(profile_name):
    url = f"https://api.openrouteservice.org/v2/directions/{profile_name}/geojson"
    headers = {
        "Authorization": ors_key,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [[-80.1918, 25.7617], [-80.1373, 26.1224]],
        "units": "mi"
    }
    print(f"\nTesting ORS profile: {profile_name}")
    try:
        r = requests.post(url, json=body, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if ors_key:
    test_profile("driving-hgv")
    test_profile("driving-car")
else:
    print("ORS Key missing.")

if liq_key:
    print("\nTesting LocationIQ...")
    url = f"https://us1.locationiq.com/v1/search.php?key={liq_key}&q=Miami&format=json"
    try:
        r = requests.get(url)
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")
