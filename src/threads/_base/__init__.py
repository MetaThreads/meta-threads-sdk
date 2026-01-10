"""Base classes defining interfaces for the Threads SDK."""

from threads._base.auth import BaseAuthClient
from threads._base.client import BaseThreadsClient
from threads._base.insights import BaseInsightsClient
from threads._base.media import BaseMediaClient
from threads._base.posts import BasePostsClient
from threads._base.replies import BaseRepliesClient
from threads._base.webhooks import BaseWebhooksClient

__all__ = [
    "BaseAuthClient",
    "BaseInsightsClient",
    "BaseMediaClient",
    "BasePostsClient",
    "BaseRepliesClient",
    "BaseThreadsClient",
    "BaseWebhooksClient",
]
