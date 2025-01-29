import streamlit as st
import pandas as pd
import plotly.express as px
from spotify_client import get_artist_image

def render_audio_features(data):
    # Function to display images with fixed size
    def display_fixed_size_image(col, image_url, alt_text, size=1):
        if image_url:
            col.markdown(f"""
            <div style="text-align: center;">
                <img src="{image_url}" alt="{alt_text}" style="width:{size}px; height:{size}px; object-fit:cover; border-radius:10px;">
            </div>
            """, unsafe_allow_html=True)
        else:
            col.write(f"No image available for {alt_text}")

    # Load the dataset
    @st.cache_data
    def load_data():
        data = pd.read_csv("https://raw.githubusercontent.com/orrefo/Music/refs/heads/main/all.csv")
        return data

    data = load_data()

    # Ensure "chart_week" is in datetime format
    data["chart_week"] = pd.to_datetime(data["chart_week"], errors="coerce")

    
    st.title(":musical_note: Audio Features")

    tab1, tab2, = st.tabs(["General Statistics", "Artist Specific"])

        # List of audio features to plot
    audio_features = [
            "acousticness",
            "valence",
            "danceability",
            "energy",
            "speechiness",
            "instrumentalness",
            "liveness"
        ]

        # Dictionary of audio features and their corresponding emojis
    feature_emojis = {
        "acousticness": "🎸",
        "valence": "😃",
        "danceability": "🕺",
        "energy": "⚡",
        "speechiness": "🗣️",
        "instrumentalness": "🎹",
        "liveness": "🎤"
    }

    # Check if the dataset contains the necessary columns
    available_features = [feature for feature in audio_features if feature in data.columns]

    if not available_features:
        st.error("The dataset does not contain any of the specified audio features.")
    elif data["chart_week"].isna().all():
        st.error("The 'chart_week' column contains no valid dates.")
    else:
        valid_data = data.dropna(subset=["chart_week"])

        with tab1:
            st.subheader("General Audio Feature Trends and Top 10 Tracks")
            
            
            # Add the description using st.markdown with Markdown formatting
            st.markdown("""
                This section provides an insightful overview of key audio features across all tracks in the Billboard Top 100 from the year 2000 until now, 
                highlighting trends over time and identifying the top-performing tracks based on their **TrueReach®** scores.
                """)


            for feature in available_features:
                emoji = feature_emojis.get(feature, "")

                feature_data = valid_data.dropna(subset=[feature])
                grouped_tracks = feature_data.groupby("track_title").agg(
                    {
                        feature: "max",
                        "artist": "first",
                        "score": "max"
                    }
                ).reset_index()

                top_tracks = grouped_tracks.sort_values(
                    by=["score", feature], ascending=[False, False]
                ).head(10)

                if not top_tracks.empty:
                    st.subheader(f"Top 10 tracks with most {feature.capitalize()} {emoji} by TrueReach®")
                    top_tracks = top_tracks[["track_title", "artist", feature, "score"]]
                    top_tracks = top_tracks.rename(columns={
                        "track_title": "Track",
                        "artist": "Artist",
                        feature: f"{feature.capitalize()}",
                        "score": "Score"
                    }).reset_index(drop=True)


                    # Iterate through the top tracks and display images and text
                    for i in range(0, len(top_tracks), 5):  # Loop through the top tracks in batches of 5
                        cols = st.columns(5)  # Create 5 columns
                        for col, (idx, row) in zip(cols, top_tracks.iloc[i:i+5].iterrows()):
                            # Fetch artist image
                            #artist_image_url = get_artist_image(row["Artist"])
                            
                            # Display image and text
                            #if artist_image_url:
                            #    display_fixed_size_image(col, artist_image_url, alt_text=row["Artist"], size=150)
                            col.write(f"**{row['Artist']}**")
                            col.write(f"*{row['Track']}*")

                feature_trend = (
                    feature_data.groupby(feature_data["chart_week"].dt.year)
                    .agg({feature: "mean"})
                    .reset_index()
                    .rename(columns={"chart_week": "Year", feature: f"Average {feature.capitalize()}"})
                )

                fig = px.line(
                    feature_trend,
                    x="Year",
                    y=f"Average {feature.capitalize()}",
                    title=f"Trend of {feature.capitalize()} Over Time {emoji}",
                    labels={"Year": "Year", f"Average {feature.capitalize()}": feature.capitalize()},
                    template="plotly_white"
                )
                fig.update_layout(
                    title_x=0.0,
                    xaxis=dict(
                        title="Year",
                        tickfont=dict(size=20)
                    ),
                    yaxis=dict(
                        title=f"Average {feature.capitalize()}",
                        tickfont=dict(size=16)
                    ),
                    font=dict(size=14)
                )
                st.plotly_chart(fig, use_container_width=True)

    
        with tab2:
            

            st.subheader("Artist Specific Audio Feature Statistics")

            # Ensure valid_data contains artist information
            if "artist" not in valid_data.columns or valid_data["artist"].isna().all():
                st.error("No artist data available in the dataset.")
            else:
                # Extract artist list
                artist_list = valid_data["artist"].dropna().unique()

                # Check if artist_list is empty
                if len(artist_list) == 0:
                    st.warning("No artists found in the dataset.")
                else:
                    # Artist selection dropdown with a unique key
                    selected_artist = st.selectbox(
                        "Filter by Artist", 
                        options=sorted(artist_list),
                        index=35,
                        key="artist_filter_tab3"  # Unique key
                    )

                    if selected_artist:
                        # Display a single image of the selected artist
                        artist_image_url = get_artist_image(selected_artist)
                        if artist_image_url:
                            st.image(artist_image_url, caption=selected_artist, width=700)

                        # Filter data for the selected artist
                        artist_data = valid_data[valid_data["artist"] == selected_artist]

                        for feature in available_features:
                            emoji = feature_emojis.get(feature, "")

                            # Filter data for the selected feature
                            feature_data = artist_data.dropna(subset=[feature])
                            grouped_tracks = feature_data.groupby("track_title").agg(
                                {
                                    feature: "max",
                                    "artist": "first",
                                    "score": "sum"
                                }
                            ).reset_index()

                            top_tracks = grouped_tracks.sort_values(
                                by=[feature, "score"], ascending=[False, False]
                            ).head(10)

                            if not top_tracks.empty:
                                st.subheader(f"Top 10 Tracks by {feature.capitalize()} {emoji} for {selected_artist}")
                                top_tracks = top_tracks[["track_title", feature, "score"]]
                                top_tracks = top_tracks.rename(columns={
                                    "track_title": "Track Title",
                                    feature: f"{feature.capitalize()}",
                                    "score": "TrueReach®"
                                }).reset_index(drop=True)

                            
                                
                            fig = px.bar(
                                top_tracks,
                                x="Track Title", 
                                y=f"{feature.capitalize()}", 
                                color="TrueReach®",  # Third dimension as a color scale
                                title=f"Top 10 Tracks by {feature.capitalize()} for {selected_artist}",
                                labels={f"{feature.capitalize()}": f"{feature.capitalize()}", "TrueReach®": "TrueReach®"},
                                color_continuous_scale="purp"  # Choose a color scale
                            )

                                # Align title to the left
                            fig.update_layout(
                                title=dict(x=0.0),  # Align title to the left
                                xaxis_title="Track Title",
                                yaxis_title=f"{feature.capitalize()}",
                                coloraxis_colorbar=dict(
                                    title="TrueReach<br>"
                                )
                            )

                            # Display the graph in Streamlit
                            st.plotly_chart(fig, use_container_width=True)
                            # Display the data as a table
                            st.table(top_tracks)