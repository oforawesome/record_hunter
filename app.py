import streamlit as st
import os
import json
import gkeepapi
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher

# --- 1. CONFIG & TOKENS ---
# Load local .env if not on Streamlit Cloud
load_dotenv()

def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

DISCOGS_TOKEN = get_secret("DISCOGS_TOKEN")
KEEP_EMAIL = get_secret("KEEP_EMAIL")
KEEP_PASSWORD = get_secret("KEEP_PASSWORD") # Reminder: Use a Google App Password
RECORDS_LIST_ID = "1V0jNBMmVbmMLlQzGu8rRbNk4s-cXBgWvY6wknPWIH35M7pC2ydqjTr5eEDMPjUk"

st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵", layout="wide")

# --- 2. KEEP API HUB ---
@st.cache_resource
def get_keep_client():
    """Authenticates with Google Keep once and reuses the session."""
    keep = gkeepapi.Keep()
    try:
        success = keep.login(KEEP_EMAIL, KEEP_PASSWORD)
        if success:
            return keep
    except Exception as e:
        st.error(f"Keep Login Failed: {e}")
    return None

def add_to_keep_list(album_text):
    """Adds an item to the specific 'Records' list and syncs."""
    keep = get_keep_client()
    if keep:
        glist = keep.get(RECORDS_LIST_ID)
        if glist:
            # Add as an unchecked item (False)
            glist.add(album_text, False)
            keep.sync()
            return True
    return False

# --- 3. HELPER FUNCTIONS ---
def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

# --- 4. DATA LOADING ---
try:
    with open('collection.json', 'r') as f:
        my_collection = json.load(f)
except FileNotFoundError:
    st.error("⚠️ collection.json not found. Please run your collector locally first!")
    st.stop()

# --- 5. USER INTERFACE ---
st.title("🎵 Record Hunter")
st.markdown("Auditing your Discogs collection against the 'Gold Standard'.")

artist_input = st.text_input("Enter Artist Name (e.g., Bruce Springsteen, The Cure):")

if artist_input:
    with st.spinner(f'Searching MusicBrainz for {artist_input}...'):
        official_studio_list = get_studio_albums(artist_input)
        my_artist_records = [r for r in my_collection if artist_input.lower() in r['artist'].lower()]

    if not my_artist_records and not official_studio_list:
        st.warning("No records found for that artist.")
    else:
        owned_titles = [r['title'] for r in my_artist_records]
        missing_studio = []

        for album_data in official_studio_list:
            studio_title = album_data['title']
            match = next((t for t in owned_titles if is_similar(studio_title, t)), None)
            if not match:
                missing_studio.append(album_data)

        # --- 6. DISPLAY RESULTS ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Owned (Full Collection)")
            sorted_owned = sorted(my_artist_records, key=lambda x: x.get('year', 0))
            for a in sorted_owned:
                y = a.get('year', '')
                st.write(f"- **{a['title']}** ({y})")

        with col2:
            st.header("❌ Missing (Studio Only)")
            sorted_missing = sorted(missing_studio, key=lambda x: str(x.get('year', '9999')))
            
            for m in sorted_missing:
                album_label = f"{artist_input} - {m['title']}"
                sub_col1, sub_col2 = st.columns([0.8, 0.2])
                
                with sub_col1:
                    st.write(f"**{m['title']}** ({m['year']})")
                
                with sub_col2:
                    # THE ADD BUTTON
                    if st.button("➕", key=album_label):
                        with st.spinner("Syncing to Keep..."):
                            if add_to_keep_list(album_label):
                                st.toast(f"Added {m['title']}!", icon="✅")
                            else:
                                st.error("Failed to add.")