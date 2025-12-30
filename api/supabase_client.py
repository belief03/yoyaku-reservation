"""
Supabaseクライアント設定
"""
from supabase import create_client, Client
from typing import Optional
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class SupabaseClient:
    """Supabaseクライアントのシングルトン"""
    
    _instance: Optional[Client] = None
    _service_instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """通常のSupabaseクライアントを取得"""
        if cls._instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
    
    @classmethod
    def get_service_client(cls) -> Client:
        """サービスロール用のSupabaseクライアントを取得（管理者権限）"""
        if cls._service_instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
            cls._service_instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        return cls._service_instance
    
    @classmethod
    def reset(cls):
        """クライアントをリセット（テスト用）"""
        cls._instance = None
        cls._service_instance = None


# グローバルなクライアントインスタンス
supabase: Client = SupabaseClient.get_client()







