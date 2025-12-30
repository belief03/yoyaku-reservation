"""
ロギング設定
アプリケーション全体のログ管理
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import os

# ログディレクトリの作成
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# ログファイル名（日付付き）
log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"


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
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# デフォルトロガー
logger = setup_logger()






