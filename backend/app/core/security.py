import hmac
import hashlib
from typing import Optional


def verify_github_signature(payload_body: bytes, secret: str, signature_header: Optional[str]) -> bool:
    """
    Constant-time validation of GitHub HMAC-SHA256 signature header.
    Format of signature_header: sha256=<hex_digest>
    """
    if not signature_header or not secret:
        return False

    parts = signature_header.split("=", 1)
    if len(parts) != 2 or parts[0] != "sha256":
        return False

    expected_signature = parts[1]
    mac = hmac.new(secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)
