"""Tests for Pydantic models."""

from datetime import datetime, timedelta

from threads.constants import ContainerStatus, MediaType, MetricType
from threads.models.auth import LongLivedToken, ShortLivedToken
from threads.models.insights import Insight, InsightsResponse
from threads.models.media import MediaContainer, MediaContainerStatus
from threads.models.post import Post, PublishingLimit
from threads.models.user import User, UserProfile


class TestShortLivedToken:
    """Tests for ShortLivedToken model."""

    def test_create_token(self):
        token = ShortLivedToken(
            access_token="test_token",
            user_id="123",
        )
        assert token.access_token == "test_token"
        assert token.user_id == "123"

    def test_is_expired_fresh_token(self):
        token = ShortLivedToken(
            access_token="test_token",
            user_id="123",
        )
        assert token.is_expired is False

    def test_is_expired_old_token(self):
        token = ShortLivedToken(
            access_token="test_token",
            user_id="123",
            created_at=datetime.now() - timedelta(hours=2),
        )
        assert token.is_expired is True


class TestLongLivedToken:
    """Tests for LongLivedToken model."""

    def test_create_token(self):
        token = LongLivedToken(
            access_token="test_token",
            expires_in=5184000,  # 60 days
        )
        assert token.access_token == "test_token"
        assert token.token_type == "bearer"

    def test_expires_at(self):
        token = LongLivedToken(
            access_token="test_token",
            expires_in=3600,
        )
        expected = token.created_at + timedelta(seconds=3600)
        assert abs((token.expires_at - expected).total_seconds()) < 1


class TestMediaContainer:
    """Tests for MediaContainer model."""

    def test_create_container(self):
        container = MediaContainer(id="container_123")
        assert container.id == "container_123"


class TestMediaContainerStatus:
    """Tests for MediaContainerStatus model."""

    def test_is_ready_finished(self):
        status = MediaContainerStatus(
            id="123",
            status=ContainerStatus.FINISHED,
        )
        assert status.is_ready is True
        assert status.has_error is False

    def test_has_error(self):
        status = MediaContainerStatus(
            id="123",
            status=ContainerStatus.ERROR,
            error_message="Processing failed",
        )
        assert status.is_ready is False
        assert status.has_error is True

    def test_in_progress(self):
        status = MediaContainerStatus(
            id="123",
            status=ContainerStatus.IN_PROGRESS,
        )
        assert status.is_ready is False
        assert status.has_error is False


class TestPost:
    """Tests for Post model."""

    def test_create_text_post(self):
        post = Post(
            id="post_123",
            media_type=MediaType.TEXT,
            text="Hello, Threads!",
        )
        assert post.id == "post_123"
        assert post.media_type == MediaType.TEXT
        assert post.text == "Hello, Threads!"

    def test_create_image_post(self):
        post = Post(
            id="post_123",
            media_type=MediaType.IMAGE,
            media_url="https://example.com/image.jpg",
        )
        assert post.media_type == MediaType.IMAGE
        assert post.media_url == "https://example.com/image.jpg"


class TestPublishingLimit:
    """Tests for PublishingLimit model."""

    def test_remaining_posts(self):
        limit = PublishingLimit(
            quota_usage=100,
            quota_total=250,
        )
        assert limit.remaining_posts == 150

    def test_remaining_posts_at_limit(self):
        limit = PublishingLimit(
            quota_usage=250,
            quota_total=250,
        )
        assert limit.remaining_posts == 0

    def test_remaining_replies(self):
        limit = PublishingLimit(
            quota_usage=100,
            reply_quota_usage=500,
            reply_quota_total=1000,
        )
        assert limit.remaining_replies == 500


class TestInsight:
    """Tests for Insight model."""

    def test_value_property(self):
        insight = Insight(
            name=MetricType.VIEWS,
            period="lifetime",
            values=[{"value": 1000}],
        )
        assert insight.value == 1000

    def test_value_empty(self):
        insight = Insight(
            name=MetricType.VIEWS,
            period="lifetime",
            values=[],
        )
        assert insight.value == 0


class TestInsightsResponse:
    """Tests for InsightsResponse model."""

    def test_get_metrics(self):
        response = InsightsResponse(
            data=[
                Insight(
                    name=MetricType.VIEWS,
                    period="lifetime",
                    values=[{"value": 1000}],
                ),
                Insight(
                    name=MetricType.LIKES,
                    period="lifetime",
                    values=[{"value": 50}],
                ),
            ]
        )
        assert response.views == 1000
        assert response.likes == 50
        assert response.replies == 0  # Not in response


class TestUser:
    """Tests for User model."""

    def test_create_user(self):
        user = User(
            id="123",
            username="testuser",
            name="Test User",
        )
        assert user.id == "123"
        assert user.username == "testuser"


class TestUserProfile:
    """Tests for UserProfile model."""

    def test_create_profile(self):
        profile = UserProfile(
            id="123",
            username="testuser",
            follower_count=1000,
            following_count=500,
        )
        assert profile.follower_count == 1000
        assert profile.following_count == 500
