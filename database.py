import time
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
import sqlite3

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    token: Optional[str] = Field(default=None, index=True)


class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    markdown: str
    user_id: int = Field(foreign_key="user.id")
    s3_image: str
    ts_created: int = Field(default=int(time.time()))

    def to_dict(self):
        return {
            "id": self.id,
            "markdown": self.markdown,
            "user_id": self.user_id,
            "s3_image": self.s3_image,
            "ts_created": self.ts_created
        }


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
