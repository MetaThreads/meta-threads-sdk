"""Example: Using the async client for concurrent operations."""

import asyncio
import os

from threads import AsyncThreadsClient

ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


async def basic_async_post() -> None:
    """Create a post using the async client."""
    async with AsyncThreadsClient(access_token=ACCESS_TOKEN) as client:
        post = await client.posts.create_and_publish(
            user_id=USER_ID,
            text="Posted asynchronously!",
        )
        print(f"Post published: {post.permalink}")


async def concurrent_operations() -> None:
    """Perform multiple operations concurrently."""
    async with AsyncThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Fetch multiple resources concurrently
        posts_task = client.posts.get_user_posts(USER_ID, limit=10)
        limit_task = client.posts.get_publishing_limit(USER_ID)

        posts, limit = await asyncio.gather(posts_task, limit_task)

        print(f"Found {len(posts)} posts")
        print(f"Publishing limit: {limit.remaining_posts} posts remaining")


async def fetch_insights_for_multiple_posts() -> None:
    """Fetch insights for multiple posts concurrently."""
    async with AsyncThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Get recent posts
        posts = await client.posts.get_user_posts(USER_ID, limit=5)

        if not posts:
            print("No posts found")
            return

        # Fetch insights for all posts concurrently
        insight_tasks = [client.insights.get_media_insights(post.id) for post in posts]

        insights_list = await asyncio.gather(*insight_tasks)

        # Display results
        for post, insights in zip(posts, insights_list, strict=True):
            print(f"\nPost: {post.text[:50] if post.text else 'No text'}...")
            print(f"  Views: {insights.views}")
            print(f"  Likes: {insights.likes}")
            print(f"  Replies: {insights.replies}")


async def post_multiple_threads() -> None:
    """Post multiple threads concurrently (be mindful of rate limits!)."""
    async with AsyncThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Check publishing limit first
        limit = await client.posts.get_publishing_limit(USER_ID)

        if limit.remaining_posts < 3:
            print(f"Not enough quota. Remaining: {limit.remaining_posts}")
            return

        texts = [
            "First concurrent post",
            "Second concurrent post",
            "Third concurrent post",
        ]

        # Create all posts concurrently
        post_tasks = [
            client.posts.create_and_publish(user_id=USER_ID, text=text)
            for text in texts
        ]

        posts = await asyncio.gather(*post_tasks)

        for post in posts:
            print(f"Published: {post.permalink}")


if __name__ == "__main__":
    asyncio.run(basic_async_post())
