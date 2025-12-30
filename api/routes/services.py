"""
サービス管理APIルート
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
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービスを作成"""
    service_data = service.dict()
    service_data["shop_id"] = current_shop["id"]
    result = db.table("services").insert(service_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="サービスの作成に失敗しました")
    
    return ServiceResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_services(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービス一覧を取得"""
    query = db.table("services").select("*").eq("shop_id", current_shop["id"])
    
    if category:
        query = query.eq("category", category)
    if is_active is not None:
        query = query.eq("is_active", is_active)
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    # ソートなしで実行（created_atカラムが存在しない可能性があるため）
    result = query.execute()
    
    total = len(result.data)
    items = result.data[from_index:to_index]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービス詳細を取得"""
    result = db.table("services").select("*").eq("id", service_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="サービスが見つかりません")
    
    return ServiceResponse(**result.data[0])


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    service_update: ServiceUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービス情報を更新"""
    # サービスの存在確認と所有権チェック
    existing = db.table("services").select("*").eq("id", service_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="サービスが見つかりません")
    
    update_data = service_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("services").update(update_data).eq("id", service_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="サービス情報の更新に失敗しました")
    
    return ServiceResponse(**result.data[0])


@router.delete("/{service_id}", response_model=MessageResponse)
async def delete_service(
    service_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービスを削除（論理削除）"""
    result = db.table("services").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", service_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="サービスが見つかりません")
    
    return MessageResponse(message="サービスを削除しました")


@router.get("/categories/list")
async def list_categories(
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """サービスカテゴリ一覧を取得"""
    result = db.table("services").select("category").eq("shop_id", current_shop["id"]).execute()
    
    categories = set()
    for item in result.data:
        if item.get("category"):
            categories.add(item["category"])
    
    return {"categories": sorted(list(categories))}


