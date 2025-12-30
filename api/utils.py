"""
ユーティリティ関数
共通で使用するヘルパー関数
"""
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from config import settings


def parse_time_string(time_str: str) -> Tuple[int, int]:
    """
    時間文字列（HH:MM）を時と分にパース
    
    Args:
        time_str: 時間文字列（例: "09:00"）
    
    Returns:
        (hour, minute)のタプル
    """
    try:
        parts = time_str.split(':')
        return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    except (ValueError, IndexError):
        raise ValueError(f"無効な時間形式です: {time_str}")


def is_business_hours(dt: datetime) -> bool:
    """
    指定された日時が営業時間内かどうかをチェック
    
    Args:
        dt: チェックする日時
    
    Returns:
        営業時間内の場合True
    """
    start_hour, start_minute = parse_time_string(settings.BUSINESS_HOURS_START)
    end_hour, end_minute = parse_time_string(settings.BUSINESS_HOURS_END)
    
    current_hour = dt.hour
    current_minute = dt.minute
    
    # 開始時間のチェック
    if current_hour < start_hour:
        return False
    if current_hour == start_hour and current_minute < start_minute:
        return False
    
    # 終了時間のチェック
    if current_hour > end_hour:
        return False
    if current_hour == end_hour and current_minute >= end_minute:
        return False
    
    return True


def is_business_day(dt: datetime) -> bool:
    """
    指定された日時が営業日かどうかをチェック
    
    Args:
        dt: チェックする日時
    
    Returns:
        営業日の場合True
    """
    weekday = dt.weekday()  # 0=月曜日, 6=日曜日
    return weekday in settings.BUSINESS_DAYS


def generate_time_slots(
    date: datetime,
    duration_minutes: int = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> List[datetime]:
    """
    指定日の時間枠を生成
    
    Args:
        date: 対象日
        duration_minutes: 各時間枠の長さ（分）
        start_time: 開始時間（HH:MM形式、デフォルトは設定値）
        end_time: 終了時間（HH:MM形式、デフォルトは設定値）
    
    Returns:
        時間枠のリスト
    """
    if duration_minutes is None:
        duration_minutes = settings.RESERVATION_SLOT_DURATION_MINUTES
    
    if start_time is None:
        start_time = settings.BUSINESS_HOURS_START
    if end_time is None:
        end_time = settings.BUSINESS_HOURS_END
    
    start_hour, start_minute = parse_time_string(start_time)
    end_hour, end_minute = parse_time_string(end_time)
    
    slots = []
    current_time = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_datetime = date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    
    while current_time + timedelta(minutes=duration_minutes) <= end_datetime:
        slots.append(current_time)
        current_time += timedelta(minutes=duration_minutes)
    
    return slots


def format_datetime_jp(dt: datetime) -> str:
    """
    日時を日本語形式でフォーマット
    
    Args:
        dt: 日時
    
    Returns:
        フォーマットされた文字列（例: "2024年1月1日(月) 10:00"）
    """
    weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekday_names[dt.weekday()]
    
    return dt.strftime(f"%Y年%m月%d日({weekday}) %H:%M")


def calculate_discount(
    total_amount: int,
    discount_type: str,
    discount_value: int,
    max_discount: Optional[int] = None
) -> int:
    """
    割引金額を計算
    
    Args:
        total_amount: 合計金額
        discount_type: 割引タイプ（"percentage"または"fixed_amount"）
        discount_value: 割引値（パーセンテージまたは固定金額）
        max_discount: 最大割引金額（オプション）
    
    Returns:
        割引金額
    """
    if discount_type == "percentage":
        discount = int(total_amount * discount_value / 100)
        if max_discount:
            discount = min(discount, max_discount)
    elif discount_type == "fixed_amount":
        discount = discount_value
    else:
        discount = 0
    
    return min(discount, total_amount)  # 合計金額を超えないようにする


def validate_email(email: str) -> bool:
    """
    メールアドレスの簡易バリデーション
    
    Args:
        email: メールアドレス
    
    Returns:
        有効な場合True
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    電話番号の簡易バリデーション
    
    Args:
        phone: 電話番号
    
    Returns:
        有効な場合True
    """
    import re
    # 数字とハイフン、括弧のみを許可
    pattern = r'^[\d\-\(\)\s]+$'
    return bool(re.match(pattern, phone)) and len(phone.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')) >= 10


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    文字列を指定長で切り詰め
    
    Args:
        text: 対象文字列
        max_length: 最大長
        suffix: 切り詰め時の接尾辞
    
    Returns:
        切り詰められた文字列
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_currency(amount: int) -> str:
    """
    金額を日本語形式でフォーマット
    
    Args:
        amount: 金額
    
    Returns:
        フォーマットされた文字列（例: "¥1,000"）
    """
    return f"¥{amount:,}"


def get_next_business_day(dt: datetime, days: int = 1) -> datetime:
    """
    次の営業日を取得
    
    Args:
        dt: 基準日時
        days: 何営業日後か
    
    Returns:
        次の営業日
    """
    current = dt
    count = 0
    
    while count < days:
        current += timedelta(days=1)
        if is_business_day(current):
            count += 1
    
    return current


def calculate_age(birthday: datetime) -> Optional[int]:
    """
    生年月日から年齢を計算
    
    Args:
        birthday: 生年月日
    
    Returns:
        年齢（計算できない場合はNone）
    """
    if not birthday:
        return None
    
    today = datetime.now()
    age = today.year - birthday.year
    
    # まだ誕生日を迎えていない場合
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    
    return age


def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズ
    
    Args:
        filename: 元のファイル名
    
    Returns:
        サニタイズされたファイル名
    """
    import re
    # 危険な文字を削除
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 連続するスペースやドットを削除
    filename = re.sub(r'\.{2,}', '.', filename)
    filename = filename.strip('. ')
    
    return filename or "file"


def generate_unique_code(prefix: str = "", length: int = 8) -> str:
    """
    ユニークなコードを生成
    
    Args:
        prefix: プレフィックス
        length: コードの長さ
    
    Returns:
        生成されたコード
    """
    import random
    import string
    
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    
    return f"{prefix}{code}" if prefix else code






