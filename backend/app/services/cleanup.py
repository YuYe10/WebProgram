"""Cleanup service for unused images and expired archived notes.

This module handles two categories of periodic maintenance:

1. **Image cleanup** – Detects and deletes image files in the ``uploads/``
   directory that are no longer referenced by any note's Tiptap content.
   This runs both eagerly (immediately after a note update/delete) and
   periodically via the background cleanup loop.

2. **Expired archived note cleanup** – Automatically purges notes that have
   been in the archive for more than 7 days, removing their tag associations
   first to avoid foreign-key violations.
"""

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

# Absolute path to the uploads directory where user-uploaded images are stored
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"

# Regex pattern matching image URLs embedded in Tiptap JSON content.
# Matches paths like "/uploads/abc123def456.png" and captures the filename.
IMAGE_URL_PATTERN = re.compile(r"/uploads/([a-f0-9]+\.[a-z]+)")


def extract_image_filenames(content: dict | None) -> set[str]:
    """Extract all image filenames from a single note's Tiptap JSON content.

    Images in Tiptap JSON have ``type: "image"`` with ``attrs.src`` pointing
    to ``/uploads/<filename>``.  The function recursively walks the document
    tree and collects all such filenames.

    Args:
        content: A Tiptap JSON document (dict), or None.

    Returns:
        A set of bare filenames (e.g. ``{"abc123.png"}``) without the
        ``/uploads/`` prefix.
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
            # Recurse into all values to handle nested structures
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(content)
    return result


def extract_referenced_images(db_session) -> set[str]:
    """Extract all referenced image filenames from note contents.

    Iterates over a collection of note objects (typically a synchronous
    SQLAlchemy result set) and aggregates every image filename referenced
    across all notes.

    Args:
        db_session: An iterable of note objects, each with a ``content``
            attribute containing Tiptap JSON.

    Returns:
        A set of all image filenames referenced by the provided notes.
    """
    referenced: set[str] = set()
    for note in db_session:
        if note.content:
            referenced.update(extract_image_filenames(note.content))
    return referenced


async def cleanup_unused_images(db: AsyncSession) -> int:
    """Delete image files in uploads/ that aren't referenced by any note.

    Scans all notes to build the set of referenced filenames, then compares
    it against the files on disk.  Any file not referenced by any note is
    deleted.

    Args:
        db: Async database session used to query note content.

    Returns:
        The number of image files deleted.
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
        # Delete files that exist on disk but are not referenced by any note
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
    images that are no longer needed.  Unlike ``cleanup_unused_images``, this
    only checks the provided candidate filenames against the database, making
    it more efficient for targeted cleanup.

    Args:
        db: Database session used to query note content.
        candidate_filenames: Set of bare filenames (e.g. ``"abc123.png"``)
            to check for orphan status.

    Returns:
        The number of image files deleted.
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
        # Only delete if the file is not referenced by any remaining note
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

    Finds all notes where ``is_archived`` is True and ``archived_at`` is
    older than the 7-day cutoff, then deletes their tag associations and
    the notes themselves.  The tag associations are deleted explicitly
    before the notes to avoid foreign-key violations (even though cascading
    deletes should handle this, being explicit is safer).

    Args:
        db: Async database session.

    Returns:
        The number of notes deleted.
    """
    # Calculate the cutoff timestamp: 7 days ago from now
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
    """Run all cleanup tasks and return a summary.

    Executes both image cleanup and expired archived note cleanup in
    sequence.

    Args:
        db: Async database session.

    Returns:
        A dict with keys ``unused_images_deleted`` and
        ``expired_archived_deleted`` containing the respective counts.
    """
    images_deleted = await cleanup_unused_images(db)
    notes_deleted = await cleanup_expired_archived(db)
    return {
        "unused_images_deleted": images_deleted,
        "expired_archived_deleted": notes_deleted,
    }


async def cleanup_loop(session_factory, interval_seconds: int = 3600):
    """Background loop that runs cleanup periodically.

    Sleeps for the configured interval, then creates a new database session
    and runs all cleanup tasks.  The loop continues until cancelled (e.g.
    on application shutdown).  Errors are caught and logged so the loop
    never terminates unexpectedly.

    Args:
        session_factory: An ``async_sessionmaker`` callable that produces a
            new ``AsyncSession`` when called.
        interval_seconds: Seconds between cleanup runs.  Defaults to 1 hour
            (3600 seconds).
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            logger.info("Running scheduled cleanup...")
            async with session_factory() as db:
                await run_all_cleanup(db)
        except asyncio.CancelledError:
            # Graceful shutdown: exit the loop without error
            logger.info("Cleanup loop cancelled")
            break
        except Exception as e:
            # Log but do not re-raise so the loop keeps running
            logger.error(f"Error in cleanup loop: {e}", exc_info=True)
