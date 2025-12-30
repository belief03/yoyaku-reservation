"""
認証・認可システム
JWTトークンを使用した店舗認証
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from api.database import get_db
from api.logger import logger

# パスワードハッシュ用のコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer認証
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードを検証"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"パスワード検証エラー: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """パスワードをハッシュ化"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """JWTアクセストークンを生成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """JWTトークンを検証"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWTトークン検証エラー: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"トークン検証エラー: {str(e)}")
        return None


async def authenticate_shop(email: str, password: str, db: Client) -> Optional[dict]:
    """店舗の認証"""
    try:
        # 店舗を検索
        result = db.table("shops").select("*").eq("email", email).eq("is_active", True).execute()
        
        if not result.data or len(result.data) == 0:
            return None
        
        shop = result.data[0]
        
        # パスワードを検証
        # 既存のSHA256ハッシュとの互換性を保つため、両方をチェック
        password_hash = shop.get("password_hash")
        
        # bcryptハッシュの場合
        if password_hash.startswith("$2b$") or password_hash.startswith("$2a$"):
            if not verify_password(password, password_hash):
                return None
        else:
            # SHA256ハッシュの場合（既存データとの互換性）
            import hashlib
            if hashlib.sha256(password.encode()).hexdigest() != password_hash:
                return None
        
        return {
            "id": shop["id"],
            "email": shop["email"],
            "name": shop["name"],
            "admin_email": shop.get("admin_email"),
            "admin_name": shop.get("admin_name")
        }
    except Exception as e:
        logger.error(f"認証エラー: {str(e)}")
        return None


async def get_current_shop(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db)
) -> dict:
    """現在の認証済み店舗を取得"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証情報が無効です",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        logger.debug(f"トークン受信: {token[:20]}...")
        payload = verify_token(token)
        
        if payload is None:
            logger.error("トークンの検証に失敗しました")
            raise credentials_exception
        
        shop_id: str = payload.get("sub")
        if shop_id is None:
            raise credentials_exception
        
        # 店舗の存在確認とアクティブ状態の確認
        result = db.table("shops").select("*").eq("id", shop_id).eq("is_active", True).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="店舗が見つからないか、無効です"
            )
        
        shop = result.data[0]
        
        return {
            "id": shop["id"],
            "email": shop["email"],
            "name": shop["name"],
            "admin_email": shop.get("admin_email"),
            "admin_name": shop.get("admin_name")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"認証チェックエラー: {str(e)}")
        raise credentials_exception


def get_shop_id_filter(shop_id: str) -> dict:
    """shop_idでフィルタリングするためのクエリ条件を返す"""


def verify_admin_api_key(api_key: Optional[str] = None) -> bool:
    """システム管理者のAPIキーを検証"""
    if not settings.ADMIN_API_KEY:
        # 開発環境ではAPIキーが設定されていない場合は警告を出すが許可
        logger.warning("ADMIN_API_KEYが設定されていません。本番環境では必ず設定してください。")
        return True  # 開発環境では許可
    
    if not api_key:
        return False
    
    return api_key == settings.ADMIN_API_KEY


async def require_admin(
    x_admin_api_key: Optional[str] = None
) -> bool:
    """システム管理者の認証を要求"""
    from fastapi import Header
    
    if not verify_admin_api_key(x_admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この操作を実行するにはシステム管理者の権限が必要です"
        )
    return True
    return {"shop_id": shop_id}

