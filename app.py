import streamlit as st
import os
import discogs_client
from urllib.parse import quote_plus
from dotenv import load_dotenv
from cataloguer import get_studio_albums
from difflib import SequenceMatcher
from tasks_client import add_record_to_tasks

# --- 1. CONFIG & TOKENS ---
load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

DISCOGS_TOKEN = get_secret("DISCOGS_TOKEN")

st.set_page_config(page_title="Record Hunter NZ", page_icon="🎵", layout="wide")

# --- 2. HELPER FUNCTIONS ---
def fetch_discogs_collection():
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

def trademe_url(artist, album):
    query = quote_plus(f"{artist} {album}")
    return f"https://www.trademe.co.nz/a/marketplace/music-instruments/vinyl/lps-33-rpm/search?condition=used&search_string={query}"

def realgroovy_url(artist, album):
    query = quote_plus(f"{artist} {album}")
    return f"https://realgroovy.com/search?q={query}"

def marbecks_url(artist, album):
    clean_query = f"{artist.strip()} {album.strip()}"
    query_encoded = quote_plus(clean_query)
    return f"https://www.marbecks.co.nz/search/keyword/{query_encoded}"

def discogs_marketplace_url(artist, album):
    strict_query = f'"{artist.strip()}" "{album.strip()}"'
    base_url = "https://www.discogs.com/sell/list?"
    params = (
        f"q={quote_plus(strict_query)}"
        "&format=Vinyl"
        "&format_desc=Album"
        "&sort=price%2Casc"
    )
    return base_url + params

def is_similar(official_title, owned_string, threshold=0.8):
    off = str(official_title).lower().strip()
    own = str(owned_string).lower().strip()
    return (off in own) or (SequenceMatcher(None, off, own).ratio() > threshold)

# --- 3. DATA LOADING ---
if "my_collection" not in st.session_state:
    with st.spinner("Loading your Discogs collection..."):
        try:
            st.session_state.my_collection = fetch_discogs_collection()
        except Exception as e:
            st.error(f"Failed to load Discogs collection: {e}")
            st.session_state.my_collection = []

# --- 4. USER INTERFACE ---
st.title("🎵 Record Hunter")

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
st.caption(f"✅ {len(my_collection)} records loaded from Discogs.")

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

            for idx, m in enumerate(sorted_missing):
                album_label = f"{canonical_artist} - {m['title']} ({m['year']})"
                sub_col1, sub_col2, sub_col3, sub_col4, sub_col5, sub_col6 = st.columns([0.35, 0.13, 0.13, 0.13, 0.13, 0.13])

                with sub_col1:
                    st.write(f"**{m['title']}** ({m['year']})")

                with sub_col2:
                    tm_link = trademe_url(canonical_artist, m['title'])
                    st.link_button("🔍 TM", tm_link)

                with sub_col3:
                    rg_link = realgroovy_url(canonical_artist, m['title'])
                    st.link_button("🎵 RG", rg_link)

                with sub_col4:
                    mb_link = marbecks_url(canonical_artist, m['title'])
                    st.link_button("💿 MB", mb_link)

                with sub_col5:
                    dc_link = discogs_marketplace_url(canonical_artist, m['title'])
                    st.link_button("🏷️ DC", dc_link)

                with sub_col6:
                    if st.button("➕", key=f"{album_label}_{idx}"):
                        with st.spinner("Adding to Google Tasks..."):
                            if add_record_to_tasks(album_label, notes=tm_link):
                                st.toast(f"Added {m['title']}!", icon="✅")
                            else:
                                st.error("Failed to add.")