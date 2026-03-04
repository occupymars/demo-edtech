"""Widget token generation for Fourbyfour in-app notifications."""

import hmac
import hashlib
import json
import base64
import time
from app.config import config


def generate_widget_token(user_id: str, expires_in: int = 86400) -> str:
    """
    Generate a signed token for the Fourbyfour widget.

    Args:
        user_id: The user ID to generate a token for
        expires_in: Token expiry in seconds (default 24 hours)

    Returns:
        A signed JWT-like token string
    """
    if not config.FOURBYFOUR_WIDGET_SECRET:
        return ""

    # Create payload
    payload = {
        "sub": user_id,
        "pid": config.FOURBYFOUR_PROJECT_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in,
    }

    # Encode header and payload
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()

    # Create signature
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        config.FOURBYFOUR_WIDGET_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

    return f"{header_b64}.{payload_b64}.{signature_b64}"
