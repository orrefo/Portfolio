import streamlit as st
import pandas as pd
import plotly.express as px

def render_artist_duel(data, artist_scores):
    st.title("⚔️ Artist Duel: Who’s the Star?")
    st.write(
        "Compare two artists head-to-head on various metrics like popularity, followers, and energy."
    )
    
    # Preprocess data: Group by artist to calculate the total points with the TrueReach system 
    artist_scores = data.groupby("artist", as_index=False)["score"].sum()
    
    # Select Artists
    artist_1 = st.selectbox("Choose Artist 1", artist_scores["artist"].unique(), index=35)
    artist_2 = st.selectbox("Choose Artist 2", artist_scores["artist"].unique(), index=98)
    artist_1_data = data[data["artist"] == artist_1]
    artist_2_data = data[data["artist"] == artist_2]
    
    # Get overall scores for each artist
    artist_1_score_true = artist_1_data["score"].sum()
    artist_2_score_true = artist_2_data["score"].sum()

    # Display overall scores as a bar chart
    st.subheader("🌟 TrueReach® Comparison")
    overall_score_data = pd.DataFrame({
        "Artist": [artist_1, artist_2],
        "Score": [artist_1_score_true, artist_2_score_true]
    })

    # Dynamic color assignment for TrueReach®
    color_scale = ["#a569bd", "#d2b4de"] if artist_1_score_true > artist_2_score_true else ["#d2b4de", "#a569bd"]

    fig = px.bar(
        overall_score_data,
        x="Artist",
        y="Score",
        title="🌟 TrueReach® Comparison",
        labels={"Artist": "Artist", "Score": "TrueReach®"},
        color="Artist",
        color_discrete_sequence=color_scale,
        template="plotly_white"
    )
    fig.update_layout(title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Artist Duel Comparison Metrics
    metrics = {
        "🎶 Popularity": "popularity",
        "👥 Followers": "followers",
        "💃 Danceability": "danceability",
        "⚡ Energy": "energy",
        "🎭 Valence (Mood)": "valence"
    }

    # Loop through each metric to create individual charts
    for metric_name, metric_column in metrics.items():
        st.subheader(f"{metric_name}")

        # Calculate scores
        artist_1_score = artist_1_data[metric_column].mean()
        artist_2_score = artist_2_data[metric_column].mean()

        # Create a DataFrame for the metric comparison
        duel_data = pd.DataFrame({
            "Artist": [artist_1, artist_2],
            "Score": [artist_1_score, artist_2_score]
        })

        # Dynamic color assignment for the current metric
        metric_colors =["#a569bd", "#d2b4de"]  if artist_1_score > artist_2_score else ["#d2b4de", "#a569bd"]

        # Create bar chart for the metric
        fig = px.bar(
            duel_data,
            x="Artist",
            y="Score",
            title=f"{metric_name}: {artist_1} vs {artist_2}",
            labels={"Artist": "Artist", "Score": metric_name},
            color="Artist",
            color_discrete_sequence=metric_colors,
            template="plotly_white"
        )
        fig.update_layout(title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

    # Prepare summary table
    st.subheader("📊 Summary of Comparison Metrics")
    summary_data = pd.DataFrame({
        "Metric": ["🌟 TrueReach®"] + list(metrics.keys()),
        artist_1: [artist_1_score_true] + [
            round(artist_1_data[metrics[key]].mean(), 1)
            for key in metrics
        ],
        artist_2: [artist_2_score_true] + [
            round(artist_2_data[metrics[key]].mean(), 1)
            for key in metrics
        ]
    })

    # Display summary table
    st.dataframe(summary_data, use_container_width=True)
