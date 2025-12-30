"""
FastAPIアプリケーションのメインファイル
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from api.logger import logger
from api.exceptions import YoyakuException
from api.routes import (
    reservations,
    customers,
    stylists,
    services,
    products,
    orders,
    coupons,
    campaigns,
    storage
)
from api.routes import recommendations
from api.routes import settings as settings_router
from api.routes import invitations
from api.routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # 起動時の処理
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")
    yield
    # 終了時の処理
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


# FastAPIアプリケーションの作成
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="予約管理システムのAPI",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# エラーハンドラー
@app.exception_handler(YoyakuException)
async def yoyaku_exception_handler(request, exc: YoyakuException):
    """カスタム例外ハンドラー"""
    logger.error(f"YoyakuException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """グローバル例外ハンドラー"""
    import traceback
    error_detail = str(exc)
    error_traceback = traceback.format_exc()
    logger.error(f"Unhandled exception: {error_detail}\n{error_traceback}")
    
    # 開発環境では詳細なエラー情報を返す
    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "detail": error_detail,
                "traceback": error_traceback.split("\n") if error_traceback else None
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )


# 静的ファイルの配信（ルーター登録の前に設定）
static_dir = Path(__file__).parent.parent / "static"
logger.info(f"Static directory: {static_dir}, exists: {static_dir.exists()}")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info("Static files mounted at /static")

# ヘルスチェックエンドポイント

@app.get("/")
async def root():
    """ルートエンドポイント - UIページを返す"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "running",
        "ui": "http://localhost:8000/static/index.html",
        "admin": "http://localhost:8000/static/admin.html"
    }

@app.get("/admin")
async def admin():
    """管理画面エンドポイント"""
    admin_file = static_dir / "admin.html"
    if admin_file.exists():
        return FileResponse(str(admin_file))
    raise HTTPException(status_code=404, detail="Admin page not found")


@app.get("/invite/{token}")
async def invite_page(token: str):
    """招待リンクページエンドポイント"""
    invite_file = static_dir / "invite.html"
    if invite_file.exists():
        return FileResponse(str(invite_file))
    raise HTTPException(status_code=404, detail="Invite page not found")


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


# ルーターの登録
app.include_router(
    reservations.router,
    prefix=f"{settings.API_V1_PREFIX}/reservations",
    tags=["reservations"]
)

app.include_router(
    customers.router,
    prefix=f"{settings.API_V1_PREFIX}/customers",
    tags=["customers"]
)

app.include_router(
    stylists.router,
    prefix=f"{settings.API_V1_PREFIX}/stylists",
    tags=["stylists"]
)

app.include_router(
    services.router,
    prefix=f"{settings.API_V1_PREFIX}/services",
    tags=["services"]
)

app.include_router(
    products.router,
    prefix=f"{settings.API_V1_PREFIX}/products",
    tags=["products"]
)

app.include_router(
    orders.router,
    prefix=f"{settings.API_V1_PREFIX}/orders",
    tags=["orders"]
)

app.include_router(
    coupons.router,
    prefix=f"{settings.API_V1_PREFIX}/coupons",
    tags=["coupons"]
)

app.include_router(
    campaigns.router,
    prefix=f"{settings.API_V1_PREFIX}/campaigns",
    tags=["campaigns"]
)

app.include_router(
    storage.router,
    prefix=f"{settings.API_V1_PREFIX}/storage",
    tags=["storage"]
)

app.include_router(
    recommendations.router,
    prefix=f"{settings.API_V1_PREFIX}/recommendations",
    tags=["recommendations"]
)

app.include_router(
    settings_router.router,
    prefix=f"{settings.API_V1_PREFIX}/settings",
    tags=["settings"]
)

app.include_router(
    invitations.router,
    prefix=f"{settings.API_V1_PREFIX}/invitations",
    tags=["invitations"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


