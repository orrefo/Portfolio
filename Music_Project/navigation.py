# Navigation sidebar logic will go here
import streamlit as st

def render_sidebar():
    st.sidebar.title("🎵 Dashboard Navigation")
    return st.sidebar.radio(
        "Select a Section",
        [
            "🛬Landing Page",
            "👩‍🎤TrueReach®",
            "🎤 Artist Insights",
            "⚔️ Artist Duel: Who’s the Star?",
            "🔬Audio Features"
            
        ]
    )