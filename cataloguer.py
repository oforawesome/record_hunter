import musicbrainzngs
import time  # <--- New import for pausing

# Use a specific user agent so MusicBrainz doesn't think you're a bot
musicbrainzngs.set_useragent("RecordHunter", "1.1", "your_email@example.com")

def get_studio_albums(artist_name):
    print(f"--- 🌐 Fetching official albums for {artist_name}...")
    
    try:
        # 1. Search for the artist
        result = musicbrainzngs.search_artists(artist=artist_name)
        if not result['artist-list']: 
            return []
        
        artist_id = result['artist-list'][0]['id']
        
        # 2. Add a tiny 1-second pause to be polite to the server
        time.sleep(1)
        
        # 3. Fetch the release groups
        groups = musicbrainzngs.browse_release_groups(artist=artist_id, release_type=['album'])
        
        final_titles = []
        for g in groups['release-group-list']:
            # STRICT FILTER: Must be 'Album' and have NO secondary types (No Live/Comp)
            if g.get('type') == 'Album' and not g.get('secondary-type-list'):
                final_titles.append(g['title'])
                
        return sorted(list(set(final_titles)))

    except Exception as e:
        print(f"⚠️ Network hiccup: {e}")
        print("--- 🔄 Retrying in 3 seconds...")
        time.sleep(3)
        return get_studio_albums(artist_name) # Try one more time