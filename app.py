import streamlit as st
import os
import json
import discogs_client
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher
from tasks_client import add_record_to_tasks

# --- 1. CONFIG & TOKENS ---
load_dotenv()

def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

DISCOGS_TOKEN = get_secret("DISCOGS_TOKEN")

st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵", layout="wide")

# --- 2. HELPER FUNCTIONS ---
def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

def fetch_discogs_collection():
    """Pull the latest collection from Discogs and return as a list."""
    client = discogs_client.Client('RecordHunter/1.0', user_token=DISCOGS_TOKEN)
    user = client.identity()
    collection = user.collection_folders[0].releases
    collection_list = []
    for item in collection:
        release = item.release
        collection_list.append({
            "artist": release.artists[0].name,
            "title": release.title,
            "year": getattr(release, 'year', 0)
        })
    return collection_list

# --- 3. DATA LOADING ---
# Try loading from session state first, then fall back to collection.json
if "my_collection" not in st.session_state:
    try:
        with open('collection.json', 'r') as f:
            st.session_state.my_collection = json.load(f)
    except FileNotFoundError:
        st.session_state.my_collection = []

# --- 4. USER INTERFACE ---
st.title("🎵 Record Hunter")

# --- SYNC BUTTON ---
col_title, col_sync = st.columns([0.85, 0.15])
with col_title:
    st.markdown("Auditing your Discogs collection against the 'Gold Standard'.")
with col_sync:
    if st.button("🔄 Sync Collection"):
        with st.spinner("Fetching from Discogs..."):
            try:
                st.session_state.my_collection = fetch_discogs_collection()
                st.toast(f"Synced {len(st.session_state.my_collection)} records!", icon="✅")
            except Exception as e:
                st.error(f"Sync failed: {e}")

if not st.session_state.my_collection:
    st.warning("⚠️ No collection loaded. Hit 🔄 Sync Collection to fetch from Discogs.")
    st.stop()

my_collection = st.session_state.my_collection

# --- 5. ARTIST SEARCH ---
artist_input = st.text_input("Enter Artist Name (e.g., Bruce Springsteen, The Cure):")

if artist_input:
    with st.spinner(f'Searching MusicBrainz for {artist_input}...'):
        official_studio_list, canonical_artist = get_studio_albums(artist_input)

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
                album_label = f"{canonical_artist} - {m['title']} ({m['year']})"
                sub_col1, sub_col2 = st.columns([0.8, 0.2])

                with sub_col1:
                    st.write(f"**{m['title']}** ({m['year']})")

                with sub_col2:
                    if st.button("➕", key=album_label):
                        with st.spinner("Adding to Google Tasks..."):
                            if add_record_to_tasks(album_label):
                                st.toast(f"Added {m['title']}!", icon="✅")
                            else:
                                st.error("Failed to add.")
