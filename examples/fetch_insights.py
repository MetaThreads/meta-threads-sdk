"""Example: Fetch and analyze post insights."""

import os
from datetime import datetime, timedelta

from threads import MetricType, ThreadsClient

ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


def get_post_insights(post_id: str) -> None:
    """Get detailed insights for a specific post."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        insights = client.insights.get_media_insights(post_id)

        print(f"Insights for post {post_id}:")
        print(f"  Views: {insights.views}")
        print(f"  Likes: {insights.likes}")
        print(f"  Replies: {insights.replies}")
        print(f"  Reposts: {insights.reposts}")
        print(f"  Quotes: {insights.quotes}")


def get_specific_metrics(post_id: str) -> None:
    """Get only specific metrics for a post."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Request only views and likes
        insights = client.insights.get_media_insights(
            post_id,
            metrics=[MetricType.VIEWS, MetricType.LIKES],
        )

        print(f"Views: {insights.views}")
        print(f"Likes: {insights.likes}")


def get_engagement_summary(post_id: str) -> None:
    """Get engagement metrics using convenience method."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        engagement = client.insights.get_engagement(post_id)

        print("Engagement Summary:")
        for metric, value in engagement.items():
            print(f"  {metric.capitalize()}: {value}")

        # Calculate engagement rate if you have views
        views = client.insights.get_views(post_id)
        total_engagement = sum(engagement.values())
        if views > 0:
            rate = (total_engagement / views) * 100
            print(f"\nEngagement Rate: {rate:.2f}%")


def get_user_insights() -> None:
    """Get account-level insights."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Get insights for the past 7 days
        now = int(datetime.now().timestamp())
        week_ago = int((datetime.now() - timedelta(days=7)).timestamp())

        insights = client.insights.get_user_insights(
            USER_ID,
            since=week_ago,
            until=now,
        )

        print("User Insights (Last 7 Days):")
        for insight in insights.data:
            print(f"  {insight.name}: {insight.values}")


def analyze_all_posts() -> None:
    """Analyze insights for all recent posts."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Get recent posts
        posts = client.posts.get_user_posts(USER_ID, limit=10)

        if not posts:
            print("No posts found")
            return

        print(f"Analyzing {len(posts)} posts...\n")

        total_views = 0
        total_likes = 0
        total_replies = 0

        for post in posts:
            try:
                insights = client.insights.get_media_insights(post.id)
                total_views += insights.views
                total_likes += insights.likes
                total_replies += insights.replies

                text_preview = (post.text[:40] + "...") if post.text else "No text"
                print(f"Post: {text_preview}")
                print(f"  Views: {insights.views}, Likes: {insights.likes}")
            except Exception as e:
                print(f"Error fetching insights for {post.id}: {e}")

        print("\n" + "=" * 40)
        print("TOTALS:")
        print(f"  Total Views: {total_views}")
        print(f"  Total Likes: {total_likes}")
        print(f"  Total Replies: {total_replies}")

        if len(posts) > 0:
            print("\nAVERAGES:")
            print(f"  Avg Views/Post: {total_views / len(posts):.1f}")
            print(f"  Avg Likes/Post: {total_likes / len(posts):.1f}")


if __name__ == "__main__":
    analyze_all_posts()
