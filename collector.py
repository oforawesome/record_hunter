import os
import json
import discogs_client
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCOGS_TOKEN")
client = discogs_client.Client('MyVinylAuditor/1.0', user_token=token)

def refresh_collection():
    print("--- 📥 Accessing Discogs API...")
    user = client.identity()
    
    # This is the folder for "All Music"
    collection = user.collection_folders[0].releases
    
    collection_list = []
    print(f"--- 🔍 Found {len(collection)} records. Starting download...")

    for item in collection:
        release = item.release
        
        # Grab the artist name safely
        artist = release.artists[0].name
        title = release.title
        
        # Create the searchable string: "U2 - War"
        entry = f"{artist} - {title}"
        collection_list.append(entry)
        
        # Print every 50th record so you know it's working without spamming the screen
        if len(collection_list) % 50 == 0:
            print(f"--- 📦 Processed {len(collection_list)} records...")

    # Save to the JSON file
    with open('collection.json', 'w') as f:
        json.dump(collection_list, f)
        
    print(f"--- ✅ SUCCESS! Saved {len(collection_list)} records to collection.json")

# THE START BUTTON (Crucial!)
if __name__ == "__main__":
    refresh_collection()