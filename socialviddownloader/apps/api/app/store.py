import asyncio
import json
import sqlite3
import time

from redis.asyncio import Redis

from .config import settings


class RedisStore:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)

    async def get(self, key):
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key, value, ttl, nx=False):
        return await self.redis.set(key, json.dumps(value), ex=ttl, nx=nx)

    async def delete(self, key):
        await self.redis.delete(key)

    async def compare_delete(self, key, owner):
        return await self.redis.eval(
            "if redis.call('GET',KEYS[1])==ARGV[1] then return redis.call('DEL',KEYS[1]) end; return 0", 1, key, json.dumps(owner)
        )

    async def increment(self, key, ttl):
        return await self.redis.eval(
            "local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],ARGV[1]) end; return n", 1, key, ttl
        )

    async def ping(self):
        return await self.redis.ping()

    async def close(self):
        await self.redis.aclose()


class SQLiteStore:
    """Explicit local-development store. Never a silent Redis fallback."""

    def _run(self, action, key=None, value=None, ttl=60, nx=False):
        with sqlite3.connect(settings.local_state_path, timeout=10) as db:
            db.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL, expires REAL NOT NULL)")
            db.execute("BEGIN IMMEDIATE")
            now = time.time()
            db.execute("DELETE FROM state WHERE expires <= ?", (now,))
            row = db.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
            if action == "get":
                return json.loads(row[0]) if row else None
            if action == "compare_delete":
                if row and json.loads(row[0]) == value:
                    db.execute("DELETE FROM state WHERE key = ?", (key,))
                    return True
                return False
            if action == "delete":
                db.execute("DELETE FROM state WHERE key = ?", (key,))
                return True
            if action == "increment":
                value = json.loads(row[0]) + 1 if row else 1
                if row:
                    db.execute("UPDATE state SET value=? WHERE key=?", (json.dumps(value), key))
                    return value
            if action == "set" and nx and row:
                return False
            db.execute("INSERT OR REPLACE INTO state VALUES (?, ?, ?)", (key, json.dumps(value), now + ttl))
            return value if action == "increment" else True

    async def get(self, key):
        return await asyncio.to_thread(self._run, "get", key)

    async def set(self, key, value, ttl, nx=False):
        return await asyncio.to_thread(self._run, "set", key, value, ttl, nx)

    async def delete(self, key):
        return await asyncio.to_thread(self._run, "delete", key)

    async def compare_delete(self, key, owner):
        return await asyncio.to_thread(self._run, "compare_delete", key, owner)

    async def increment(self, key, ttl):
        return await asyncio.to_thread(self._run, "increment", key, None, ttl)

    async def ping(self):
        await self.get("health")
        return True

    async def close(self):
        pass


store = SQLiteStore() if settings.state_backend == "sqlite" and settings.environment == "development" else RedisStore()
