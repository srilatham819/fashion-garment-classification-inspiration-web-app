class AppError(Exception):
    """Base class for expected application errors."""


class NotFoundError(AppError):
    pass


class UploadValidationError(AppError):
    pass


class ClassificationError(AppError):
    pass

