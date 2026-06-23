"""File upload endpoints.
文件上传端点

Handles image uploads for use within note content. Validates file
type and size, stores files on disk, and returns a URL reference.
处理用于笔记内容中的图片上传。验证文件类型和大小，将文件存储在磁盘上，并返回URL引用。
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.api.deps import get_current_user

router = APIRouter()

# Directory where uploaded files are stored (project_root/uploads)
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
# Allowed MIME types for image uploads
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
# Maximum upload size in bytes (5 MB)
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


class ImageUploadResponse(BaseModel):
    """Response schema for a successful image upload.
    图片上传成功的响应模式

    Attributes:
        url: Relative URL path to the uploaded image.
        filename: Original filename as provided by the client.
        size: File size in bytes.
    属性：
        url: 上传图片的相对URL路径
        filename: 客户端提供的原始文件名
        size: 文件大小（字节）
    """

    url: str
    filename: str
    size: int


@router.post("/images", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile,
    _=Depends(get_current_user),
):
    """Upload an image file. Returns the URL to reference in note content.
    上传图片文件。返回用于在笔记内容中引用的URL

    The endpoint validates the MIME type against a whitelist, enforces a
    maximum file size, and saves the file with a UUID-based filename to
    prevent collisions and path traversal attacks.
    该端点根据白名单验证MIME类型，强制执行最大文件大小限制，并使用基于UUID的文件名保存文件，
    以防止冲突和路径遍历攻击。

    Args:
        file: Uploaded file object provided by FastAPI multipart handling.
              FastAPI多部分处理提供的上传文件对象
        _: Authenticated user dependency (ensures only logged-in users can upload).
           已认证用户依赖（确保只有登录用户可以上传）

    Returns:
        ImageUploadResponse: URL, original filename, and size of the uploaded image.
                             上传图片的URL、原始文件名和大小

    Raises:
        HTTPException (400): If the file type is not supported or the file exceeds 5 MB.
                             如果文件类型不受支持或文件超过5MB
    """

    # Validate content type against the whitelist
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    # Read file contents into memory for size validation and writing
    contents = await file.read()

    # Validate file size against the maximum allowed
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_SIZE // (1024 * 1024)} MB",
        )

    # Generate a unique filename while preserving the original extension
    ext = Path(file.filename or "image.png").suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"):
        ext = ".png"
    filename = f"{uuid.uuid4().hex}{ext}"

    # Ensure the upload directory exists before writing
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Write the file to disk
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    # Return a relative URL that maps to the static file mount in main.py
    url = f"/uploads/{filename}"
    return ImageUploadResponse(url=url, filename=file.filename or filename, size=len(contents))
