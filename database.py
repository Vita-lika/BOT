import logging
from typing import Optional, List
import asyncpg
from asyncpg import Connection, Pool

from models import Quote, User

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config):
        self.config = config
        self.pool: Optional[Pool] = None
    
    async def create_pool(self):
        """Создание пула подключений"""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.name
        )
    
    async def create_tables(self):
        """Создание таблиц в БД"""
        await self.create_pool()
        
        async with self.pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    text TEXT NOT NULL,
                    author TEXT,
                    tags TEXT[],
                    source TEXT,
                    added_by BIGINT REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT NOW(),
                    published BOOLEAN DEFAULT FALSE
                )
            """)
            
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS banned_words (
                    id SERIAL PRIMARY KEY,
                    word TEXT NOT NULL UNIQUE
                )
            """)
    
    async def add_user(self, user: User):
        """Добавление пользователя в БД"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO users (id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name
            """, user.id, user.username, user.first_name, user.last_name)
    
    async def add_quote(self, quote: Quote) -> int:
        """Добавление цитаты в БД"""
        async with self.pool.acquire() as connection:
            return await connection.fetchval("""
                INSERT INTO quotes (text, author, tags, source, added_by)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """, quote.text, quote.author, quote.tags, quote.source, quote.added_by)
    
    async def get_random_quote(self) -> Optional[Quote]:
        """Получение случайной цитаты"""
        async with self.pool.acquire() as connection:
            record = await connection.fetchrow("""
                SELECT * FROM quotes
                WHERE published = TRUE
                ORDER BY RANDOM()
                LIMIT 1
            """)
            return Quote(**record) if record else None
    
    async def get_banned_words(self) -> List[str]:
        """Получение списка запрещенных слов"""
        async with self.pool.acquire() as connection:
            records = await connection.fetch("SELECT word FROM banned_words")
            return [r['word'] for r in records]
    
    async def add_banned_word(self, word: str):
        """Добавление запрещенного слова"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                INSERT INTO banned_words (word) VALUES ($1)
                ON CONFLICT (word) DO NOTHING
            """, word.lower())
    
    async def mark_quote_as_published(self, quote_id: int):
        """Пометить цитату как опубликованную"""
        async with self.pool.acquire() as connection:
            await connection.execute("""
                UPDATE quotes SET published = TRUE WHERE id = $1
            """, quote_id)