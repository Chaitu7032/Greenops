from fastapi import HTTPException, status


class GreenOpsException(Exception):
    """Base exception for all GreenOps domain errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class WebhookVerificationError(GreenOpsException):
    """Raised when GitHub webhook signature verification fails."""
    pass


class DuplicateWebhookDeliveryError(GreenOpsException):
    """Raised when a webhook delivery ID has already been received and processed."""
    pass


class PolicyViolationError(GreenOpsException):
    """Raised when a CI run violates strict blocking policy rules."""
    pass


class GridServiceError(GreenOpsException):
    """Raised when grid carbon intensity retrieval fails."""
    pass
