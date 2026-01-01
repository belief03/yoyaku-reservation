"""
ロギング設定
アプリケーション全体のログ管理
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import os

# Vercel環境かどうかをチェック（複数の方法で確認）
# 根本的な原因: Vercel環境では読み取り専用ファイルシステムのため、ディレクトリ作成は常に失敗します
# 解決策: 常にtry-exceptで囲み、Vercel環境の検出が失敗してもエラーにならないようにする
try:
    current_file_path = str(Path(__file__).absolute())
    IS_VERCEL = (
        os.getenv("VERCEL") == "1" or 
        os.getenv("VERCEL_ENV") is not None or
        os.getenv("VERCEL_ENV") == "production" or
        os.getenv("VERCEL_ENV") == "preview" or
        "/var/task" in current_file_path  # Vercelの実行パスをチェック
    )
except Exception:
    # パスの取得に失敗した場合は、安全のためVercel環境とみなす
    IS_VERCEL = True

# ログディレクトリの作成（常にtry-exceptで囲んで安全に）
log_dir = None
log_file = None

# ディレクトリ作成を試みる（失敗してもエラーにしない）
# Vercel環境では常にスキップ、ローカル環境でも失敗した場合はスキップ
# 注意: Vercel環境では読み取り専用ファイルシステムのため、ディレクトリ作成は常に失敗します
# 根本的な解決策: 常にtry-exceptで囲み、Vercel環境の検出が失敗してもエラーにならないようにする
try:
    if not IS_VERCEL:
        # ローカル環境のみログディレクトリを作成を試みる
        log_dir = Path("logs")
        # ディレクトリが存在しない場合のみ作成を試みる
        # 注意: exists()チェックも読み取り専用ファイルシステムでは失敗する可能性があるため、
        # mkdir()を直接呼び出して、エラーをキャッチする
        try:
            log_dir.mkdir(exist_ok=True)
        except (OSError, PermissionError):
            # ディレクトリ作成に失敗した場合はファイルログを無効化
            log_dir = None
            log_file = None
        else:
            # ログファイル名（日付付き）
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
except (OSError, PermissionError, Exception) as e:
    # ディレクトリ作成に失敗した場合はファイルログを無効化
    # 読み取り専用ファイルシステムなどの理由で失敗してもエラーにしない
    log_dir = None
    log_file = None
# Vercel環境では何もしない（log_dirとlog_fileはNoneのまま）


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










