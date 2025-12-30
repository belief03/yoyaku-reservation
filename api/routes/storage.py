"""
ファイルストレージ管理APIルート
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from datetime import datetime
from supabase import Client
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from api.database import get_db
from api.schemas import (
    FileUploadResponse,
    FileListResponse,
    MessageResponse
)
from config import settings

router = APIRouter()


def validate_file(file: UploadFile) -> None:
    """ファイルのバリデーション"""
    # ファイルサイズのチェック（簡易版）
    # 実際の実装では、ファイルを読み込んでサイズを確認する必要があります
    
    # 許可されたファイルタイプのチェック
    allowed_types = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "text/plain"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"許可されていないファイルタイプです: {file.content_type}"
        )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = None,
    db: Client = Depends(get_db)
):
    """ファイルをアップロード"""
    # ファイルのバリデーション
    validate_file(file)
    
    # ファイルパスの生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{timestamp}_{file.filename}"
    
    if folder:
        file_path = f"{folder}/{file_name}"
    else:
        file_path = file_name
    
    # ファイルの読み込み
    file_content = await file.read()
    
    # Supabaseストレージへのアップロード
    try:
        bucket = settings.STORAGE_BUCKET
        result = db.storage.from_(bucket).upload(
            file_path,
            file_content,
            file_options={"content-type": file.content_type}
        )
        
        # 公開URLの取得
        url_result = db.storage.from_(bucket).get_public_url(file_path)
        
        return FileUploadResponse(
            name=file.filename,
            path=file_path,
            url=url_result,
            size=len(file_content),
            content_type=file.content_type or "application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルのアップロードに失敗しました: {str(e)}")


@router.get("/list", response_model=FileListResponse)
async def list_files(
    folder: Optional[str] = None,
    limit: int = 100,
    db: Client = Depends(get_db)
):
    """ファイル一覧を取得"""
    try:
        bucket = settings.STORAGE_BUCKET
        
        if folder:
            result = db.storage.from_(bucket).list(folder, {"limit": limit})
        else:
            result = db.storage.from_(bucket).list("", {"limit": limit})
        
        files = []
        for item in result:
            file_path = f"{folder}/{item['name']}" if folder else item['name']
            url_result = db.storage.from_(bucket).get_public_url(file_path)
            
            files.append(FileUploadResponse(
                name=item['name'],
                path=file_path,
                url=url_result,
                size=item.get('metadata', {}).get('size', 0),
                content_type=item.get('metadata', {}).get('mimetype', 'application/octet-stream')
            ))
        
        return FileListResponse(files=files, total=len(files))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイル一覧の取得に失敗しました: {str(e)}")


@router.delete("/{file_path:path}", response_model=MessageResponse)
async def delete_file(
    file_path: str,
    db: Client = Depends(get_db)
):
    """ファイルを削除"""
    try:
        bucket = settings.STORAGE_BUCKET
        db.storage.from_(bucket).remove([file_path])
        
        return MessageResponse(message=f"ファイル {file_path} を削除しました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ファイルの削除に失敗しました: {str(e)}")


@router.get("/{file_path:path}/url")
async def get_file_url(
    file_path: str,
    db: Client = Depends(get_db)
):
    """ファイルの公開URLを取得"""
    try:
        bucket = settings.STORAGE_BUCKET
        url = db.storage.from_(bucket).get_public_url(file_path)
        
        return {"url": url, "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URLの取得に失敗しました: {str(e)}")







