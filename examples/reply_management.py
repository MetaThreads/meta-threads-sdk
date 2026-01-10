"""Example: Managing replies on Threads posts."""

import os

from threads import ReplyControl, ThreadsClient

ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
USER_ID = os.environ["THREADS_USER_ID"]


def get_replies_to_post(post_id: str) -> None:
    """Get all replies to a specific post."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        replies = client.replies.get_replies(post_id)

        print(f"Found {len(replies)} replies:")
        for reply in replies:
            print(f"\n@{reply.username}: {reply.text}")
            print(f"  ID: {reply.id}")
            print(f"  Hidden: {reply.hide_status}")


def get_conversation_thread(post_id: str) -> None:
    """Get the full conversation thread for a post."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Get conversation (includes nested replies)
        conversation = client.replies.get_conversation(post_id)

        print(f"Conversation thread ({len(conversation)} messages):")
        for msg in conversation:
            print(f"  @{msg.username}: {msg.text}")


def hide_reply(reply_id: str) -> None:
    """Hide a specific reply."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        success = client.replies.hide(reply_id)

        if success:
            print(f"Reply {reply_id} hidden successfully")
        else:
            print("Failed to hide reply")


def unhide_reply(reply_id: str) -> None:
    """Unhide a previously hidden reply."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        success = client.replies.unhide(reply_id)

        if success:
            print(f"Reply {reply_id} unhidden successfully")
        else:
            print("Failed to unhide reply")


def get_user_replies() -> None:
    """Get all replies made by the authenticated user."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        replies = client.replies.get_user_replies(USER_ID, limit=20)

        print(f"Your recent replies ({len(replies)}):")
        for reply in replies:
            print(f"\n{reply.text}")
            print(f"  Permalink: {reply.permalink}")
            print(f"  Posted: {reply.timestamp}")


def post_with_reply_control() -> None:
    """Create a post with specific reply controls."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        # Only allow accounts you follow to reply
        post = client.posts.create_and_publish(
            user_id=USER_ID,
            text="This post only allows replies from accounts I follow.",
            reply_control=ReplyControl.ACCOUNTS_YOU_FOLLOW,
        )
        print(f"Post with restricted replies: {post.permalink}")


def post_reply(post_id: str, text: str) -> None:
    """Reply to an existing post."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        from threads import MediaType

        # Create a reply container
        container = client.media.create_container(
            user_id=USER_ID,
            media_type=MediaType.TEXT,
            text=text,
            reply_to_id=post_id,  # This makes it a reply
        )

        # Publish the reply
        reply = client.posts.publish(USER_ID, container.id)
        print(f"Reply posted: {reply.permalink}")


def moderate_replies(post_id: str) -> None:
    """Example moderation workflow for replies."""
    with ThreadsClient(access_token=ACCESS_TOKEN) as client:
        replies = client.replies.get_replies(post_id)

        # Define some basic moderation keywords
        blocked_words = ["spam", "scam", "buy now"]

        for reply in replies:
            if reply.text is None:
                continue

            # Check for blocked content
            text_lower = reply.text.lower()
            should_hide = any(word in text_lower for word in blocked_words)

            if should_hide and reply.hide_status != "HIDDEN":
                print(f"Hiding reply from @{reply.username}: {reply.text[:50]}...")
                client.replies.hide(reply.id)


if __name__ == "__main__":
    # Example: Get replies to a specific post
    # get_replies_to_post("POST_ID_HERE")

    # Example: Get user's own replies
    get_user_replies()
