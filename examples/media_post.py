"""Example: Post images and videos to Threads."""

import os

from threads import ThreadsClient

ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


def post_image() -> None:
    """Post an image with caption."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        post = client.posts.create_and_publish(
            user_id=USER_ID,
            text="Check out this image!",
            image_url="https://example.com/image.jpg",
        )
        print(f"Image post published: {post.permalink}")


def post_video() -> None:
    """Post a video with caption."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Videos may take time to process, so we wait for the container
        post = client.posts.create_and_publish(
            user_id=USER_ID,
            text="Watch this video!",
            video_url="https://example.com/video.mp4",
            wait_for_ready=True,  # Wait for video processing
            max_wait_time=120.0,  # Wait up to 2 minutes
        )
        print(f"Video post published: {post.permalink}")


def post_with_manual_container() -> None:
    """Create container and publish separately for more control."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Step 1: Create the media container
        container = client.media.create_image_container(
            user_id=USER_ID,
            image_url="https://example.com/image.jpg",
            text="Posted with manual container creation",
        )
        print(f"Container created: {container.id}")

        # Step 2: Check container status (optional for images)
        status = client.media.get_container_status(container.id)
        print(f"Container status: {status.status}")

        # Step 3: Publish the container
        post = client.posts.publish(USER_ID, container.id)
        print(f"Post published: {post.permalink}")


if __name__ == "__main__":
    post_image()
