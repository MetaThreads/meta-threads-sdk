"""Tests for exception handling."""

import pytest

from threads.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ThreadsAPIError,
    ThreadsError,
    ValidationError,
    raise_for_error,
)


class TestThreadsError:
    """Tests for base ThreadsError."""

    def test_create_error(self):
        error = ThreadsError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"

    def test_error_with_details(self):
        error = ThreadsError("Error", key="value")
        assert error.details == {"key": "value"}


class TestThreadsAPIError:
    """Tests for ThreadsAPIError."""

    def test_create_api_error(self):
        error = ThreadsAPIError(
            "API Error",
            status_code=400,
            error_code=100,
            fbtrace_id="ABC123",
        )
        assert error.status_code == 400
        assert error.error_code == 100
        assert error.fbtrace_id == "ABC123"

    def test_str_representation(self):
        error = ThreadsAPIError(
            "API Error",
            status_code=400,
            error_code=100,
        )
        result = str(error)
        assert "API Error" in result
        assert "400" in result
        assert "100" in result


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_with_retry_after(self):
        error = RateLimitError(
            "Rate limited",
            retry_after=60,
        )
        assert error.retry_after == 60


class TestRaiseForError:
    """Tests for raise_for_error function."""

    def test_authentication_error_401(self):
        response = {
            "error": {
                "message": "Invalid token",
                "code": 190,
            }
        }
        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_error(response, 401)
        assert exc_info.value.status_code == 401

    def test_authentication_error_by_code(self):
        response = {
            "error": {
                "message": "Token expired",
                "code": 190,
            }
        }
        with pytest.raises(AuthenticationError):
            raise_for_error(response, 400)

    def test_authorization_error(self):
        response = {
            "error": {
                "message": "Permission denied",
                "code": 200,
            }
        }
        with pytest.raises(AuthorizationError):
            raise_for_error(response, 403)

    def test_rate_limit_error(self):
        response = {
            "error": {
                "message": "Too many requests",
                "code": 4,
            }
        }
        with pytest.raises(RateLimitError):
            raise_for_error(response, 429)

    def test_not_found_error(self):
        response = {
            "error": {
                "message": "Post not found",
            }
        }
        with pytest.raises(NotFoundError):
            raise_for_error(response, 404)

    def test_generic_api_error(self):
        response = {
            "error": {
                "message": "Unknown error",
                "code": 999,
            }
        }
        with pytest.raises(ThreadsAPIError):
            raise_for_error(response, 500)


class TestValidationError:
    """Tests for ValidationError."""

    def test_create_validation_error(self):
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert isinstance(error, ThreadsError)
