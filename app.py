import os
import streamlit as st

# Check if we are in the cloud (Streamlit) or local (.env)
if "DISCOGS_TOKEN" in st.secrets:
    token = st.secrets["DISCOGS_TOKEN"]
else:
    # Fallback for your local MacBook testing
    from dotenv import load_dotenv
    load_dotenv()
    token = os.getenv("DISCOGS_TOKEN")
import json
from cataloguer import get_studio_albums
from difflib import SequenceMatcher

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
        official_studio_list = get_studio_albums(artist_input)
        my_artist_records = [r for r in my_collection if artist_input.lower() in r.lower()]

    if not official_studio_list:
        st.warning("No studio albums found for that artist.")
    else:
        owned_studio = []
        missing_studio = []

        for studio_album in official_studio_list:
            match = next((r for r in my_artist_records if is_similar(studio_album, r)), None)
            if match:
                owned_studio.append(match)
                my_artist_records.remove(match)
            else:
                missing_studio.append(studio_album)

        # --- DISPLAY RESULTS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Owned")
            for a in sorted(owned_studio):
                st.write(f"- {a}")

        with col2:
            st.header("❌ Missing")
            for m in sorted(missing_studio):
                # Trade Me Link Button!
                q = f"{artist_input} {m} vinyl"
                link = f"https://www.trademe.co.nz/marketplace/music-instruments/vinyl/search?searchstring={q.replace(' ', '+')}"
                st.markdown(f"- {m} [🛒]({link})")