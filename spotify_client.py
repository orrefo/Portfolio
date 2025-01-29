import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st


# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=st.secrets["CLIENT_ID"],
    client_secret=st.secrets["CLIENT_SECRET"]
))

@st.cache_data
def get_artist_image(artist_name):
    """Fetch artist image from Spotify API."""
    results = sp.search(q='artist:' + artist_name, type='artist')
    items = results.get('artists', {}).get('items', [])
    if items:
        return items[0].get('images', [])[0].get('url')
    return None
