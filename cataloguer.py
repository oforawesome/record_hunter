import musicbrainzngs
import time

# Setup
musicbrainzngs.set_useragent("RecordHunter", "1.1", "your_email@example.com")

def get_studio_albums(artist_name):
    try:
        # 1. Search for the artist
        search = musicbrainzngs.search_artists(artist=artist_name)
        if not search['artist-list']:
            return []
        
        artist_id = search['artist-list'][0]['id']
        
        # 2. Get their release groups
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