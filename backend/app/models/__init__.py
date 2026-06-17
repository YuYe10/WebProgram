"""Database models package.

Re-exports all SQLAlchemy ORM model classes so they can be imported
from ``app.models`` directly.  Importing this package also ensures
every model is registered with the declarative metadata, which is
required for Alembic auto-generation and ``Base.metadata.create_all``
to work correctly.
"""

from app.models.user import User
from app.models.notebook import Notebook
from app.models.note import Note
from app.models.tag import Tag, NoteTag

__all__ = ["User", "Notebook", "Note", "Tag", "NoteTag"]
