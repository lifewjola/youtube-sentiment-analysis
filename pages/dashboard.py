import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from backend.get_name import get_nickname_by_email
from backend.modules.get_videos import get_video_urls_from_username
from backend.upsert_video import upsert_video
from backend.upsert_comments import upsert_comments_for_video
from backend.upsert_sentiment import analyze_sentiment_for_video

st.set_page_config(page_title="YouTube Sentiment Dashboard", page_icon="images/YouTube-Icon-Full-Color-Logo.wine.svg", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

DATABASE = 'youtube_dashboard.db'

email = st.session_state.get("email", None)

header1, header2 = st.columns(2)

header2.image("images/YouTube-White-Full-Color-Logo.wine.png", width=150)


if email:
    name = get_nickname_by_email(email) or "You"
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, youtube_username FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    header1.title(f"Welcome, {name}")  

    if user:
        user_id, youtube_username = user

        if "video_fetch_done" not in st.session_state:
            st.session_state["video_fetch_done"] = False

        if not st.session_state["video_fetch_done"]:
            with st.spinner("Fetching your videos and comments..."):
                try:
                    conn = sqlite3.connect(DATABASE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT video_url FROM videos WHERE user_id = ?", (user_id,))
                    existing_video_urls = {row[0] for row in cursor.fetchall()} 
                    conn.close()

                    video_urls = get_video_urls_from_username(youtube_username)
                    video_urls_latest = get_video_urls_from_username(youtube_username)[:20]

                    if not video_urls:
                        st.warning("No videos found for this username.")
                    else:
                        message_placeholder = st.empty()
                        message_placeholder.write(f"Found {len(video_urls)} videos. Processing your latest 20 videos... \nThis may take a while, please keep the tab open")
                        
                        for i, video_url in enumerate(video_urls_latest, start=1):
                            if video_url in existing_video_urls:
                                continue  

                            try:
                                upsert_video(user_id, video_url)
                                with sqlite3.connect(DATABASE) as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("SELECT video_id FROM videos WHERE video_url = ?", (video_url,))
                                    video_id = cursor.fetchone()

                                    if video_id:
                                        video_id = video_id[0]
                                        upsert_comments_for_video(video_url, video_id)
                                        analyze_sentiment_for_video(video_id)
                            except Exception as inner_e:
                                st.error(f"Error processing video {video_url}: {inner_e}")
                
                        message_placeholder.empty()

                        st.session_state["video_fetch_done"] = True

                except Exception as e:
                    st.error(f"Error fetching videos: {e}")

        def load_data(user_id):
            conn = sqlite3.connect(DATABASE)
            df_videos = pd.read_sql(f"SELECT * FROM videos WHERE user_id = {user_id}", conn)
            df_comments = pd.read_sql(f"SELECT * FROM comments WHERE video_id IN (SELECT video_id FROM videos WHERE user_id = {user_id})", conn)
            conn.close()
            return df_videos, df_comments

        videos_df, comments_df = load_data(user_id)
        comments_df["published_at"] = pd.to_datetime(comments_df["published_at"], format="%Y-%m-%dT%H:%M:%SZ")

        st.sidebar.title("Customize your View")

        video_options = ["All"] + videos_df["title"].tolist()
        selected_video_title = st.sidebar.selectbox("Select Video", video_options)

        if selected_video_title == "All":
            st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg", width=200)
            st.markdown(f"#### Showing Insights on all videos by {youtube_username}")

            selected_comments = comments_df  
            selected_video = pd.Series({
            "video_id": "All",
            "title": "All Videos",
            "likes": videos_df["likes"].sum(),
            "total_comments": comments_df.shape[0],
            "positive_count": (comments_df["sentiment"] == "POSITIVE").sum(),
            "neutral_count": (comments_df["sentiment"] == "NEUTRAL").sum(),
            "negative_count": (comments_df["sentiment"] == "NEGATIVE").sum()
        })
        else:
            selected_video = videos_df[videos_df["title"] == selected_video_title].iloc[0]
            st.markdown(f"#### Showing Insights on video: '{selected_video['title']}'")
            video_thumbnail = videos_df[videos_df['title'] == selected_video_title]['thumbnail_url'].values[0]
            st.sidebar.image(video_thumbnail, width=250)
            selected_video_id = selected_video["video_id"]
            selected_comments = comments_df[comments_df["video_id"] == selected_video_id]


        if selected_video_title != "All":
            videos_df_sorted = videos_df.sort_values("video_id")
            selected_index = videos_df_sorted[videos_df_sorted["video_id"] == selected_video_id].index[0]

            if selected_index > videos_df_sorted.index.min():
                previous_video = videos_df_sorted.loc[selected_index - 1]
                previous_video_id = previous_video["video_id"]
                previous_comments = comments_df[comments_df["video_id"] == previous_video_id]
            else:
                previous_video = None
                previous_comments = pd.DataFrame()
        else:
            previous_video = None
            previous_comments = pd.DataFrame()


        total_comments = len(selected_comments)
        if previous_video is not None:
            prev_total_comments = len(previous_comments)
            delta_comments = total_comments - prev_total_comments
        else:
            delta_comments = 0

        # Total number of likes & delta vs. previous video
        total_likes = selected_video["likes"]
        if previous_video is not None:
            prev_total_likes = previous_video["likes"]
            delta_likes = total_likes - prev_total_likes
        else:
            delta_likes = 0

        # Overall sentiment: the sentiment with the most comment likes
        if total_comments > 0:
            sentiment_counts = selected_comments["sentiment"].value_counts() 
            comment_likes = selected_comments["like_count"]
            weighted_sentiments = selected_comments.groupby("sentiment")["like_count"].sum()
            overall_sentiment = weighted_sentiments.idxmax() if not weighted_sentiments.empty else "N/A"


        disable_delta = selected_video_title == "All" or previous_video is None

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Total Comments",
                value=total_comments,
                delta=f"{delta_comments:+}" if not disable_delta and delta_comments != 0 else None,
                border=True
            )
        with col2:
            st.metric(
                label="Total Likes",
                value=total_likes,
                delta=f"{delta_likes:+}" if not disable_delta and delta_likes != 0 else None,
                border=True
            )
        with col3:
            st.metric(label="Overall Sentiment", value=overall_sentiment, border=True)

        search_term = st.sidebar.text_input("Search for a topic in comments", "")
        if search_term:
            selected_comments = selected_comments[
                selected_comments["comment_text"].str.contains(search_term, case=False, na=False)
            ]

        pos_count = (selected_comments["sentiment"] == "POSITIVE").sum()
        neu_count = (selected_comments["sentiment"] == "NEUTRAL").sum()
        neg_count = (selected_comments["sentiment"] == "NEGATIVE").sum()

        if total_comments > 0:
            pos_pct = pos_count / total_comments * 100
            neu_pct = neu_count / total_comments * 100
            neg_pct = neg_count / total_comments * 100
        else:
            pos_pct = neu_pct = neg_pct = 0

        if not disable_delta and not previous_comments.empty:
            prev_pos = (previous_comments["sentiment"] == "POSITIVE").sum()
            prev_neu = (previous_comments["sentiment"] == "NEUTRAL").sum()
            prev_neg = (previous_comments["sentiment"] == "NEGATIVE").sum()
            
            delta_pos = pos_count - prev_pos
            delta_neu = neu_count - prev_neu
            delta_neg = neg_count - prev_neg
        else:
            delta_pos = delta_neu = delta_neg = None  

        col_pos, col_neu, col_neg = st.columns(3)

        with col_pos:
            st.metric(
                label="Positive Comments",
                value=f"{pos_count} ({pos_pct:.1f}%)",
                delta=f"{delta_pos:+}" if delta_pos is not None and delta_pos != 0 else None,
                border=True
            )
            with st.expander("View Positive Comments"):
                for _, row in selected_comments[selected_comments["sentiment"] == "POSITIVE"].iterrows():
                    st.write(row["comment_text"])

        with col_neu:
            st.metric(
                label="Neutral Comments",
                value=f"{neu_count} ({neu_pct:.1f}%)",
                delta=f"{delta_neu:+}" if delta_neu is not None and delta_neu != 0 else None,
                border=True
            )
            with st.expander("View Neutral Comments"):
                for _, row in selected_comments[selected_comments["sentiment"] == "NEUTRAL"].iterrows():
                    st.write(row["comment_text"])

        with col_neg:
            st.metric(
                label="Negative Comments",
                value=f"{neg_count} ({neg_pct:.1f}%)",
                delta=f"{delta_neg:+}" if delta_neg is not None and delta_neg != 0 else None,
                delta_color="inverse",
                border=True
            )
            with st.expander("View Negative Comments"):
                for _, row in selected_comments[selected_comments["sentiment"] == "NEGATIVE"].iterrows():
                    st.write(row["comment_text"])

        with st.sidebar.expander("ℹ️ Metric Explanations"):
            st.write("- Overall Sentiment is based on the sentiment with the most comment likes.")
            st.write("- The deltas indicate performance in comparison to the last video")
        st.sidebar.image("images/bmc", width=150)


        def generate_wordcloud(text, colormap):

            custom_stopwords = STOPWORDS.union({"video", "watch", "channel", "subscribe", "like", "good"})

            if not text:
                return None
            wc = WordCloud(width=400, height=200, background_color="white",
                        colormap=colormap, stopwords=custom_stopwords).generate(text)
            return wc

        st.markdown("#### Keywords Associated with Each Sentiment")

        col_wc1, col_wc2, col_wc3 = st.columns(3)
        with col_wc1:
            st.markdown("##### Positive")
            positive_text = " ".join(selected_comments[selected_comments["sentiment"]=="POSITIVE"]["comment_text"].tolist())
            wc_positive = generate_wordcloud(positive_text, "Blues")
            if wc_positive:
                fig, ax = plt.subplots(figsize=(4, 2))
                ax.imshow(wc_positive, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
        with col_wc2:
            st.markdown("##### Neutral")
            neutral_text = " ".join(selected_comments[selected_comments["sentiment"]=="NEUTRAL"]["comment_text"].tolist())
            wc_neutral = generate_wordcloud(neutral_text, "Greys")
            if wc_neutral:
                fig, ax = plt.subplots(figsize=(4, 2))
                ax.imshow(wc_neutral, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
        with col_wc3:
            st.markdown("##### Negative")
            negative_text = " ".join(selected_comments[selected_comments["sentiment"]=="NEGATIVE"]["comment_text"].tolist())
            wc_negative = generate_wordcloud(negative_text, "Reds")
            if wc_negative:
                fig, ax = plt.subplots(figsize=(4, 2))
                ax.imshow(wc_negative, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)

        custom_colors = {
            "POSITIVE": "darkblue", 
            "NEUTRAL": "lightgray", 
            "NEGATIVE": "lightcoral"  
        }

        sentiment_data = pd.DataFrame({
            "sentiment": ["POSITIVE", "NEUTRAL", "NEGATIVE"],
            "count": [pos_count, neu_count, neg_count]
        })


        fig = go.Figure()

        for sentiment, color in custom_colors.items():
            df_filtered = sentiment_data[sentiment_data["sentiment"] == sentiment]
            fig.add_trace(go.Bar(
                x=df_filtered["sentiment"], 
                y=df_filtered["count"], 
                name=sentiment.capitalize(),
                marker=dict(color=color)
            ))

        fig.update_layout(title_text="Sentiment Distribution")
        
        st.plotly_chart(fig, use_container_width=True)

        if not selected_comments.empty:
            selected_comments["date"] = selected_comments["published_at"].dt.date
            
            trend_data = selected_comments.groupby(["date", "sentiment"]).size().reset_index(name="count")

            line_fig = px.line(
                trend_data, 
                x="date", 
                y="count", 
                color="sentiment",
                title="Sentiment Trend Over Time",
                line_group="sentiment",
                color_discrete_map=custom_colors,
            )
            
            line_fig.update_yaxes(range=[0, max(trend_data["count"]) if not trend_data.empty else 10])

            st.plotly_chart(line_fig, use_container_width=True, key="chart_line")
        else:
            st.write("No comments available for trend analysis.")


        total_counts = comments_df.groupby("video_id").size().reset_index(name="total_comments")

        positive_counts = (comments_df[comments_df["sentiment"] == "POSITIVE"]
                        .groupby("video_id").size().reset_index(name="positive_count"))

        videos_merged = pd.merge(videos_df, total_counts, on="video_id", how="left")
        videos_merged = pd.merge(videos_merged, positive_counts, on="video_id", how="left")

        videos_merged[["total_comments", "positive_count"]] = videos_merged[["total_comments", "positive_count"]].fillna(0)

        videos_merged["positive_percentage"] = (videos_merged["positive_count"] / videos_merged["total_comments"]) * 100

        videos_merged["positive_percentage"] = videos_merged["positive_percentage"].fillna(0)

        bubble_fig = px.scatter(videos_merged,
                                x="likes",
                                y="positive_percentage",
                                size="positive_percentage",
                                color="title",
                                hover_name="title",
                                title="Correlation between Video Likes and Positive Comment Percentage")

        st.plotly_chart(bubble_fig, use_container_width=True, key="chart_bubble")
    
    st.sidebar.link_button("Log Out", "pages/logout")

else:
    st.title("Dashboard")
    st.warning("Log in to get a full view analysis across 20 videos.")
    if st.link_button("Login", "pages/login"):
        st.switch_page("pages/login.py")
