"""Cleanup service for unused images and expired archived notes."""

import asyncio
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.tag import NoteTag

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"

# Image URL pattern: /uploads/<filename>
IMAGE_URL_PATTERN = re.compile(r"/uploads/([a-f0-9]+\.[a-z]+)")


def extract_image_filenames(content: dict | None) -> set[str]:
    """Extract all image filenames from a single note's Tiptap JSON content.

    Images in Tiptap JSON have type: "image" with attrs.src pointing to /uploads/<filename>.
    Returns a set of bare filenames (e.g. "abc123.png") without the /uploads/ prefix.
    """
    result: set[str] = set()
    if not content:
        return result

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "image" and "attrs" in node:
                src = node["attrs"].get("src", "")
                match = IMAGE_URL_PATTERN.search(src)
                if match:
                    result.add(match.group(1))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(content)
    return result


def extract_referenced_images(db_session) -> set[str]:
    """Extract all referenced image filenames from note contents."""
    referenced: set[str] = set()
    for note in db_session:
        if note.content:
            referenced.update(extract_image_filenames(note.content))
    return referenced


async def cleanup_unused_images(db: AsyncSession) -> int:
    """Delete image files in uploads/ that aren't referenced by any note.

    Returns the number of files deleted.
    """
    # Get all notes with content
    result = await db.execute(select(Note.content))
    notes = result.all()

    # Extract all referenced image filenames from note content
    referenced: set[str] = set()
    for (content,) in notes:
        referenced.update(extract_image_filenames(content))

    # List all files in uploads directory
    if not UPLOAD_DIR.exists():
        return 0

    deleted = 0
    for filepath in UPLOAD_DIR.iterdir():
        if filepath.is_file() and filepath.name not in referenced:
            try:
                filepath.unlink()
                logger.info(f"Deleted unused image: {filepath.name}")
                deleted += 1
            except OSError as e:
                logger.error(f"Failed to delete {filepath.name}: {e}")

    if deleted:
        logger.info(f"Cleaned up {deleted} unused image(s)")
    return deleted


async def delete_orphaned_images(db: AsyncSession, candidate_filenames: set[str]) -> int:
    """Delete specific image files from uploads/ if no note references them.

    Use this after a note is deleted or updated to immediately clean up
    images that are no longer needed.

    Args:
        db: Database session.
        candidate_filenames: Set of bare filenames (e.g. "abc123.png") to check.

    Returns the number of files deleted.
    """
    if not candidate_filenames or not UPLOAD_DIR.exists():
        return 0

    # Fetch all notes' content and build the set of still-referenced filenames
    result = await db.execute(select(Note.content))
    referenced: set[str] = set()
    for (content,) in result.all():
        referenced.update(extract_image_filenames(content))

    deleted = 0
    for filename in candidate_filenames:
        if filename not in referenced:
            filepath = UPLOAD_DIR / filename
            if filepath.is_file():
                try:
                    filepath.unlink()
                    logger.info(f"Deleted orphaned image: {filename}")
                    deleted += 1
                except OSError as e:
                    logger.error(f"Failed to delete orphaned image {filename}: {e}")

    if deleted:
        logger.info(f"Cleaned up {deleted} orphaned image(s)")
    return deleted


async def cleanup_expired_archived(db: AsyncSession) -> int:
    """Delete archived notes that have been archived for more than 7 days.

    Returns the number of notes deleted.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    # Find expired archived notes
    result = await db.execute(
        select(Note.id).where(
            Note.is_archived == True,
            Note.archived_at.isnot(None),
            Note.archived_at < cutoff,
        )
    )
    expired_ids = [row[0] for row in result.all()]

    if not expired_ids:
        return 0

    # Delete note_tags associations first (should cascade, but be explicit)
    await db.execute(
        delete(NoteTag).where(NoteTag.note_id.in_(expired_ids))
    )

    # Delete the notes
    await db.execute(
        delete(Note).where(Note.id.in_(expired_ids))
    )
    await db.commit()

    logger.info(f"Auto-deleted {len(expired_ids)} expired archived note(s)")
    return len(expired_ids)


async def run_all_cleanup(db: AsyncSession) -> dict:
    """Run all cleanup tasks. Returns a summary dict."""
    images_deleted = await cleanup_unused_images(db)
    notes_deleted = await cleanup_expired_archived(db)
    return {
        "unused_images_deleted": images_deleted,
        "expired_archived_deleted": notes_deleted,
    }


async def cleanup_loop(session_factory, interval_seconds: int = 3600):
    """Background loop that runs cleanup periodically.

    Args:
        session_factory: An async_sessionmaker callable.
        interval_seconds: Seconds between cleanup runs (default: 1 hour).
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            logger.info("Running scheduled cleanup...")
            async with session_factory() as db:
                await run_all_cleanup(db)
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}", exc_info=True)
