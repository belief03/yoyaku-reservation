"""
商品管理APIルート
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
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    PaginationParams,
    PaginatedResponse,
    MessageResponse
)

router = APIRouter()


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品を作成"""
    product_data = product.dict()
    product_data["shop_id"] = current_shop["id"]
    result = db.table("products").insert(product_data).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="商品の作成に失敗しました")
    
    return ProductResponse(**result.data[0])


@router.get("/", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    in_stock: Optional[bool] = None,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品一覧を取得"""
    query = db.table("products").select("*").eq("shop_id", current_shop["id"])
    
    if category:
        query = query.eq("category", category)
    if is_active is not None:
        query = query.eq("is_active", is_active)
    if in_stock is not None:
        if in_stock:
            query = query.or_("stock_quantity.is.null,stock_quantity.gt.0")
        else:
            query = query.eq("stock_quantity", 0)
    
    # ページネーション
    from_index = (page - 1) * page_size
    to_index = from_index + page_size
    
    # display_orderカラムが存在しない場合はcreated_atでソート
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


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品詳細を取得"""
    result = db.table("products").select("*").eq("id", product_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    
    return ProductResponse(**result.data[0])


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品情報を更新"""
    # 商品の存在確認と所有権チェック
    existing = db.table("products").select("*").eq("id", product_id).eq("shop_id", current_shop["id"]).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    
    update_data = product_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    result = db.table("products").update(update_data).eq("id", product_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="商品情報の更新に失敗しました")
    
    return ProductResponse(**result.data[0])


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: str,
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品を削除（論理削除）"""
    result = db.table("products").update({
        "is_active": False,
        "updated_at": datetime.now().isoformat()
    }).eq("id", product_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    
    return MessageResponse(message="商品を削除しました")


@router.post("/{product_id}/stock")
async def update_stock(
    product_id: str,
    quantity: int = Query(..., description="在庫数量"),
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品の在庫を更新"""
    result = db.table("products").update({
        "stock_quantity": quantity,
        "updated_at": datetime.now().isoformat()
    }).eq("id", product_id).eq("shop_id", current_shop["id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    
    return ProductResponse(**result.data[0])


@router.get("/categories/list")
async def list_categories(
    current_shop: dict = Depends(get_current_shop),
    db: Client = Depends(get_db)
):
    """商品カテゴリ一覧を取得"""
    result = db.table("products").select("category").eq("shop_id", current_shop["id"]).execute()
    
    categories = set()
    for item in result.data:
        if item.get("category"):
            categories.add(item["category"])
    
    return {"categories": sorted(list(categories))}

