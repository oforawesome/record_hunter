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
    if key in st.secrets:
        return st.secrets[key]
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
        st.error(f"Failed to