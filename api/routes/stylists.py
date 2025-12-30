"""
スタイリスト管理APIルート
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
    StylistCreate,
    StylistUpdate,
    StylistResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/", response_model=StylistResponse)
async def create_stylist(
    stylist: StylistCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリストを作成"""
    stylist_data = stylist.dict()
    stylist_data["shop_id"] = current_shop["id"]
    result = db.table("stylists").insert(stylist_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="スタイリストの作成に失敗しました")
    
    return StylistResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_stylists(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    specialty: Optional[str] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリスト一覧を取得"""
    query = db.table("stylists").select("*").eq("shop_id", current_shop["id"])
    
    if is_active is not None:
        query = query.eq("is_active", is_active)
    if specialty:
        query = query.eq("specialty", specialty)
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = query.order("created_at", desc=False).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{stylist_id}", response_model=StylistResponse)
async def get_stylist(
    stylist_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリスト詳細を取得"""
    result = db.table("stylists").select("*").eq("id", stylist_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="スタイリストが見つかりません")
    
    # IDを文字列に変換（データベースが整数型の場合）
    data = result.data[0].copy()
    if isinstance(data.get("id"), int):
        data["id"] = str(data["id"])
    
    return StylistResponse(**data)


@router.patch("/{stylist_id}", response_model=StylistResponse)
async def update_stylist(
    stylist_id: str,
    stylist_update: StylistUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリスト情報を更新"""
    # スタイリストの存在確認と所有権チェック
    existing = db.table("stylists").select("*").eq("id", stylist_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="スタイリストが見つかりません")
    
    update_data = stylist_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("stylists").update(update_data).eq("id", stylist_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="スタイリスト情報の更新に失敗しました")
    
    return StylistResponse(**result.data[0])


@router.delete("/{stylist_id}", response_model=MessageResponse)
async def delete_stylist(
    stylist_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリストを削除（論理削除）"""
    result = db.table("stylists").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", stylist_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="スタイリストが見つかりません")
    
    return MessageResponse(message="スタイリストを削除しました")


@router.get("/{stylist_id}/reservations")
async def get_stylist_reservations(
    stylist_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """スタイリストの予約一覧を取得"""
    # スタイリストの存在確認と所有権チェック
    stylist = db.table("stylists").select("*").eq("id", stylist_id).eq("shop_id", current_shop["id"]).execute()
    if not stylist.data:
        raise HTTPException(status_code=404, detail="スタイリストが見つかりません")
    
    # 予約の取得
    query = db.table("reservations").select("*").eq("stylist_id", stylist_id).eq("shop_id", current_shop["id"])
    
    if start_date:
        query = query.gte("reservation_datetime", start_date.isoformat())
    if end_date:
        query = query.lte("reservation_datetime", end_date.isoformat())
    
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    result = query.order("reservation_datetime", desc=False).execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


