class AppError(Exception):
    """Base application error."""


class CsvResolutionError(AppError):
    """Raised when no usable CSV file can be resolved."""


class CsvDataError(AppError):
    """Raised when CSV content is invalid for the expected schema."""


class InsufficientAccountsError(AppError):
    """Raised when not enough unused accounts remain."""


class BrowserFlowNotImplementedError(AppError):
    """Raised while the browser flow is still being scaffolded."""


class BrowserStepError(AppError):
    """Raised when a browser automation step fails."""

    def __init__(self, status: str, step: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.step = step
