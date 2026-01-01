"""
ロギング設定
アプリケーション全体のログ管理
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import os

# Vercel環境かどうかをチェック
IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

# ログディレクトリの作成（Vercel環境ではスキップ）
log_dir = None
log_file = None

if not IS_VERCEL:
    # ローカル環境のみログディレクトリを作成
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        # ログファイル名（日付付き）
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    except (OSError, PermissionError):
        # ディレクトリ作成に失敗した場合はファイルログを無効化
        log_dir = None
        log_file = None


def setup_logger(name: str = "yoyaku", level: int = logging.INFO) -> logging.Logger:
    """
    ロガーをセットアップ
    
    Args:
        name: ロガー名
        level: ログレベル
    
    Returns:
        設定されたロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラーをクリア
    logger.handlers.clear()
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソールハンドラー（常に追加）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー（ローカル環境のみ、かつディレクトリ作成が成功した場合のみ）
    if log_file is not None and log_dir is not None:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # ファイルハンドラーの作成に失敗した場合はスキップ
            pass
    
    return logger


# デフォルトロガー
logger = setup_logger()










