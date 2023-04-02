from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData()

flashcards = Table(
    "flashcards",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("english_word", String),
    Column("hiragana", String),
    Column("katakana", String),
    Column("kanji", String),
    Column("romaji", String),
)

metadata.create_all(engine)

database = Database(DATABASE_URL)
