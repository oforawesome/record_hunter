import os
import json
import streamlit as st  # <--- MUST be before you use st.secrets
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher

# NOW you can run the logic
if "DISCOGS_TOKEN" in st.secrets:
    token = st.secrets["DISCOGS_TOKEN"]
else:
    load_dotenv()
    token = os.getenv("DISCOGS_TOKEN")

# --- UI SETUP ---
st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵")
st.title("🎵 Record Hunter")
st.markdown("Auditing your Discogs collection against the 'Gold Standard'.")

# --- LOGIC ---
def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

# --- THE APP ---
try:
    with open('collection.json', 'r') as f:
        my_collection = json.load(f)
except FileNotFoundError:
    st.error("⚠️ collection.json not found. Please run your collector locally first!")
    st.stop()

artist_input = st.text_input("Enter Artist Name (e.g., The Cure, U2):")

if artist_input:
    with st.spinner(f'Searching MusicBrainz for {artist_input}...'):
        # 1. Get the "Gold Standard" (Studio Albums only) from MusicBrainz
        official_studio_list = get_studio_albums(artist_input)
        
        # 2. Get EVERYTHING you own by this artist (Live, Compilations, Studio)
        # We don't filter this list by 'type' yet—we want to show it all!
        my_artist_records = [r for r in my_collection if artist_input.lower() in r['artist'].lower()]

    if not my_artist_records and not official_studio_list:
        st.warning("No records found for that artist.")
    else:
        # --- THE AUDIT LOGIC ---
        # We check which of the OFFICIAL studio albums are missing from your total list
        owned_titles = [r['title'] for r in my_artist_records]
        missing_studio = []


    for album_data in official_studio_list:
        studio_title = album_data['title']
        studio_year = album_data['year']
    
        # Use studio_title for the fuzzy matching
        match = next((t for t in owned_titles if is_similar(studio_title, t)), None)
    
        if not match:
            missing_studio.append(album_data) # Keep the whole dictionary for the display!

        # --- DISPLAY RESULTS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Owned (Full Collection)")
            # Sort your full owned list by year
            sorted_owned = sorted(my_artist_records, key=lambda x: x.get('year', 0))
            for a in sorted_owned:
                year = a.get('year')
                year_display = f"({year})" if year and year != 0 else ""
                st.write(f"- **{a['title']}** {year_display}")

        with col2:
            st.header("❌ Missing (Studio Only)")
            for m in sorted(missing_studio):
                q = f"{artist_input} {m} vinyl"
                link = f"https://www.trademe.co.nz/marketplace/music-instruments/vinyl/search?searchstring={q.replace(' ', '+')}"
                st.markdown(f"- {m} [🛒]({link})")