"""
認証APIルート
ログイン、ログアウト、トークン更新など
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client
from datetime import timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.auth import authenticate_shop, create_access_token, get_current_shop, get_password_hash
from api.logger import logger
from config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """ログインレスポンス"""
    access_token: str
    token_type: str = "bearer"
    shop_id: str
    shop_name: str
    admin_email: str
    admin_name: str


class ShopInfo(BaseModel):
    """店舗情報レスポンス"""
    id: str
    email: str
    name: str
    admin_email: str
    admin_name: str
    is_active: bool


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Client = Depends(get_db)
):
    """店舗ログイン"""
    try:
        # 認証
        shop = await authenticate_shop(login_data.email, login_data.password, db)
        
        if shop is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません"
            )
        
        # アクセストークンを生成
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": shop["id"], "email": shop["email"]},
            expires_delta=access_token_expires
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            shop_id=shop["id"],
            shop_name=shop["name"],
            admin_email=shop.get("admin_email", ""),
            admin_name=shop.get("admin_name", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ログインエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログインに失敗しました"
        )


@router.get("/me", response_model=ShopInfo)
async def get_current_shop_info(
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """現在のログイン中の店舗情報を取得"""
    try:
        result = db.table("shops").select("*").eq("id", current_shop["id"]).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="店舗が見つかりません"
            )
        
        shop = result.data[0]
        
        return ShopInfo(
            id=shop["id"],
            email=shop["email"],
            name=shop["name"],
            admin_email=shop.get("admin_email", ""),
            admin_name=shop.get("admin_name", ""),
            is_active=shop.get("is_active", True)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"店舗情報取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="店舗情報の取得に失敗しました"
        )


@router.post("/logout")
async def logout():
    """ログアウト（クライアント側でトークンを削除）"""
    return {"message": "ログアウトしました"}




