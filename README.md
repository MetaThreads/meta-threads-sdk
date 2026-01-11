# meta-threads-sdk

Unofficial Python SDK for Meta's Threads API.

[![PyPI version](https://img.shields.io/pypi/v/meta-threads-sdk.svg)](https://pypi.org/project/meta-threads-sdk/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Sync & Async clients** - Choose the right client for your use case
- **Full API coverage** - Posts, media, insights, replies, user profiles
- **Type-safe** - Full type hints and Pydantic models
- **OAuth 2.0** - Complete authentication flow support
- **Rate limiting** - Built-in rate limit tracking
- **Logging** - Configurable logging for debugging

## Installation

```bash
pip install meta-threads-sdk
```

Or with uv:

```bash
uv add meta-threads-sdk
```

## Quick Start

### Synchronous Client

```python
from threads import ThreadsClient

with ThreadsClient(access_token="your_token") as client:
    # Create a text post
    post = client.posts.create_and_publish(
        user_id="your_user_id",
        text="Hello from Threads SDK!",
    )
    print(f"Published: {post.permalink}")

    # Get user profile
    profile = client.users.get_me()
    print(f"Username: {profile.username}")
```

### Asynchronous Client

```python
import asyncio
from threads import AsyncThreadsClient

async def main():
    async with AsyncThreadsClient(access_token="your_token") as client:
        post = await client.posts.create_and_publish(
            user_id="your_user_id",
            text="Hello from async Threads SDK!",
        )
        print(f"Published: {post.permalink}")

asyncio.run(main())
```

## Authentication

### OAuth 2.0 Flow

1. **Set up your Meta App**: Go to [Meta Developer Console](https://developers.facebook.com/) and create an app with Threads API access.

2. **Configure redirect URI**: Add your redirect URI in the app settings (e.g., `https://your-app.com/callback`).

3. **Get authorization**:

```python
from threads import ThreadsClient
from threads.constants import Scope

client = ThreadsClient(access_token="")

# Step 1: Generate authorization URL
auth_url = client.auth.get_authorization_url(
    client_id="your_app_id",
    redirect_uri="https://your-app.com/callback",
    scopes=[
        Scope.BASIC,
        Scope.CONTENT_PUBLISH,
        Scope.MANAGE_INSIGHTS,
        Scope.READ_REPLIES,
        Scope.MANAGE_REPLIES,
    ],
)
print(f"Open this URL: {auth_url}")

# Step 2: After user authorizes, exchange code for token
short_token = client.auth.exchange_code(
    client_id="your_app_id",
    client_secret="your_app_secret",
    redirect_uri="https://your-app.com/callback",
    code="authorization_code_from_callback",
)
print(f"Short-lived token: {short_token.access_token}")
print(f"User ID: {short_token.user_id}")

# Step 3: Get long-lived token (60 days)
long_token = client.auth.get_long_lived_token(
    client_secret="your_app_secret",
    short_lived_token=short_token.access_token,
)
print(f"Long-lived token: {long_token.access_token}")
print(f"Expires in: {long_token.expires_in} seconds")

# Step 4: Refresh token before expiry
refreshed = client.auth.refresh_long_lived_token(long_token.access_token)
```

## API Reference

### Posts

```python
from threads.constants import ReplyControl

# Create and publish a text post
post = client.posts.create_and_publish(
    user_id="123",
    text="Hello, Threads!",
)

# Create post with image
post = client.posts.create_and_publish(
    user_id="123",
    text="Check out this photo!",
    image_url="https://example.com/image.jpg",
)

# Create post with video
post = client.posts.create_and_publish(
    user_id="123",
    text="Watch this video!",
    video_url="https://example.com/video.mp4",
    wait_for_ready=True,  # Wait for video processing
)

# Control who can reply
post = client.posts.create_and_publish(
    user_id="123",
    text="Only my followers can reply",
    reply_control=ReplyControl.ACCOUNTS_YOU_FOLLOW,
)

# Get a post
post = client.posts.get("post_id")

# Get user's posts
posts = client.posts.get_user_posts("user_id", limit=10)

# Delete a post
client.posts.delete("post_id")

# Check publishing limits (250 posts / 1000 replies per 24h)
limit = client.posts.get_publishing_limit("user_id")
print(f"Posts: {limit.quota_usage}/{limit.quota_total}")
print(f"Remaining: {limit.remaining_posts}")
```

### Replies

```python
# Reply to a post
reply = client.posts.create_and_publish(
    user_id="123",
    text="This is my reply!",
    reply_to_id="original_post_id",
)

# Get replies to a post
replies = client.replies.get_replies("post_id")

# Get user's replies
my_replies = client.replies.get_user_replies("user_id", limit=10)

# Get conversation thread
conversation = client.replies.get_conversation("post_id")

# Manage reply visibility
client.replies.hide("reply_id")
client.replies.unhide("reply_id")
```

### Media (Images, Videos, Carousels)

```python
# Create image container
container = client.media.create_image_container(
    user_id="123",
    image_url="https://example.com/image.jpg",
    text="Caption",
)

# Create video container
container = client.media.create_video_container(
    user_id="123",
    video_url="https://example.com/video.mp4",
    text="Video caption",
)

# Check container status (for videos)
status = client.media.get_container_status(container.id)
print(f"Status: {status.status}")  # IN_PROGRESS, FINISHED, ERROR

# Create carousel (multi-image post)
import time

# Step 1: Create child containers
child_ids = []
for image_url in image_urls:
    container = client.media.create_image_container(
        user_id="123",
        image_url=image_url,
        is_carousel_item=True,
    )
    # Wait for each child to be ready
    while True:
        status = client.media.get_container_status(container.id)
        if status.is_ready:
            child_ids.append(container.id)
            break
        if status.has_error:
            raise Exception(status.error_message)
        time.sleep(1)

# Step 2: Create carousel container
carousel = client.media.create_carousel_container(
    user_id="123",
    children=child_ids,
    text="Swipe to see more!",
)

# Step 3: Wait for carousel to be ready
while True:
    status = client.media.get_container_status(carousel.id)
    if status.is_ready:
        break
    time.sleep(1)

# Step 4: Publish
post = client.posts.publish("123", carousel.id)
```

### User Profile

```python
# Get current user's profile
me = client.users.get_me()
print(f"Username: {me.username}")
print(f"Bio: {me.biography}")

# Get another user's profile
user = client.users.get("user_id")
```

### Insights

```python
from threads.constants import MetricType

# Get post metrics
insights = client.insights.get_media_insights("post_id")
print(f"Views: {insights.views}")
print(f"Likes: {insights.likes}")
print(f"Replies: {insights.replies}")
print(f"Reposts: {insights.reposts}")
print(f"Quotes: {insights.quotes}")

# Get specific metrics
insights = client.insights.get_media_insights(
    "post_id",
    metrics=[MetricType.VIEWS, MetricType.LIKES],
)

# Get user-level insights
user_insights = client.insights.get_user_insights("user_id")
views = user_insights.get_metric("views")
followers = user_insights.get_metric("followers_count")
```

## Error Handling

```python
from threads.exceptions import (
    ThreadsAPIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ContainerError,
)

try:
    post = client.posts.create_and_publish(user_id="123", text="Hello!")
except AuthenticationError:
    print("Invalid or expired token")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except ContainerError as e:
    print(f"Media processing failed: {e.message}")
except ThreadsAPIError as e:
    print(f"API error: {e.message} (code: {e.error_code})")
```

## Logging

Enable logging to debug API calls:

```python
from threads import setup_logging
import logging

# Enable debug logging
setup_logging(level=logging.DEBUG)

# Or configure specific loggers
setup_logging(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

## Rate Limits

The Threads API has the following limits:
- **250 posts** per 24-hour rolling window
- **1000 replies** per 24-hour rolling window

Check your current usage:

```python
limit = client.posts.get_publishing_limit("user_id")
print(f"Posts used: {limit.quota_usage}/{limit.quota_total}")
print(f"Remaining posts: {limit.remaining_posts}")
```

## Development

```bash
# Clone the repository
git clone https://github.com/MetaThreads/meta-threads-sdk.git
cd meta-threads-sdk

# Install uv if you haven't
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/threads --cov-report=term-missing

# Run linter
uv run ruff check .

# Run type checker
uv run mypy src
```

## License

MIT License - see [LICENSE](LICENSE) for details.
