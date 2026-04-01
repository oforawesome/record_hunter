import json
from difflib import SequenceMatcher
from cataloguer import get_studio_albums

def is_similar(official_title, owned_string, threshold=0.8):
    """
    Improved matching: Checks if the official title exists inside 
    the 'Artist - Title' string from your Discogs.
    """
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    
    # 1. Direct Containment (Fixes "War" matching "U2 - War")
    if off in own:
        return True
        
    # 2. Fuzzy Ratio (Handles "The Joshua Tree" vs "Joshua Tree")
    return SequenceMatcher(None, off, own).ratio() > threshold

def run_audit():
    # 1. Load the local shelf
    print("--- 📂 Loading your local collection...")
    try:
        with open('collection.json', 'r') as f:
            my_collection = json.load(f)
    except FileNotFoundError:
        return print("❌ Error: collection.json not found! Run collector.py first.")

    artist_input = input("\n🎵 Artist to audit (e.g., U2): ")
    
    # 2. Get the "Gold Standard" list from MusicBrainz
    official_studio_list = get_studio_albums(artist_input)

    # 3. Filter your shelf for records by this artist
    my_artist_records = [r for r in my_collection if artist_input.lower() in r.lower()]

    owned_studio = []
    missing_studio = []
    owned_extras = []

    # 4. MATCHING LOGIC
    # We loop through the official list and see if you own them
    for studio_album in official_studio_list:
        match = next((r for r in my_artist_records if is_similar(studio_album, r)), None)
        if match:
            owned_studio.append(match)
        else:
            missing_studio.append(studio_album)

    # 5. EXTRA FINDER
    # Identify records you own that aren't part of the core studio list
    for r in my_artist_records:
        if not any(is_similar(s, r) for s in official_studio_list):
            owned_extras.append(r)

    # --- THE FINAL REPORT ---
    print("\n" + "="*40)
    print(f"📊 {artist_input.upper()} AUDIT REPORT")
    print("="*40)
    
    print(f"✅ OWNED STUDIO ALBUMS ({len(owned_studio)}):")
    if not owned_studio:
        print("  (None found)")
    else:
        for a in sorted(owned_studio):
            print(f"  - {a}")

    if owned_extras:
        print(f"\n🎸 OWNED EXTRAS (Live/EP/Comp) ({len(owned_extras)}):")
        for e in sorted(owned_extras):
            print(f"  - {e}")

    print(f"\n❌ MISSING STUDIO ALBUMS ({len(missing_studio)}):")
    if not missing_studio:
        print("  🎉 Collection Complete!")
    else:
        for m in sorted(missing_studio):
            print(f"  - {m}")
    print("="*40)

if __name__ == "__main__":
    run_audit()