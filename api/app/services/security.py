from __future__ import annotations
import hmac
import hashlib
from app.core.config import get_settings


def verify_webhook_signature(body: bytes, signature: str | None) -> bool:
    if not signature:
        return False
    secret = get_settings().webhook_signing_secret.encode()
    mac = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)
