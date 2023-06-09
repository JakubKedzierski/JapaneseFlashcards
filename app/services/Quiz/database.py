from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData()

users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True)
)

flashcards = Table(
    "flashcards",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String),
    Column("word", String),
    Column("hiragana", String),
    Column("kanji", String),
)

quizes = Table(
    "quizes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String),
    Column("date", String),
    Column("quiz_content", String)
)

metadata.create_all(engine)

database = Database(DATABASE_URL)
