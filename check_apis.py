import os
import requests
from dotenv import load_dotenv

load_dotenv()

ors_key = os.getenv('OPENROUTES_API_KEY')
liq_key = os.getenv('LOCATIONIQ_API_KEY')

print(f"Checking keys...")

if ors_key:
    url = "https://api.openrouteservice.org/v2/directions/driving-hgv/geojson"
    headers = {
        "Authorization": ors_key,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [[-80.1918, 25.7617], [-80.1373, 26.1224]], # Miami to Ft Lauderdale
        "units": "mi"
    }
    try:
        r = requests.post(url, json=body, headers=headers)
        print(f"ORS Status: {r.status_code}")
        if r.status_code == 200:
            print("ORS: Working correctly.")
        elif r.status_code == 429:
            print("ORS: Rate limit exceeded.")
            print(f"Response: {r.text}")
        elif r.status_code == 403:
            print("ORS: Key invalid or forbidden.")
            print(f"Response: {r.text}")
        else:
            print(f"ORS unexpected status: {r.text}")
    except Exception as e:
        print(f"ORS Error: {e}")
else:
    print("ORS Key missing.")

if liq_key:
    url = f"https://us1.locationiq.com/v1/search.php?key={liq_key}&q=Miami&format=json"
    try:
        r = requests.get(url)
        print(f"LocationIQ Status: {r.status_code}")
        if r.status_code == 429:
            print("LocationIQ: Rate limit exceeded (likely 2 req/sec or daily limit).")
    except Exception as e:
        print(f"LocationIQ Error: {e}")
else:
    print("LocationIQ Key missing.")
