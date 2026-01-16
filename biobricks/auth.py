"""
GitHub authentication for BioBricks private repositories.

Supports:
1. Personal Access Token (PAT) - manual token entry
2. GitHub OAuth Device Flow - browser-based login (requires OAuth app)
"""

import json
import time
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests

from .logger import logger

# GitHub OAuth App credentials (register at https://github.com/settings/applications/new)
# For device flow, set "Device authorization" to enabled
GITHUB_CLIENT_ID = "Ov23liQH9qJK7QWjvdXm"  # BioBricks GitHub OAuth App
GITHUB_DEVICE_AUTH_URL = "https://github.com/login/device/code"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"

# Token storage
AUTH_FILE = Path.home() / ".biobricks_auth"


def _read_auth() -> Dict[str, Any]:
    """Read auth tokens from storage."""
    if not AUTH_FILE.exists():
        return {}
    try:
        return json.loads(AUTH_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def _write_auth(auth_data: Dict[str, Any]) -> None:
    """Write auth tokens to storage."""
    AUTH_FILE.write_text(json.dumps(auth_data, indent=2))
    AUTH_FILE.chmod(0o600)  # Restrict permissions


def get_github_token() -> Optional[str]:
    """Get the stored GitHub token."""
    auth = _read_auth()

    # Check if token exists and is not expired
    if "github_token" in auth:
        expires_at = auth.get("github_expires_at")
        if expires_at:
            if datetime.fromisoformat(expires_at) > datetime.now():
                return auth["github_token"]
            # Token expired, try to refresh
            if "github_refresh_token" in auth:
                return refresh_github_token()
        else:
            # PAT tokens don't expire
            return auth["github_token"]

    return None


def set_github_token(token: str, refresh_token: Optional[str] = None,
                     expires_in: Optional[int] = None) -> None:
    """Store a GitHub token."""
    auth = _read_auth()
    auth["github_token"] = token

    if refresh_token:
        auth["github_refresh_token"] = refresh_token

    if expires_in:
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        auth["github_expires_at"] = expires_at.isoformat()
    else:
        # Remove expiration for PAT tokens
        auth.pop("github_expires_at", None)
        auth.pop("github_refresh_token", None)

    _write_auth(auth)


def clear_github_token() -> None:
    """Remove stored GitHub tokens."""
    auth = _read_auth()
    auth.pop("github_token", None)
    auth.pop("github_refresh_token", None)
    auth.pop("github_expires_at", None)
    auth.pop("github_user", None)
    _write_auth(auth)


def refresh_github_token() -> Optional[str]:
    """Refresh an expired OAuth token."""
    auth = _read_auth()
    refresh_token = auth.get("github_refresh_token")

    if not refresh_token:
        return None

    try:
        response = requests.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

        if "access_token" in data:
            set_github_token(
                data["access_token"],
                data.get("refresh_token", refresh_token),
                data.get("expires_in"),
            )
            return data["access_token"]
    except Exception as e:
        logger.warning(f"Failed to refresh token: {e}")

    return None


def validate_github_token(token: str) -> Dict[str, Any]:
    """Validate a GitHub token and get user info."""
    try:
        response = requests.get(
            f"{GITHUB_API_URL}/user",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid or expired GitHub token")
        raise


def check_repo_access(token: str, owner: str = "biobricks-ai", repo: str = None) -> bool:
    """Check if the token has access to private biobricks repos."""
    try:
        # Check access to a known repo or list private repos
        if repo:
            url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
        else:
            url = f"{GITHUB_API_URL}/orgs/{owner}/repos?type=private"

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
        )
        return response.status_code == 200
    except Exception:
        return False


def login_with_pat(token: str) -> Dict[str, Any]:
    """Login with a Personal Access Token."""
    user = validate_github_token(token)
    set_github_token(token)

    # Store username
    auth = _read_auth()
    auth["github_user"] = user.get("login")
    _write_auth(auth)

    return user


def login_with_device_flow() -> Dict[str, Any]:
    """Login using GitHub's device flow (browser-based)."""
    # Step 1: Request device and user codes
    response = requests.post(
        GITHUB_DEVICE_AUTH_URL,
        data={
            "client_id": GITHUB_CLIENT_ID,
            "scope": "repo",  # Access to private repos
        },
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    data = response.json()

    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data["verification_uri"]
    expires_in = data["expires_in"]
    interval = data.get("interval", 5)

    # Step 2: Show user the code and open browser
    print(f"\nTo authenticate, visit: {verification_uri}")
    print(f"Enter code: {user_code}\n")

    # Try to open browser automatically
    try:
        webbrowser.open(verification_uri)
    except Exception:
        pass

    # Step 3: Poll for token
    print("Waiting for authorization...")
    start_time = time.time()

    while time.time() - start_time < expires_in:
        time.sleep(interval)

        response = requests.post(
            GITHUB_TOKEN_URL,
            data={
                "client_id": GITHUB_CLIENT_ID,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            headers={"Accept": "application/json"},
        )

        token_data = response.json()

        if "access_token" in token_data:
            # Success!
            set_github_token(
                token_data["access_token"],
                token_data.get("refresh_token"),
                token_data.get("expires_in"),
            )

            user = validate_github_token(token_data["access_token"])
            auth = _read_auth()
            auth["github_user"] = user.get("login")
            _write_auth(auth)

            return user

        error = token_data.get("error")
        if error == "authorization_pending":
            continue
        elif error == "slow_down":
            interval += 5
        elif error == "expired_token":
            raise TimeoutError("Authorization expired. Please try again.")
        elif error == "access_denied":
            raise PermissionError("Authorization was denied.")
        else:
            raise RuntimeError(f"Authentication failed: {error}")

    raise TimeoutError("Authorization timed out. Please try again.")


def get_auth_status() -> Dict[str, Any]:
    """Get current authentication status."""
    auth = _read_auth()
    token = get_github_token()

    status = {
        "authenticated": token is not None,
        "user": auth.get("github_user"),
        "has_refresh_token": "github_refresh_token" in auth,
    }

    if token:
        try:
            user = validate_github_token(token)
            status["user"] = user.get("login")
            status["valid"] = True
        except Exception:
            status["valid"] = False

    return status


def get_authenticated_git_url(url: str) -> str:
    """Convert a GitHub URL to use token authentication."""
    token = get_github_token()
    if not token:
        return url

    # Handle HTTPS URLs
    if url.startswith("https://github.com/"):
        # Insert token into URL: https://token@github.com/...
        return url.replace("https://github.com/", f"https://{token}@github.com/")

    return url


def get_git_credentials() -> Optional[tuple]:
    """Get credentials for git credential helper."""
    token = get_github_token()
    if token:
        auth = _read_auth()
        username = auth.get("github_user", "x-access-token")
        return (username, token)
    return None
