import aiosqlite
from datetime import datetime

DB_NAME = 'TGUsers.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                time TEXT,
                city TEXT
            )
        ''')
        await db.commit()

async def add_user(user_id, username, first_name, last_name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        await db.commit()

async def enable_notifications(user_id, city, time):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users
            SET time = ?, city = ?
            WHERE user_id = ?
        ''', (time, city, user_id))
        await db.commit()

async def disable_notifications(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users
            SET time = NULL, city = NULL
            WHERE user_id = ?
        ''', (user_id,))
        await db.commit()