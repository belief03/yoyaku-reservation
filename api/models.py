"""
データベースモデル定義
Supabaseのテーブル構造に対応するPydanticモデル
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ReservationStatus(str, Enum):
    """予約ステータス"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class OrderStatus(str, Enum):
    """注文ステータス"""
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class CouponType(str, Enum):
    """クーポンタイプ"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SERVICE = "free_service"


class CampaignStatus(str, Enum):
    """キャンペーンステータス"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


# ベースモデル
class BaseDBModel(BaseModel):
    """データベースモデルのベースクラス"""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 顧客モデル
class Customer(BaseDBModel):
    """顧客モデル"""
    email: EmailStr
    phone: Optional[str] = None
    name: Optional[str] = None
    name_kana: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    total_visits: int = 0
    last_visit: Optional[datetime] = None


# スタイリストモデル
class Stylist(BaseDBModel):
    """スタイリストモデル"""
    name: str
    name_kana: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool = True
    working_hours: Optional[dict] = None  # JSON形式で保存


# サービスモデル
class Service(BaseDBModel):
    """サービスモデル"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: int
    price: int
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    display_order: int = 0


# 商品モデル
class Product(BaseDBModel):
    """商品モデル"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    price: int
    cost: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_active: bool = True
    display_order: int = 0


# 予約モデル
class Reservation(BaseDBModel):
    """予約モデル"""
    customer_id: str
    stylist_id: Optional[str] = None
    service_id: str
    reservation_datetime: datetime
    duration_minutes: int
    status: ReservationStatus = ReservationStatus.PENDING
    notes: Optional[str] = None
    reminder_sent: bool = False
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None


# 注文モデル
class Order(BaseDBModel):
    """注文モデル"""
    customer_id: str
    reservation_id: Optional[str] = None
    total_amount: int
    discount_amount: int = 0
    final_amount: int
    status: OrderStatus = OrderStatus.PENDING
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[dict]] = None  # JSON形式で保存


# 注文アイテムモデル
class OrderItem(BaseModel):
    """注文アイテム"""
    product_id: Optional[str] = None
    service_id: Optional[str] = None
    name: str
    quantity: int
    unit_price: int
    subtotal: int


# クーポンモデル
class Coupon(BaseDBModel):
    """クーポンモデル"""
    code: str
    name: str
    description: Optional[str] = None
    coupon_type: CouponType
    discount_value: int  # パーセンテージまたは固定金額
    min_purchase_amount: Optional[int] = None
    max_discount_amount: Optional[int] = None
    valid_from: datetime
    valid_until: datetime
    usage_limit: Optional[int] = None
    usage_count: int = 0
    is_active: bool = True
    applicable_services: Optional[List[str]] = None  # サービスIDのリスト


# クーポン使用履歴モデル
class CouponUsage(BaseDBModel):
    """クーポン使用履歴"""
    coupon_id: str
    customer_id: str
    order_id: str
    discount_amount: int
    used_at: datetime


# キャンペーンモデル
class Campaign(BaseDBModel):
    """キャンペーンモデル"""
    name: str
    description: Optional[str] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: datetime
    end_date: datetime
    target_audience: Optional[dict] = None  # JSON形式で保存
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    conditions: Optional[dict] = None  # JSON形式で保存
    is_active: bool = True


# ストレージファイルモデル
class StorageFile(BaseModel):
    """ストレージファイルモデル"""
    name: str
    path: str
    bucket: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None







