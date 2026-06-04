import streamlit as st
import os
import discogs_client
import gkeepapi
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher

# --- 1. CONFIG & TOKENS ---
load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

DISCOGS_TOKEN = get_secret("DISCOGS_TOKEN")
KEEP_EMAIL = get_secret("KEEP_EMAIL")
KEEP_PASSWORD = get_secret("KEEP_PASSWORD")

st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵", layout="wide")

# --- 2. DISCOGS COLLECTION (live, cached per session) ---
@st.cache_data(show_spinner="Loading your Discogs collection...")
def load_collection():
    try:
        client = discogs_client.Client('RecordHunterNZ/1.0', user_token=DISCOGS_TOKEN)
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
    except Exception as e:
        st.error(f"Failed to load Discogs collection: {e}")
        return []

# --- 3. KEEP API ---
@st.cache_resource
def get_keep_client():
    keep = gkeepapi.Keep()
    try:
        email = get_secret("KEEP_EMAIL").strip()
        password = get_secret("KEEP_PASSWORD").strip()
        success = keep.authenticate(email, password)
        if success:
            return keep
    except gkeepapi.exception.LoginException:
        st.error("Invalid Credentials. Check your App Password.")
    except Exception as e:
        st.error(f"Google Keep connection error: {e}")
    return None

def add_to_keep_list(album_text):
    keep = get_keep_client()
    if keep:
        for g in keep.all():
            if g.title == "Records" and isinstance(g, gkeepapi.node.List):
                g.add(album_text, False)
                keep.sync()
                return True
    return False

# --- 4. HELPERS ---
def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

# --- 5. UI ---
st.title("🎵 Record Hunter")
st.markdown("Auditing your Discogs collection against the 'Gold Standard'.")

st.write("DEBUG: starting collection load...")
my_collection = load_collection()
st.write(f"DEBUG: load complete, {len(my_collection)} records")

if not my_collection:
    st.warning("Could not load your Discogs collection. Check your DISCOGS_TOKEN.")
    st.stop()

st.caption(f"✅ {len(my_collection)} records loaded from Discogs.")

artist_input = st.text_input("Enter Artist Name (e.g., Bruce Springsteen, The Cure):")

if artist_input:
    with st.spinner(f'Searching MusicBrainz for {artist_input}...'):
        official_studio_list, canonical_name = get_studio_albums(artist_input)

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

        col1, col2 = st.columns(2)

        with col1:
            st.header("✅ Owned (Full Collection)")
            sorted_owned = sorted(my_artist_records, key=lambda x: x.get('year', 0))
            for a in sorted_owned:
                st.write(f"- **{a['title']}** ({a.get('year', '')})")

        with col2:
            st.header("❌ Missing (Studio Only)")
            sorted_missing = sorted(missing_studio, key=lambda x: str(x.get('year', '9999')))
            for m in sorted_missing:
                album_label = f"{artist_input} - {m['title']}"
                sub_col1, sub_col2 = st.columns([0.8, 0.2])
                with sub_col1:
                    st.write(f"**{m['title']}** ({m['year']})")
                with sub_col2:
                    if st.button("➕", key=album_label):
                        with st.spinner("Syncing to Keep..."):
                            if add_to_keep_list(album_label):
                                st.toast(f"Added {m['title']}!", icon="✅")
                            else:
                                st.error("Failed to add.")