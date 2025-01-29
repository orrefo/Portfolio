import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st

# Spotify API credentials
CLIENT_ID = '99d8401365114e2da8eb836284bc8be0'
CLIENT_SECRET = '91c15af888db425083ed55e374fadff6'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

@st.cache_data
def get_artist_image(artist_name):
    """Fetch artist image from Spotify API."""
    results = sp.search(q='artist:' + artist_name, type='artist')
    items = results.get('artists', {}).get('items', [])
    if items:
        return items[0].get('images', [])[0].get('url')
    return None
