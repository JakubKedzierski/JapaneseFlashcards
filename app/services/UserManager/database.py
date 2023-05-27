from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData()

users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_email", String),
    Column("user_phone", String),
    Column("token", String),
    Column("level", String)
)

metadata.create_all(engine)

database = Database(DATABASE_URL)
