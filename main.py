import streamlit as st
from data_loader import load_data
from navigation import render_sidebar
from landing_page import render_landing_section
from TrueReach import render_truereach_section
from artist_insights import render_artist_insights
from artist_duel import render_artist_duel
from audio_features import render_audio_features

# Page configuration
st.set_page_config(
        page_title="Millennial Music Festival planning dashboard",
        page_icon="🎸",
        layout="wide"
    )

# Load data
data = load_data("all")
chart = load_data("chart")
mapping = load_data("mapping")
artist = load_data("artist")
tracks = load_data("tracks")

# Navigation
section = render_sidebar()

# Render selected section
if section == "🛬Landing Page":
    render_landing_section()
elif section == "👩‍🎤TrueReach®":
    render_truereach_section(chart, mapping, artist, tracks)
elif section == "🎤 Artist Insights":
    render_artist_insights(data)
elif section == "🔬Audio Features":
    render_audio_features(data)
elif section == "⚔️ Artist Duel: Who’s the Star?":
    render_artist_duel(data, artist_scores=None)
