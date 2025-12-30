"""
AIレコメンデーションAPIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from ai.recommendation_engine import RecommendationEngine

router = APIRouter()


def get_recommendation_engine(db: Client):
    """レコメンデーションエンジンのインスタンスを取得"""
    return RecommendationEngine(db)


@router.get("/services/{customer_id}")
async def get_recommended_services(
    customer_id: str,
    limit: int = Query(5, ge=1, le=20),
    db: Client = Depends(get_db)
):
    """顧客におすすめのサービスを取得"""
    try:
        engine = get_recommendation_engine(db)
        recommendations = engine.recommend_services(customer_id, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レコメンデーション取得エラー: {str(e)}")


@router.get("/products/{customer_id}")
async def get_recommended_products(
    customer_id: str,
    service_id: Optional[str] = None,
    limit: int = Query(5, ge=1, le=20),
    db: Client = Depends(get_db)
):
    """顧客におすすめの商品を取得"""
    try:
        engine = get_recommendation_engine(db)
        recommendations = engine.recommend_products(customer_id, service_id, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レコメンデーション取得エラー: {str(e)}")


@router.get("/times/{customer_id}")
async def get_recommended_times(
    customer_id: str,
    service_id: str = Query(..., description="サービスID"),
    db: Client = Depends(get_db)
):
    """顧客におすすめの予約時間を取得"""
    try:
        engine = get_recommendation_engine(db)
        recommendations = engine.predict_optimal_time(customer_id, service_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レコメンデーション取得エラー: {str(e)}")


@router.get("/preferences/{customer_id}")
async def get_customer_preferences(
    customer_id: str,
    db: Client = Depends(get_db)
):
    """顧客の好みを分析"""
    try:
        engine = get_recommendation_engine(db)
        preferences = engine.analyze_customer_preferences(customer_id)
        return preferences
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析エラー: {str(e)}")

