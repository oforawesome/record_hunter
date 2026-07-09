import json
from volumio_client import fetch_all_albums

# IMPORTANT: This only works when run on the same network as your Pi.
# It will NOT work from Streamlit Cloud - mDNS names like volumio.local
# aren't reachable off your LAN. Run this locally, same as collector.py
# for Discogs, then commit the resulting volumio_collection.json.
#
# If volumio.local doesn't resolve on your machine, swap in the Pi's
# IP address instead, e.g. "http://192.168.1.50"
VOLUMIO_URL = "http://volumio.local"


def refresh_volumio_collection():
    print(f"--- 📥 Connecting to Volumio at {VOLUMIO_URL}...")
    albums = fetch_all_albums(VOLUMIO_URL)
    print(f"--- 🔍 Found {len(albums)} albums.")

    with open("volumio_collection.json", "w") as f:
        json.dump(albums, f, indent=2)

    print(f"--- ✅ SUCCESS! Saved {len(albums)} albums to volumio_collection.json")


# THE START BUTTON (Crucial!)
if __name__ == "__main__":
    refresh_volumio_collection()
