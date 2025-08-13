import streamlit as st
import pandas as pd
import plotly.express as px

def render_artist_insights(data):
    st.title("🎤 Artist Insights")
    tab_1, tab_2=st.tabs(['Artist Insight','Top Artists Now'])
    data["chart_week"] = pd.to_datetime(data["chart_week"], errors="coerce")
    with tab_1: 
        # Artist Filter
        st.subheader("Filter by Artist")
        artist_choice = st.selectbox("Select an Artist", data["artist"].unique(), index=7)
        artist_data = data[data["artist"] == artist_choice]

        # Ensure data exists for the selected artist
        if artist_data.empty:
            st.write("No data available for the selected artist.")
        else:
            # 1. Artist Score Growth Over Time
            st.subheader("📈 Artist TrueReach® Growth Over Time")

            # Group by year dynamically
            artist_data_yearly = (
                artist_data.groupby(artist_data["chart_week"].dt.year)
                .agg({"score": "sum"})
                .reset_index()
                .rename(columns={"chart_week": "Year"})
            )

            # Ensure the Year column is an integer
            artist_data_yearly["Year"] = artist_data_yearly["Year"].astype(int)

            # Allow user to select a range of years
            min_year, max_year = artist_data_yearly["Year"].min(), artist_data_yearly["Year"].max()
            # Check if the artist has only one year of activity or no activity
        if min_year == max_year:
            st.write(f"The artist {artist_choice} has not been active across multiple years or has insufficient data for a range of years.")
        else:
            # Range slider for year selection
            selected_years = st.slider(
                "Select Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=1,
                help="Drag the slider to filter data by year range."
            )

            # Filter the data based on the selected year range
            filtered_data = artist_data_yearly[
                (artist_data_yearly["Year"] >= selected_years[0]) &
                (artist_data_yearly["Year"] <= selected_years[1])
            ]

            # Create the line chart
            fig = px.line(
                filtered_data,
                x="Year",
                y="score",
                title=f"TrueReach® Growth for {artist_choice} ({selected_years[0]} - {selected_years[1]})",
                labels={"Year": "Year", "score": "Score"},
                template="plotly_white"
            )
            fig.update_layout(title_x=0.5, xaxis=dict( type="category")) # Treat years as discrete categories to avoid decimals
        
            st.plotly_chart(fig, use_container_width=True)

            # 2. Most Successful Tracks by Chart Appearances
            st.subheader("Most Successful Tracks by Chart Appearances")
            track_success_count = (
                artist_data.groupby(["track_title", "artist"], as_index=False)
                .agg({"list_position": "count", "release_date": "min"})  # Count chart appearances and get release date
                .rename(columns={"list_position": "num_chart_appearances"})  # Rename column for clarity
                .sort_values("num_chart_appearances", ascending=False)  # Sort by the number of appearances
            )

            top_successful_tracks = track_success_count.head(5)
            st.write(top_successful_tracks[["track_title", "num_chart_appearances", "release_date"]])

            fig = px.bar(
                top_successful_tracks,
                x="track_title",
                y="num_chart_appearances",
                title=f"Most Successful Tracks for {artist_choice}",
                labels={"track_title": "Track Title", "num_chart_appearances": "Chart Appearances"},
                text="num_chart_appearances",  # Display chart appearances count on bars,
                color="num_chart_appearances",
                color_continuous_scale="purp"
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(title_x=0.5, template="plotly_white", height=600, width=1000,)
            st.plotly_chart(fig, use_container_width=True)

            # 3. Release Distribution
            st.subheader(f"Release Distribution for {artist_choice}")
            unique_tracks = artist_data.groupby("track_id", as_index=False).first()  # Ensure unique tracks by grouping on track_id
            track_types = unique_tracks["album_type"].value_counts().reset_index()
            track_types.columns = ["album_type", "count"]

            fig = px.pie(
                track_types,
                values="count",
                names="album_type",
                title=f"Release Distribution for {artist_choice}",
                labels={"album_type": "Album Type", "count": "Count"},
                template="plotly_white",
                color="album_type",
                color_discrete_sequence= px.colors.sequential.Purp_r
            )
            st.plotly_chart(fig)
    with tab_2: 
        # Discover Top Artists
            
        st.subheader("Discover the Top Artists Now")
        st.write("Explore the top artists based on current popularity and customize filters to refine the view.")

        # Range slider for popularity
        popularity_range = st.slider(
            "Select Popularity Range",
            min_value=int(data["popularity"].min()),
            max_value=int(data["popularity"].max()),
            value=(50, 100),  # Default range
            step=1,
            help="Select the range of popularity scores to filter artists."
            )

        explicit_filter = st.checkbox(
            "Include Explicit Artists",
            value=True,
            help="Toggle to include or exclude explicit artists."
            )

        # Group data by artist
        grouped_artists = data.groupby("artist", as_index=False).agg({
                "popularity": "mean",  # Average popularity score
                "followers": "sum",    # Total followers for each artist
                "explicit": "any",     # Check if any track is explicit
                "score": "sum"         # Total score for the artist (TrueReach)
            })

        # Apply filters
        filtered_artists = grouped_artists[
                (grouped_artists['popularity'] >= popularity_range[0]) &
                (grouped_artists['popularity'] <= popularity_range[1])
            ]
        if not explicit_filter:
                filtered_artists = filtered_artists[~filtered_artists['explicit']]

        # Sort by popularity
        filtered_artists = filtered_artists.sort_values("popularity", ascending=False)

        # Top Artists Chart
        fig = px.bar(
                filtered_artists.head(10),
                x="artist",
                y="popularity",
                title="Top 10 Artists by Popularity",
                color="explicit",
                labels={"artist": "Artist", "popularity": "Popularity"},
                color_discrete_map= {True: "#f0766d", False: "#d2b4de"},
                template="plotly_white",
                hover_data={"popularity": True, "followers": True, "explicit": True}
            )
        fig.update_layout(title_x=0.5)
        st.plotly_chart(fig, use_container_width=True)

        # Filtered Artists Data Table
        st.subheader("Filtered Artists Data")
        st.dataframe(filtered_artists[["artist", "popularity", "followers", "explicit", "score"]], use_container_width=True)
