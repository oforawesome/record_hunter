import musicbrainzngs
from difflib import SequenceMatcher

# Setup
musicbrainzngs.set_useragent("RecordHunter", "1.1", "your_email@example.com")

def _name_match(input_name, result_name):
    """Check if the result name closely matches what the user typed."""
    a = input_name.lower().strip()
    b = result_name.lower().strip()
    # Exact match or very high similarity
    return a == b or SequenceMatcher(None, a, b).ratio() > 0.85

def get_studio_albums(artist_name):
    try:
        # 1. Search for the artist
        search = musicbrainzngs.search_artists(artist=artist_name)
        if not search['artist-list']:
            return []

        # 2. Find the best matching artist by name (not just first result)
        artist_id = None
        for artist in search['artist-list']:
            if _name_match(artist_name, artist.get('name', '')):
                artist_id = artist['id']
                break

        if not artist_id:
            return []

        # 3. Get their release groups
        data = musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"])
        groups = data['artist']['release-group-list']

        albums = []
        for g in groups:
            # Filter for Studio Albums ONLY
            p_type = g.get('primary-type', '')
            s_types = g.get('secondary-type-list', [])
            if p_type == 'Album' and not s_types:
                albums.append({
                    "title": g['title'],
                    "year": g.get('first-release-date', 'N/A')[:4]
                })

        return albums

    except Exception as e:
        print(f"Error: {e}")
        return []
