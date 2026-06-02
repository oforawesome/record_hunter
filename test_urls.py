from urllib.parse import quote_plus

def marbecks_url(artist, album):
    """Builds a reliable Marbecks URL without the page index cache bug."""
    clean_query = f"{artist.strip()} {album.strip()}"
    return f"https://www.marbecks.co.nz/search/keyword/{quote_plus(clean_query)}"

def discogs_marketplace_url(artist, album):
    """
    Builds a direct link to the Discogs Marketplace.
    Uses literal phrase quotes to force matches on BOTH the artist 
    and album title, sorting by lowest price vinyl.
    """
    # Wrapping both fields in literal quotes eliminates messy fuzzy matches
    strict_query = f'"{artist.strip()}" "{album.strip()}"'
    
    base_url = "https://www.discogs.com/sell/list?"
    params = (
        f"q={quote_plus(strict_query)}"
        "&format=Vinyl"       # Restricts marketplace items to Vinyl
        "&sort=price%2Casc"   # Sorts by price: Low to High
    )
    return base_url + params

# --- RUN THE TEST CASES ---
test_artist = "The Cure"
test_album = "Kiss Me Kiss Me Kiss Me"

print("\n=======================================")
print(f" TESTING FOR: {test_artist} - {test_album}")
print("=======================================")

print(f"\n[Marbecks URL]:\n{marbecks_url(test_artist, test_album)}")
print(f"\n[Discogs Marketplace (Cheapest Vinyl - No Compilations)]:\n{discogs_marketplace_url(test_artist, test_album)}")

print("\n=======================================\n")
