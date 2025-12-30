"""
キャンペーンステータス更新スクリプト
キャンペーンの開始・終了を自動的に更新
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing.campaign_manager import get_campaign_manager
from api.logger import logger


def update_campaign_statuses():
    """キャンペーンのステータスを更新"""
    logger.info("キャンペーンステータスの更新を開始します")
    
    try:
        campaign_manager = get_campaign_manager()
        campaign_manager.update_campaign_status()
        logger.info("キャンペーンステータスの更新が完了しました")
    except Exception as e:
        logger.error(f"キャンペーンステータスの更新中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    update_campaign_statuses()






