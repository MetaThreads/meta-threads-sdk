"""Constants for the Threads API SDK."""

from enum import StrEnum

# API Configuration
API_BASE_URL = "https://graph.threads.net"
API_VERSION = "v1.0"
OAUTH_BASE_URL = "https://threads.net/oauth"

# Rate Limits (rolling 24-hour window)
MAX_POSTS_PER_DAY = 250
MAX_REPLIES_PER_DAY = 1000

# Token Configuration
SHORT_LIVED_TOKEN_EXPIRY_SECONDS = 3600  # 1 hour
LONG_LIVED_TOKEN_EXPIRY_DAYS = 60


class Scope(StrEnum):
    """OAuth scopes for Threads API."""

    BASIC = "threads_basic"
    CONTENT_PUBLISH = "threads_content_publish"
    READ_REPLIES = "threads_read_replies"
    MANAGE_REPLIES = "threads_manage_replies"
    MANAGE_INSIGHTS = "threads_manage_insights"


class MediaType(StrEnum):
    """Supported media types for Threads posts."""

    TEXT = "TEXT"
    TEXT_POST = "TEXT_POST"  # API returns this for text-only posts
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL = "CAROUSEL"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"  # API returns this for published carousels


class ReplyControl(StrEnum):
    """Reply control settings for posts."""

    EVERYONE = "EVERYONE"
    ACCOUNTS_YOU_FOLLOW = "ACCOUNTS_YOU_FOLLOW"
    MENTIONED_ONLY = "MENTIONED_ONLY"


class MetricType(StrEnum):
    """Available metrics for insights."""

    VIEWS = "views"
    LIKES = "likes"
    REPLIES = "replies"
    REPOSTS = "reposts"
    QUOTES = "quotes"
    FOLLOWERS_COUNT = "followers_count"
    FOLLOWER_DEMOGRAPHICS = "follower_demographics"


class ContainerStatus(StrEnum):
    """Media container status during publishing."""

    EXPIRED = "EXPIRED"
    ERROR = "ERROR"
    FINISHED = "FINISHED"
    IN_PROGRESS = "IN_PROGRESS"
    PUBLISHED = "PUBLISHED"


# Default HTTP Configuration
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
