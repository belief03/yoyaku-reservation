"""
キャンペーン管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.auth import get_current_shop
from api.schemas import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)
from api.models import CampaignStatus

router = APIRouter()


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーンを作成"""
    campaign_data = campaign.dict()
    campaign_data["status"] = CampaignStatus.DRAFT.value
    campaign_data["shop_id"] = current_shop["id"]
    result = db.table("campaigns").insert(campaign_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="キャンペーンの作成に失敗しました")
    
    return CampaignResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[CampaignStatus] = None,
    is_active: Optional[bool] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーン一覧を取得"""
    query = db.table("campaigns").select("*").eq("shop_id", current_shop["id"])
    
    if status:
        query = query.eq("status", status.value)
    if is_active is not None:
        query = query.eq("is_active", is_active)
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = query.order("created_at", desc=True).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/active")
async def list_active_campaigns(
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """アクティブなキャンペーン一覧を取得"""
    now = datetime.now().isoformat()
    
    # statusカラムが存在しない場合はis_activeのみでフィルタ
    try:
        result = db.table("campaigns").select("*").eq(
            "status", CampaignStatus.ACTIVE.value
        ).eq("is_active", True).eq("shop_id", current_shop["id"]).lte("start_date", now).gte("end_date", now).execute()
    except Exception:
        # statusカラムが存在しない場合
        result = db.table("campaigns").select("*").eq(
            "is_active", True
        ).eq("shop_id", current_shop["id"]).lte("start_date", now).gte("end_date", now).execute()
    
    return {"campaigns": result.data}


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーン詳細を取得"""
    result = db.table("campaigns").select("*").eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    return CampaignResponse(**result.data[0])


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーン情報を更新"""
    # キャンペーンの存在確認と所有権チェック
    existing = db.table("campaigns").select("*").eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    update_data = campaign_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("campaigns").update(update_data).eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="キャンペーン情報の更新に失敗しました")
    
    return CampaignResponse(**result.data[0])


@router.post("/{campaign_id}/activate", response_model=CampaignResponse)
async def activate_campaign(
    campaign_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーンを有効化"""
    result = db.table("campaigns").update({
        "status": CampaignStatus.ACTIVE.value,
        "is_active": True,
        "updated_at": datetime.now().isoformat()
    }).eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    return CampaignResponse(**result.data[0])


@router.post("/{campaign_id}/pause", response_model=CampaignResponse)
async def pause_campaign(
    campaign_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーンを一時停止"""
    result = db.table("campaigns").update({
        "status": CampaignStatus.PAUSED.value,
        "updated_at": datetime.now().isoformat()
    }).eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    return CampaignResponse(**result.data[0])


@router.post("/{campaign_id}/end", response_model=CampaignResponse)
async def end_campaign(
    campaign_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーンを終了"""
    result = db.table("campaigns").update({
        "status": CampaignStatus.ENDED.value,
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    return CampaignResponse(**result.data[0])


@router.delete("/{campaign_id}", response_model=MessageResponse)
async def delete_campaign(
    campaign_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """キャンペーンを削除（論理削除）"""
    result = db.table("campaigns").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", campaign_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="キャンペーンが見つかりません")
    
    return MessageResponse(message="キャンペーンを削除しました")


