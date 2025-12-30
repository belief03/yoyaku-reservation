"""
データベース接続とセッション管理
"""
from supabase import Client
from typing import Generator
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.supabase_client import supabase


def get_db() -> Generator[Client, None, None]:
    """
    データベースクライアントを取得する依存関数
    FastAPIの依存性注入で使用
    """
    try:
        yield supabase
    finally:
        pass  # Supabaseクライアントはステートレスなのでクリーンアップ不要


def get_service_db() -> Generator[Client, None, None]:
    """
    サービスロール用のデータベースクライアントを取得
    管理者権限が必要な操作で使用
    """
    from api.supabase_client import SupabaseClient
    try:
        yield SupabaseClient.get_service_client()
    finally:
        pass







