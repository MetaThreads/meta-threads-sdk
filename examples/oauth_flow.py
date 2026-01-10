"""Example: Complete OAuth 2.0 authentication flow."""

import os
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from threads import ThreadsClient
from threads.constants import Scope

# App credentials (from Meta Developer Portal)
CLIENT_ID = os.environ["THREADS_CLIENT_ID"]
CLIENT_SECRET = os.environ["THREADS_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8000/callback"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    auth_code: str | None = None

    def do_GET(self) -> None:
        """Handle the OAuth callback."""
        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            params = parse_qs(parsed.query)

            if "code" in params:
                OAuthCallbackHandler.auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Authorization successful!</h1>"
                    b"<p>You can close this window.</p></body></html>"
                )
            elif "error" in params:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                error = params.get("error", ["Unknown"])[0]
                self.wfile.write(
                    f"<html><body><h1>Error: {error}</h1></body></html>".encode()
                )
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:
        """Suppress default logging."""
        pass


def run_oauth_flow() -> dict[str, str]:
    """Run the complete OAuth flow and return tokens."""
    # Create a client (without token for auth operations)
    client = ThreadsClient(access_token="")

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Step 1: Generate authorization URL
    auth_url = client.auth.get_authorization_url(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scopes=[
            Scope.BASIC,
            Scope.CONTENT_PUBLISH,
            Scope.READ_REPLIES,
            Scope.MANAGE_REPLIES,
            Scope.MANAGE_INSIGHTS,
        ],
        state=state,
    )

    print("=" * 60)
    print("STEP 1: Open this URL in your browser to authorize:")
    print(auth_url)
    print("=" * 60)

    # Step 2: Start local server to receive callback
    print("\nWaiting for authorization callback...")
    server = HTTPServer(("localhost", 8000), OAuthCallbackHandler)

    while OAuthCallbackHandler.auth_code is None:
        server.handle_request()

    auth_code = OAuthCallbackHandler.auth_code
    print(f"\nReceived authorization code: {auth_code[:20]}...")

    # Step 3: Exchange code for short-lived token
    print("\nExchanging code for short-lived token...")
    short_token = client.auth.exchange_code(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        code=auth_code,
    )
    print(f"Short-lived token obtained! User ID: {short_token.user_id}")

    # Step 4: Exchange for long-lived token
    print("\nExchanging for long-lived token...")
    long_token = client.auth.get_long_lived_token(
        client_secret=CLIENT_SECRET,
        short_lived_token=short_token.access_token,
    )
    print(f"Long-lived token obtained! Expires at: {long_token.expires_at}")

    client.close()

    return {
        "access_token": long_token.access_token,
        "user_id": short_token.user_id,
        "expires_at": str(long_token.expires_at),
    }


def refresh_existing_token(access_token: str) -> str:
    """Refresh an existing long-lived token."""
    client = ThreadsClient(access_token=access_token)

    refreshed = client.auth.refresh_token(access_token)
    print(f"Token refreshed! New expiry in {refreshed.expires_in} seconds")

    client.close()
    return refreshed.access_token


if __name__ == "__main__":
    tokens = run_oauth_flow()
    print("\n" + "=" * 60)
    print("AUTHENTICATION COMPLETE!")
    print("=" * 60)
    print(f"Access Token: {tokens['access_token'][:50]}...")
    print(f"User ID: {tokens['user_id']}")
    print(f"Expires At: {tokens['expires_at']}")
    print("\nSave these securely in environment variables!")
