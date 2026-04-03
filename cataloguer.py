import musicbrainzngs
import time  # <--- New import for pausing

# Use a specific user agent so MusicBrainz doesn't think you're a bot
musicbrainzngs.set_useragent("RecordHunter", "1.1", "your_email@example.com")

def get_studio_albums(artist_name):
    # ... (Your existing setup code: musicbrainzngs.search_artists, etc.)
    
    # After you get the release_groups from MusicBrainz:
    albums = []
    for group in release_groups:
        # We only want "Studio" albums (not live or compilations)
        if 'type' in group and group['type'] == 'Album':
            # 1. Get the Title
            title = group['title']
            
            # 2. Get the Year (MusicBrainz calls this 'first-release-date')
            # It usually looks like "1975-08-25", so we take the first 4 characters
            release_date = group.get('first-release-date', '')
            year = release_date[:4] if release_date else "N/A"
            
            # 3. Save as a dictionary instead of just a string
            albums.append({
                "title": title,
                "year": year
            })
            
    return albums

    except Exception as e:
        print(f"⚠️ Network hiccup: {e}")
        print("--- 🔄 Retrying in 3 seconds...")
        time.sleep(3)
        return get_studio_albums(artist_name) # Try one more time