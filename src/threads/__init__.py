"""Unofficial Python client for Meta's Threads API.

This package provides both synchronous and asynchronous clients for
interacting with the Threads API.

Example (Sync):
    ```python
    from threads import ThreadsClient

    with ThreadsClient(access_token="your_token") as client:
        # Post a text thread
        post = client.posts.create_and_publish(
            user_id="your_user_id",
            text="Hello from Threads SDK!",
        )
        print(f"Published: {post.permalink}")

        # Get insights
        insights = client.insights.get_media_insights(post.id)
        print(f"Views: {insights.views}")
    ```

Example (Async):
    ```python
    from threads import AsyncThreadsClient

    async with AsyncThreadsClient(access_token="your_token") as client:
        post = await client.posts.create_and_publish(
            user_id="your_user_id",
            text="Hello from Threads SDK!",
        )
    ```
"""

from threads._async.client import AsyncThreadsClient
from threads._sync.client import ThreadsClient
from threads._utils.logger import get_logger, setup_logging
from threads.constants import (
    ContainerStatus,
    MediaType,
    MetricType,
    ReplyControl,
    Scope,
)
from threads.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ContainerError,
    MediaError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ThreadsAPIError,
    ThreadsError,
    TimeoutError,
    ValidationError,
    WebhookError,
)
from threads.models import (
    Insight,
    InsightsResponse,
    LongLivedToken,
    MediaContainer,
    MediaContainerStatus,
    Post,
    PublishingLimit,
    RefreshedToken,
    ShortLivedToken,
    User,
    UserInsightsResponse,
    UserProfile,
    WebhookEvent,
    WebhookPayload,
    WebhookSubscription,
)

__version__ = "0.2.1"

__all__ = [
    # Clients
    "AsyncThreadsClient",
    "ThreadsClient",
    # Logging
    "get_logger",
    "setup_logging",
    # Constants/Enums
    "ContainerStatus",
    "MediaType",
    "MetricType",
    "ReplyControl",
    "Scope",
    # Exceptions
    "AuthenticationError",
    "AuthorizationError",
    "ContainerError",
    "MediaError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "ThreadsAPIError",
    "ThreadsError",
    "TimeoutError",
    "ValidationError",
    "WebhookError",
    # Models - Auth
    "LongLivedToken",
    "RefreshedToken",
    "ShortLivedToken",
    # Models - Insights
    "Insight",
    "InsightsResponse",
    "UserInsightsResponse",
    # Models - Media
    "MediaContainer",
    "MediaContainerStatus",
    # Models - Post
    "Post",
    "PublishingLimit",
    # Models - User
    "User",
    "UserProfile",
    # Models - Webhook
    "WebhookEvent",
    "WebhookPayload",
    "WebhookSubscription",
    # Version
    "__version__",
]
