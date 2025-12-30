"""
カスタム例外クラス
アプリケーション固有の例外を定義
"""
from fastapi import HTTPException, status


class YoyakuException(HTTPException):
    """ベース例外クラス"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(YoyakuException):
    """バリデーションエラー"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotFoundError(YoyakuException):
    """リソースが見つからないエラー"""
    def __init__(self, resource: str, resource_id: str = None):
        detail = f"{resource}が見つかりません"
        if resource_id:
            detail += f" (ID: {resource_id})"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(YoyakuException):
    """競合エラー（重複など）"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedError(YoyakuException):
    """認証エラー"""
    def __init__(self, detail: str = "認証が必要です"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenError(YoyakuException):
    """権限エラー"""
    def __init__(self, detail: str = "この操作を実行する権限がありません"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BusinessLogicError(YoyakuException):
    """ビジネスロジックエラー"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)






