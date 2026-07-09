import requests

DEFAULT_TIMEOUT = 8


def _get(base_url, path, params=None):
    resp = requests.get(f"{base_url}{path}", params=params, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def browse(base_url, uri=""):
    """Browse a single Volumio uri and return the raw navigation payload."""
    params = {"uri": uri} if uri else {}
    return _get(base_url, "/api/v1/browse", params)


def list_music_sources(base_url):
    """
    Return the top-level browsable items under Music Library
    (e.g. NAS, USB, INTERNAL, whatever mount points you have).
    """
    data = browse(base_url, "music-library")
    lists = data.get("navigation", {}).get("lists", [])
    sources = []
    for l in lists:
        sources.extend(l.get("items", []))
    return sources


def walk_albums(base_url, uri, breadcrumb=None, max_depth=6, _depth=0):
    """
    Recursively walk a Volumio browse uri.

    A folder counts as an "album" once its children are songs rather than
    more folders (i.e. we've hit the bottom of the Artist/Album hierarchy).
    Returns a flat list of dicts: {"artist", "album", "uri", "track_count"}.
    """
    breadcrumb = breadcrumb or []
    if _depth > max_depth:
        return []

    try:
        data = browse(base_url, uri)
    except requests.RequestException as e:
        print(f"--- ⚠️ Could not browse '{uri}': {e}")
        return []

    lists = data.get("navigation", {}).get("lists", [])
    items = []
    for l in lists:
        items.extend(l.get("items", []))

    songs = [i for i in items if i.get("type") == "song"]
    folders = [i for i in items if i.get("type") == "folder"]

    if songs and not folders:
        sample = songs[0]
        artist = sample.get("artist") or (breadcrumb[-2] if len(breadcrumb) >= 2 else "Unknown Artist")
        album = sample.get("album") or (breadcrumb[-1] if breadcrumb else uri.split("/")[-1])
        return [{
            "artist": artist,
            "album": album,
            "uri": uri,
            "track_count": len(songs),
        }]

    albums = []
    for f in folders:
        child_uri = f.get("uri")
        child_title = f.get("title", "")
        if not child_uri:
            continue
        albums.extend(
            walk_albums(base_url, child_uri, breadcrumb + [child_title], max_depth, _depth + 1)
        )
    return albums


def fetch_all_albums(base_url="http://volumio.local", roots=None):
    """
    Top-level convenience function. Discovers music sources (NAS, USB,
    INTERNAL...) and walks each one for albums.

    Pass `roots` (a list of uris, e.g. ["music-library/INTERNAL/Music"])
    to skip discovery and target specific mount points directly - useful
    if auto-discovery picks up sources you don't want scanned (Web Radio,
    Spotify, etc. are skipped automatically as they aren't "folder" type).
    """
    if roots is None:
        sources = list_music_sources(base_url)
        roots = [s["uri"] for s in sources if s.get("type") == "folder"]

    all_albums = []
    for root in roots:
        print(f"--- 📂 Scanning {root}...")
        all_albums.extend(walk_albums(base_url, root))

    seen = set()
    unique = []
    for a in all_albums:
        key = (a["artist"].lower().strip(), a["album"].lower().strip(), a["uri"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique
