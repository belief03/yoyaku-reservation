"""
メール送信テストスクリプト
SMTP設定をテストして、メール送信が正常に動作するか確認します
"""
import sys
import os
import io
from pathlib import Path

# Windowsコンソールの文字エンコーディング問題を回避
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# パスを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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
            print(f"[警告] .envファイル({file_path})のエンコーディングを判別できませんでした。")
            print(f"ファイルをUTF-8で保存し直してください。")
    except Exception as e:
        print(f"[警告] .envファイルの読み込み中にエラーが発生しました: {e}")

# .envファイルを安全に読み込む
env_file = project_root / ".env"
load_env_file_safe(env_file)

try:
    from api.email_service import get_email_service
    from config import settings
except Exception as e:
    print(f"[エラー] モジュールのインポートに失敗しました: {e}")
    print(f"プロジェクトルート: {project_root}")
    sys.exit(1)

def test_email_config():
    """メール設定を確認"""
    print("=" * 60)
    print("メール送信設定確認")
    print("=" * 60)
    
    email_service = get_email_service()
    
    print(f"\n[設定確認]")
    print(f"  SMTP_HOST: {settings.SMTP_HOST or '未設定'}")
    print(f"  SMTP_PORT: {settings.SMTP_PORT}")
    print(f"  SMTP_USER: {settings.SMTP_USER or '未設定'}")
    print(f"  SMTP_PASSWORD: {'設定済み' if settings.SMTP_PASSWORD else '未設定'}")
    print(f"  EMAIL_FROM: {settings.EMAIL_FROM or '未設定'}")
    print(f"  SMTP_USE_SSL: {settings.SMTP_USE_SSL}")
    print(f"  SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
    
    print(f"\n[サービス状態]")
    print(f"  有効: {email_service.enabled}")
    
    if email_service.enabled:
        connection_type = "SSL" if email_service.use_ssl else ("STARTTLS" if email_service.use_tls else "なし")
        print(f"  接続タイプ: {connection_type}")
        print(f"  送信元アドレス: {email_service.email_from}")
    else:
        missing = []
        if not settings.SMTP_HOST:
            missing.append("SMTP_HOST")
        if not settings.SMTP_USER:
            missing.append("SMTP_USER")
        if not settings.SMTP_PASSWORD:
            missing.append("SMTP_PASSWORD")
        print(f"  不足している設定: {', '.join(missing) if missing else 'なし'}")
        print(f"\n[エラー] メール送信サービスが無効です。")
        print(f"  以下の環境変数を設定してください:")
        for item in missing:
            print(f"    - {item}")
        return False
    
    return True

def test_send_email(to_email: str):
    """テストメールを送信"""
    print("\n" + "=" * 60)
    print("テストメール送信")
    print("=" * 60)
    
    email_service = get_email_service()
    
    if not email_service.enabled:
        print("[ERROR] メール送信サービスが無効です。設定を確認してください。")
        return False
    
    print(f"\n[送信先] {to_email}")
    print(f"[送信元] {email_service.email_from}")
    
    # テストメールを送信
    test_url = "https://example.com/invite/test-token-12345"
    success = email_service.send_invitation_email(
        to_email=to_email,
        invitation_url=test_url,
        shop_name="テスト店舗"
    )
    
    if success:
        print("\n[OK] テストメールの送信に成功しました！")
        print(f"  送信先: {to_email}")
        print(f"  メールボックスを確認してください。")
        return True
    else:
        print("\n[ERROR] テストメールの送信に失敗しました。")
        print("  ログを確認して、SMTP設定を確認してください。")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/test_email.py <email>")
        print("\n例:")
        print("  python scripts/test_email.py test@example.com")
        print("\n注意: メール送信にはSMTP設定が必要です。")
        print("  .envファイルに以下の設定を追加してください:")
        print("    SMTP_HOST=smtp.gmail.com")
        print("    SMTP_PORT=587")
        print("    SMTP_USER=your-email@gmail.com")
        print("    SMTP_PASSWORD=your-app-password")
        print("    EMAIL_FROM=your-email@gmail.com")
        sys.exit(1)
    
    to_email = sys.argv[1]
    
    # 設定確認
    if not test_email_config():
        sys.exit(1)
    
    # テストメール送信
    if test_send_email(to_email):
        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("テスト失敗")
        print("=" * 60)
        sys.exit(1)

