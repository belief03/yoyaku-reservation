"""
招待管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from supabase import Client
from datetime import datetime, timedelta, timezone
import secrets
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.email_service import get_email_service
from api.logger import logger
from api.auth import verify_admin_api_key

router = APIRouter()


class InvitationCreate(BaseModel):
    """招待作成モデル"""
    email: EmailStr
    shop_name: Optional[str] = None
    expires_in_days: int = 7  # デフォルト7日間有効


class InvitationResponse(BaseModel):
    """招待レスポンスモデル"""
    id: str
    email: str
    token: str
    invitation_url: str
    expires_at: datetime
    used: bool
    shop_name: Optional[str] = None
    created_at: datetime
    email_sent: Optional[bool] = None  # メール送信の成功/失敗状態


class InvitationAccept(BaseModel):
    """招待承認モデル"""
    token: str
    shop_name: str
    login_email: EmailStr  # ログイン用メールアドレス
    shop_password: str  # 初期パスワード
    admin_name: str
    admin_email: EmailStr


@router.post("/", response_model=InvitationResponse)
async def create_invitation(
    invitation: InvitationCreate,
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key"),
    db: Client = Depends(get_db)
):
    """新しい招待を作成（システム管理者のみ）"""
    # システム管理者の認証
    if not verify_admin_api_key(x_admin_api_key):
        raise HTTPException(
            status_code=403,
            detail="この操作を実行するにはシステム管理者の権限が必要です。X-Admin-API-Keyヘッダーを設定してください。"
        )
    try:
        # 既存の招待をチェック
        existing = db.table("invitations").select("*").eq(
            "email", invitation.email
        ).eq("used", False).execute()
        
        if existing.data and len(existing.data) > 0:
            # 有効な招待が既に存在する場合はエラー
            raise HTTPException(
                status_code=400,
                detail="このメールアドレスには既に有効な招待が送信されています"
            )
        
        # トークンを生成
        token = secrets.token_urlsafe(32)
        
        # 有効期限を設定
        expires_at = datetime.now(timezone.utc) + timedelta(days=invitation.expires_in_days)
        
        # 招待URLを生成
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        invitation_url = f"{base_url}/invite/{token}"
        
        # データベースに保存
        result = db.table("invitations").insert({
            "email": invitation.email,
            "token": token,
            "invitation_url": invitation_url,
            "expires_at": expires_at.isoformat(),
            "used": False,
            "shop_name": invitation.shop_name
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="招待の作成に失敗しました")
        
        invitation_data = result.data[0]
        
        # メールを送信
        email_sent = None
        try:
            email_service = get_email_service()
            
            # メール送信サービスが有効かチェック
            if not email_service.enabled:
                logger.error(
                    f"招待メール送信失敗: メール送信サービスが無効です。\n"
                    f"SMTP設定が不足しています。以下の環境変数を設定してください:\n"
                    f"- SMTP_HOST\n"
                    f"- SMTP_USER\n"
                    f"- SMTP_PASSWORD\n"
                    f"- EMAIL_FROM (オプション、SMTP_USERが使用されます)\n"
                    f"招待は作成されましたが、メールは送信されませんでした。"
                )
                email_sent = False
                # メール送信が無効でも招待は作成される（後で手動で送信可能）
            else:
                success = email_service.send_invitation_email(
                    to_email=invitation.email,
                    invitation_url=invitation_url,
                    shop_name=invitation.shop_name or "新しい店舗"
                )
                email_sent = success
                if success:
                    logger.info(f"招待メール送信成功: {invitation.email}")
                else:
                    logger.error(
                        f"招待メール送信失敗（招待は作成されました）: {invitation.email}\n"
                        f"招待URL: {invitation_url}\n"
                        f"ログを確認してSMTP設定を確認してください。"
                    )
        except Exception as e:
            email_sent = False
            logger.error(
                f"招待メール送信エラー（招待は作成されました）: {invitation.email}\n"
                f"エラー: {str(e)}\n"
                f"招待URL: {invitation_url}"
            )
            import traceback
            logger.error(f"エラー詳細: {traceback.format_exc()}")
        
        return InvitationResponse(
            id=str(invitation_data["id"]),
            email=invitation_data["email"],
            token=invitation_data["token"],
            invitation_url=invitation_data["invitation_url"],
            expires_at=datetime.fromisoformat(invitation_data["expires_at"].replace("Z", "+00:00")),
            used=invitation_data["used"],
            shop_name=invitation_data.get("shop_name"),
            created_at=datetime.fromisoformat(invitation_data["created_at"].replace("Z", "+00:00")),
            email_sent=email_sent
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"招待作成エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"招待の作成に失敗しました: {str(e)}")


@router.get("/verify/{token}")
async def verify_invitation(
    token: str,
    db: Client = Depends(get_db)
):
    """招待トークンを検証"""
    try:
        result = db.table("invitations").select("*").eq("token", token).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="招待が見つかりません")
        
        invitation = result.data[0]
        
        # 既に使用済みかチェック
        if invitation["used"]:
            raise HTTPException(status_code=400, detail="この招待は既に使用されています")
        
        # 有効期限をチェック
        expires_at = datetime.fromisoformat(invitation["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="この招待の有効期限が切れています")
        
        return {
            "valid": True,
            "email": invitation["email"],
            "shop_name": invitation.get("shop_name"),
            "expires_at": invitation["expires_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"招待検証エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"招待の検証に失敗しました: {str(e)}")


@router.post("/accept")
async def accept_invitation(
    accept_data: InvitationAccept,
    db: Client = Depends(get_db)
):
    """招待を承認して店舗アカウントを作成"""
    try:
        # トークンを検証
        result = db.table("invitations").select("*").eq("token", accept_data.token).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="招待が見つかりません")
        
        invitation = result.data[0]
        
        if invitation["used"]:
            raise HTTPException(status_code=400, detail="この招待は既に使用されています")
        
        expires_at = datetime.fromisoformat(invitation["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="この招待の有効期限が切れています")
        
        # 既存のアカウントをチェック（ログイン用メールアドレスでチェック）
        existing_shop = db.table("shops").select("*").eq("email", accept_data.login_email).execute()
        if existing_shop.data and len(existing_shop.data) > 0:
            shop = existing_shop.data[0]
            raise HTTPException(
                status_code=400,
                detail=f"このログイン用メールアドレス（{accept_data.login_email}）は既に店舗アカウントが登録されています。既存のアカウントでログインしてください。"
            )
        
        # 店舗アカウントを作成
        shop_id = secrets.token_urlsafe(16)
        
        # パスワードハッシュ（bcryptを使用）
        from api.auth import get_password_hash
        password_hash = get_password_hash(accept_data.shop_password)
        
        # shopsテーブルに店舗情報を保存
        shop_result = db.table("shops").insert({
            "id": shop_id,
            "name": accept_data.shop_name,
            "email": accept_data.login_email,  # ログイン用メールアドレスを使用
            "admin_email": accept_data.admin_email,
            "admin_name": accept_data.admin_name,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        
        if not shop_result.data:
            raise HTTPException(status_code=500, detail="店舗アカウントの作成に失敗しました")
        
        # 招待を使用済みにマーク
        db.table("invitations").update({
            "used": True,
            "used_at": datetime.now(timezone.utc).isoformat(),
            "shop_id": shop_id
        }).eq("token", accept_data.token).execute()
        
        # デフォルト設定を作成（settingsテーブルが存在する場合のみ）
        try:
            default_settings = {
                "shop_name": accept_data.shop_name,
                "primary_color": "#667eea",
                "secondary_color": "#764ba2"
            }
            
            db.table("settings").insert({
                "key": f"shop_settings_{shop_id}",
                "value": str(default_settings).replace("'", '"')
            }).execute()
        except Exception as e:
            logger.warning(f"設定の作成に失敗しました（店舗アカウントは作成されました）: {str(e)}")
        
        return {
            "success": True,
            "shop_id": shop_id,
            "message": "店舗アカウントが作成されました",
            "login_url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/admin/login"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"招待承認エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"招待の承認に失敗しました: {str(e)}")


@router.get("/", response_model=List[InvitationResponse])
async def list_invitations(
    used: Optional[bool] = Query(None),
    x_admin_api_key: Optional[str] = Header(None, alias="X-Admin-API-Key"),
    db: Client = Depends(get_db)
):
    """招待一覧を取得（システム管理者のみ）"""
    # システム管理者の認証
    if not verify_admin_api_key(x_admin_api_key):
        raise HTTPException(
            status_code=403,
            detail="この操作を実行するにはシステム管理者の権限が必要です。X-Admin-API-Keyヘッダーを設定してください。"
        )
    try:
        query = db.table("invitations").select("*")
        
        if used is not None:
            query = query.eq("used", used)
        
        result = query.order("created_at", desc=True).execute()
        
        return [
            InvitationResponse(
                id=str(inv["id"]),
                email=inv["email"],
                token=inv["token"],
                invitation_url=inv["invitation_url"],
                expires_at=datetime.fromisoformat(inv["expires_at"].replace("Z", "+00:00")),
                used=inv["used"],
                shop_name=inv.get("shop_name"),
                created_at=datetime.fromisoformat(inv["created_at"].replace("Z", "+00:00")),
                email_sent=inv.get("email_sent")  # データベースに保存されていない場合はNone
            )
            for inv in result.data
        ]
    except Exception as e:
        logger.error(f"招待一覧取得エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=f"招待一覧の取得に失敗しました: {str(e)}")


