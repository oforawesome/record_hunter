import musicbrainzngs
import time

# Tell MusicBrainz who is calling
musicbrainzngs.set_useragent("RecordHunter", "1.1", "your_email@example.com")

def get_studio_albums(artist_name):
    try:
        # Everything from here down to 'return' is INDENTED 4 spaces
        # 1. Find the artist
        search_results = musicbrainzngs.search_artists(artist=artist_name)
        if not search_results['artist-list']:
            return []
            
        artist_id = search_results['artist-list'][0]['id']
        
        # 2. Get the albums
        result = musicbrainzngs.get_artist_by_id(artist_id, includes=["release-groups"])
        release_groups = result['artist']['release-group-list']
        
        albums = []
        for group in release_groups:
            # We want Studio Albums (Primary type 'Album', no secondary types like 'Live')
            p_type = group.get('primary-type', '')
            s_types = group.get('secondary-type-list', [])
            
            if p_type == 'Album' and not s_types:
                title = group['title']
                release_date = group.get('first-release-date', '')
                year = release_date[:4] if release_date else "N/A"
                
                albums.append({
                    "title": title,
                    "year": year
                })
        
        return albums

    except Exception as e:
        # This 'except' lines up vertically with the 'try'
        print(f"⚠️ MusicBrainz Error: {e}")
        return []