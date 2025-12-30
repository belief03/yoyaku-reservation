"""
設定ファイル
環境変数とアプリケーション設定を管理
"""
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings

# .envファイルのエンコーディングエラーを回避するため、事前に環境変数を読み込む
def load_env_file_safe(file_path: Path) -> None:
    """安全に.envファイルを読み込む（エンコーディングエラーを回避）"""
    if not file_path.exists():
        return
    
    try:
        # UTF-8で読み込みを試行
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 既に環境変数が設定されている場合は上書きしない
                    if key not in os.environ:
                        os.environ[key] = value
    except UnicodeDecodeError:
        # UTF-8で読み込めない場合、複数のエンコーディングを試行
        encodings = ["utf-8-sig", "cp932", "shift_jis", "latin-1"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            # 既に環境変数が設定されている場合は上書きしない
                            if key not in os.environ:
                                os.environ[key] = value
                break
            except (UnicodeDecodeError, LookupError):
                continue
        else:
            # すべてのエンコーディングで失敗した場合、警告を出す
            import warnings
            warnings.warn(
                f"警告: .envファイル({file_path})のエンコーディングを判別できませんでした。"
                f"ファイルをUTF-8で保存し直してください。"
            )
    except Exception as e:
        import warnings
        warnings.warn(f"警告: .envファイルの読み込み中にエラーが発生しました: {e}")


# .envファイルを安全に読み込む
env_file = Path(".env")
load_env_file_safe(env_file)


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Supabase設定
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_DB_URL: Optional[str] = os.getenv("SUPABASE_DB_URL")
    
    # データベース設定
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    
    # API設定
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Yoyaku Reservation System"
    VERSION: str = "1.0.0"
    
    # CORS設定
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # システム管理者設定
    ADMIN_API_KEY: Optional[str] = os.getenv("ADMIN_API_KEY")
    
    # 予約設定
    RESERVATION_SLOT_DURATION_MINUTES: int = 30
    MAX_ADVANCE_BOOKING_DAYS: int = 90
    MIN_ADVANCE_BOOKING_HOURS: int = 2
    CANCELLATION_HOURS_BEFORE: int = 24
    
    # 営業時間設定
    BUSINESS_HOURS_START: str = "09:00"
    BUSINESS_HOURS_END: str = "20:00"
    BUSINESS_DAYS: list[int] = [0, 1, 2, 3, 4, 5, 6]  # 0=月曜日, 6=日曜日
    
    # ファイルストレージ設定
    STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET") or os.getenv("STORAGE_BUCKET", "uploads")
    MAX_FILE_SIZE_MB: int = 10
    
    # メール設定
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    # SSL/TLS設定（自動判定されるが、明示的に指定可能）
    SMTP_USE_SSL: Optional[bool] = os.getenv("SMTP_USE_SSL", "").lower() == "true"
    SMTP_USE_TLS: Optional[bool] = os.getenv("SMTP_USE_TLS", "").lower() == "true"
    
    # AI設定
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
    
    class Config:
        # .envファイルは既に読み込まれているため、再度読み込まない
        env_file = None
        case_sensitive = True
        extra = "ignore"  # 追加の環境変数を無視（エラーを防ぐ）


settings = Settings()


