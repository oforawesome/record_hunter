import streamlit as st
import os
import json
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher

# --- 1. CONFIG & TOKENS ---
if "DISCOGS_TOKEN" in st.secrets:
    token = st.secrets["DISCOGS_TOKEN"]
else:
    load_dotenv()
    token = os.getenv("DISCOGS_TOKEN")

st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵", layout="wide")

# --- 2. HELPER FUNCTIONS ---
def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

# --- 3. DATA LOADING ---
try:
    with open('collection.json', 'r') as f:
        my_collection = json.load(f)
except FileNotFoundError:
    st.error("⚠️ collection.json not found. Please run your collector locally first!")
    st.stop()

# --- 4. USER INTERFACE ---
st.title("🎵 Record Hunter")
st.markdown("Auditing your Discogs collection against the 'Gold Standard'.")

artist_input = st.text_input("Enter Artist Name (e.g., Bruce Springsteen, The Cure):")

if artist_input:
    with st.spinner(f'Searching MusicBrainz for {artist_input}...'):
        # Get the "Gold Standard" from MusicBrainz (Returns list of dicts: title/year)
        official_studio_list = get_studio_albums(artist_input)
        
        # Get everything you own by this artist from your local JSON
        my_artist_records = [r for r in my_collection if artist_input.lower() in r['artist'].lower()]

    if not my_artist_records and not official_studio_list:
        st.warning("No records found for that artist.")
    else:
        # --- 5. THE AUDIT LOGIC ---
        owned_titles = [r['title'] for r in my_artist_records]
        missing_studio = []

        for album_data in official_studio_list:
            studio_title = album_data['title']
            # Check if this official album exists in our 'owned' list
            match = next((t for t in owned_titles if is_similar(studio_title, t)), None)
            
            if not match:
                missing_studio.append(album_data)

        # --- 6. DISPLAY RESULTS ---
        # Note: These columns are OUTSIDE the loop so they only appear once!
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Owned (Full Collection)")
            # Sort owned records by year (defaulting to 0 if missing)
            sorted_owned = sorted(my_artist_records, key=lambda x: x.get('year', 0))
            if not sorted_owned:
                st.write("No records owned by this artist.")
            for a in sorted_owned:
                year = a.get('year')
                year_display = f"({year})" if year and year != 0 else ""
                st.write(f"- **{a['title']}** {year_display}")

        with col2:
            st.header("❌ Missing (Studio Only)")
            # Sort missing records by year key to avoid dictionary comparison errors
            sorted_missing = sorted(missing_studio, key=lambda x: str(x.get('year', '9999')))
            
            if not sorted_missing:
                st.success("You have all the studio albums! Collection complete. 🎉")
            
            for m in sorted_missing:
                m_title = m['title']
                m_year = m['year']
                
                # Create Trade Me search link
                q = f"{artist_input} {m_title} vinyl".replace(' ', '+')
                link = f"https://www.trademe.co.nz/marketplace/music-instruments/vinyl/search?searchstring={q}"
                
                st.markdown(f"- **{m_title}** ({m_year}) [🛒]({link})")