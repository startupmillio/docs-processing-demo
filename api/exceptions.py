from fastapi import HTTPException
from starlette import status


class BadRequestException(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )


class ForbiddenException(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )


class NotFoundException(HTTPException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
