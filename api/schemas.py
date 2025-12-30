"""
APIリクエスト/レスポンススキーマ定義
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from api.models import (
    ReservationStatus, OrderStatus, CouponType, CampaignStatus
)


# ==================== 顧客スキーマ ====================
class CustomerBase(BaseModel):
    """顧客ベーススキーマ"""
    email: EmailStr
    phone: Optional[str] = None
    name: Optional[str] = None
    name_kana: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    """顧客作成スキーマ"""
    pass


class CustomerUpdate(BaseModel):
    """顧客更新スキーマ"""
    phone: Optional[str] = None
    name: Optional[str] = None
    name_kana: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """顧客レスポンススキーマ"""
    id: str
    is_active: bool
    total_visits: int
    last_visit: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== スタイリストスキーマ ====================
class StylistBase(BaseModel):
    """スタイリストベーススキーマ"""
    name: str
    name_kana: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    working_hours: Optional[dict] = None


class StylistCreate(StylistBase):
    """スタイリスト作成スキーマ"""
    pass


class StylistUpdate(BaseModel):
    """スタイリスト更新スキーマ"""
    name: Optional[str] = None
    name_kana: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    working_hours: Optional[dict] = None


class StylistResponse(StylistBase):
    """スタイリストレスポンススキーマ"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== サービススキーマ ====================
class ServiceBase(BaseModel):
    """サービスベーススキーマ"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: int = Field(..., gt=0)
    price: int = Field(..., ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    display_order: int = 0


class ServiceCreate(ServiceBase):
    """サービス作成スキーマ"""
    pass


class ServiceUpdate(BaseModel):
    """サービス更新スキーマ"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    price: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class ServiceResponse(ServiceBase):
    """サービスレスポンススキーマ"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== 商品スキーマ ====================
class ProductBase(BaseModel):
    """商品ベーススキーマ"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    cost: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    display_order: int = 0


class ProductCreate(ProductBase):
    """商品作成スキーマ"""
    pass


class ProductUpdate(BaseModel):
    """商品更新スキーマ"""
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    cost: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class ProductResponse(ProductBase):
    """商品レスポンススキーマ"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== 予約スキーマ ====================
class ReservationBase(BaseModel):
    """予約ベーススキーマ"""
    customer_id: str
    stylist_id: Optional[str] = None
    service_id: str
    reservation_datetime: datetime
    duration_minutes: int = Field(..., gt=0)
    notes: Optional[str] = None


class ReservationCreate(ReservationBase):
    """予約作成スキーマ"""
    pass


class ReservationUpdate(BaseModel):
    """予約更新スキーマ"""
    stylist_id: Optional[str] = None
    service_id: Optional[str] = None
    reservation_datetime: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class ReservationResponse(ReservationBase):
    """予約レスポンススキーマ"""
    id: str
    status: ReservationStatus
    reminder_sent: bool
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReservationWithDetails(ReservationResponse):
    """予約詳細レスポンススキーマ（関連データ含む）"""
    customer: Optional[CustomerResponse] = None
    stylist: Optional[StylistResponse] = None
    service: Optional[ServiceResponse] = None


# ==================== 注文スキーマ ====================
class OrderItemCreate(BaseModel):
    """注文アイテム作成スキーマ"""
    product_id: Optional[str] = None
    service_id: Optional[str] = None
    name: str
    quantity: int = Field(..., gt=0)
    unit_price: int = Field(..., ge=0)


class OrderBase(BaseModel):
    """注文ベーススキーマ"""
    customer_id: str
    reservation_id: Optional[str] = None
    items: List[OrderItemCreate]
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """注文作成スキーマ"""
    coupon_code: Optional[str] = None


class OrderUpdate(BaseModel):
    """注文更新スキーマ"""
    status: Optional[OrderStatus] = None
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """注文レスポンススキーマ"""
    id: str
    customer_id: str
    reservation_id: Optional[str] = None
    total_amount: int
    discount_amount: int
    final_amount: int
    status: OrderStatus
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class OrderWithDetails(OrderResponse):
    """注文詳細レスポンススキーマ（関連データ含む）"""
    customer: Optional[CustomerResponse] = None
    reservation: Optional[ReservationResponse] = None


# ==================== クーポンスキーマ ====================
class CouponBase(BaseModel):
    """クーポンベーススキーマ"""
    code: str = Field(..., min_length=3, max_length=50)
    name: str
    description: Optional[str] = None
    coupon_type: CouponType
    discount_value: int = Field(..., gt=0)
    min_purchase_amount: Optional[int] = Field(None, ge=0)
    max_discount_amount: Optional[int] = Field(None, ge=0)
    valid_from: datetime
    valid_until: datetime
    usage_limit: Optional[int] = Field(None, gt=0)
    applicable_services: Optional[List[str]] = None

    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v


class CouponCreate(CouponBase):
    """クーポン作成スキーマ"""
    pass


class CouponUpdate(BaseModel):
    """クーポン更新スキーマ"""
    name: Optional[str] = None
    description: Optional[str] = None
    discount_value: Optional[int] = Field(None, gt=0)
    min_purchase_amount: Optional[int] = Field(None, ge=0)
    max_discount_amount: Optional[int] = Field(None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    applicable_services: Optional[List[str]] = None


class CouponResponse(CouponBase):
    """クーポンレスポンススキーマ"""
    id: str
    usage_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class CouponValidateRequest(BaseModel):
    """クーポン検証リクエストスキーマ"""
    code: str
    total_amount: int
    service_ids: Optional[List[str]] = None


class CouponValidateResponse(BaseModel):
    """クーポン検証レスポンススキーマ"""
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: int = 0
    message: Optional[str] = None


# ==================== キャンペーンスキーマ ====================
class CampaignBase(BaseModel):
    """キャンペーンベーススキーマ"""
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    target_audience: Optional[dict] = None
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    conditions: Optional[dict] = None

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class CampaignCreate(CampaignBase):
    """キャンペーン作成スキーマ"""
    pass


class CampaignUpdate(BaseModel):
    """キャンペーン更新スキーマ"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_audience: Optional[dict] = None
    discount_type: Optional[str] = None
    discount_value: Optional[int] = None
    conditions: Optional[dict] = None
    is_active: Optional[bool] = None


class CampaignResponse(CampaignBase):
    """キャンペーンレスポンススキーマ"""
    id: str
    status: CampaignStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# ==================== ストレージスキーマ ====================
class FileUploadResponse(BaseModel):
    """ファイルアップロードレスポンススキーマ"""
    name: str
    path: str
    url: str
    size: int
    content_type: str


class FileListResponse(BaseModel):
    """ファイル一覧レスポンススキーマ"""
    files: List[FileUploadResponse]
    total: int


# ==================== 共通スキーマ ====================
class MessageResponse(BaseModel):
    """メッセージレスポンススキーマ"""
    message: str


class PaginationParams(BaseModel):
    """ページネーションパラメータ"""
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """ページネーション付きレスポンス"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int







