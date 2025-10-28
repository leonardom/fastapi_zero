from datetime import datetime

from sqlalchemy import func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ModelBase, table_registry
from .todo import Todo


@table_registry.mapped_as_dataclass
class User(ModelBase):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=func.now(),
    )

    todos: Mapped[list['Todo']] = relationship(
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )
