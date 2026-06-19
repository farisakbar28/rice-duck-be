import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import User


class UserRepository:
    def create(self, *, name: str, email: str, password_hash: str) -> User:
        now = datetime.now(timezone.utc)
        user = User(
            id=str(uuid4()),
            name=name,
            email=email.lower(),
            password_hash=password_hash,
            created_at=now,
            updated_at=now,
        )
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (id, name, email, password_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user.id,
                    user.name,
                    user.email,
                    user.password_hash,
                    user.created_at.isoformat(),
                    user.updated_at.isoformat(),
                ),
            )
        return user

    def get_by_email(self, email: str) -> User | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
                (email.lower(),),
            ).fetchone()
        return self._to_model(row) if row else None

    def get_by_id(self, user_id: str) -> User | None:
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        return self._to_model(row) if row else None

    def _to_model(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


user_repository = UserRepository()
