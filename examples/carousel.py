"""Example: Create a carousel post with multiple images."""

import os

from threads import ThreadsClient

ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


def create_carousel() -> None:
    """Create a carousel post with multiple images."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Step 1: Create individual media containers for each carousel item
        image_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg",
        ]

        item_ids = []
        for url in image_urls:
            container = client.media.create_image_container(
                user_id=USER_ID,
                image_url=url,
                is_carousel_item=True,  # Mark as carousel item
            )
            item_ids.append(container.id)
            print(f"Created carousel item: {container.id}")

        # Step 2: Create the carousel container with all items
        carousel = client.media.create_carousel_container(
            user_id=USER_ID,
            children=item_ids,
            text="Check out these photos! Swipe to see more.",
        )
        print(f"Created carousel container: {carousel.id}")

        # Step 3: Publish the carousel
        post = client.posts.publish(USER_ID, carousel.id)
        print(f"Carousel published: {post.permalink}")


def create_mixed_carousel() -> None:
    """Create a carousel with both images and videos."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Create image item
        image_container = client.media.create_image_container(
            user_id=USER_ID,
            image_url="https://example.com/image.jpg",
            is_carousel_item=True,
        )

        # Create video item
        video_container = client.media.create_video_container(
            user_id=USER_ID,
            video_url="https://example.com/video.mp4",
            is_carousel_item=True,
        )

        # Wait for video to process
        import time

        while True:
            status = client.media.get_container_status(video_container.id)
            if status.is_ready:
                break
            if status.has_error:
                raise Exception(f"Video processing failed: {status.error_message}")
            print("Waiting for video processing...")
            time.sleep(2)

        # Create and publish carousel
        carousel = client.media.create_carousel_container(
            user_id=USER_ID,
            children=[image_container.id, video_container.id],
            text="Image + Video carousel",
        )

        post = client.posts.publish(USER_ID, carousel.id)
        print(f"Mixed carousel published: {post.permalink}")


if __name__ == "__main__":
    create_carousel()
