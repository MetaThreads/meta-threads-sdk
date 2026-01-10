# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-10

### Added

- Initial release
- Synchronous `ThreadsClient` for blocking operations
- Asynchronous `AsyncThreadsClient` for async/await support
- Full OAuth 2.0 authentication flow
  - Authorization URL generation
  - Code exchange for short-lived tokens
  - Long-lived token exchange
  - Token refresh
- Post management
  - Create text posts
  - Create image posts
  - Create video posts
  - Create carousel posts
  - Get post details
  - Get user posts with pagination
  - Publishing rate limit tracking
- Media container operations
  - Create image containers
  - Create video containers
  - Create carousel containers
  - Check container status
- Insights API
  - Get media insights (views, likes, replies, reposts, quotes)
  - Get user insights
  - Convenience methods for common metrics
- Reply management
  - Get replies to posts
  - Get conversation threads
  - Hide/unhide replies
  - Get user's replies
- Webhook support
  - Subscribe to events
  - Unsubscribe
  - Get subscriptions
  - Verify webhook challenges
  - Parse webhook payloads
- Comprehensive exception hierarchy
- Input validation utilities
- Rate limiting utilities
- Full type hints (PEP 561 compliant)
- Pydantic models for all API responses
