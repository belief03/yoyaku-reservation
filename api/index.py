"""
Vercel用のエントリーポイント
"""
import sys
import os
import traceback

# 環境変数の確認（デバッグ用）
def check_env_vars():
    """環境変数の存在を確認"""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_KEY", "SECRET_KEY"]
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            # 値の最初の10文字だけをログに出力（セキュリティのため）
            print(f"[ENV] {var} is set (length: {len(value)})", file=sys.stderr)
    
    if missing:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}", file=sys.stderr)
    else:
        print("[INFO] All required environment variables are set", file=sys.stderr)
    
    return missing

# 環境変数を確認
missing_vars = check_env_vars()

# エラーハンドリングを追加
try:
    print("[INFO] Starting to import api.main...", file=sys.stderr)
    from api.main import app
    
    print("[INFO] Successfully imported api.main", file=sys.stderr)
    # Vercelがapp変数を検出できるようにする
    __all__ = ["app"]
except Exception as e:
    # エラーをログに出力（Vercelのログで確認可能）
    error_msg = f"[ERROR] Failed to import app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    
    # 最小限のFastAPIアプリを作成してエラーメッセージを返す
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def error_root():
        return JSONResponse(
            status_code=500,
            content={
                "error": "Application initialization failed",
                "message": str(e),
                "missing_env_vars": missing_vars,
                "check_logs": "Please check Vercel logs for details"
            }
        )
    
    @app.get("/health")
    async def error_health():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "missing_env_vars": missing_vars
            }
        )
    
    # すべてのルートでエラーを返す
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def error_handler(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Application initialization failed",
                "message": str(e),
                "missing_env_vars": missing_vars,
                "check_logs": "Please check Vercel logs for details"
            }
        )

