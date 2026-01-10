"""Example: Create a basic text post on Threads."""

import os

from threads import ThreadsClient

# Get credentials from environment variables
ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


def main() -> None:
    """Post a simple text thread."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Create and publish a text post in one call
        post = client.posts.create_and_publish(
            user_id=USER_ID,
            text="Hello from Threads SDK! 🧵",
        )

        print("Post published successfully!")
        print(f"Post ID: {post.id}")
        print(f"Permalink: {post.permalink}")


if __name__ == "__main__":
    main()
