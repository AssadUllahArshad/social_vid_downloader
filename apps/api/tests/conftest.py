import time

import pytest

from app import main


class MemoryStore:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        item = self.data.get(key)
        return item[0] if item and item[1] > time.time() else None

    async def set(self, key, value, ttl, nx=False):
        if nx and await self.get(key) is not None:
            return False
        self.data[key] = (value, time.time() + ttl)
        return True

    async def delete(self, key):
        self.data.pop(key, None)

    async def compare_delete(self, key, owner):
        if await self.get(key) == owner:
            await self.delete(key)
            return True
        return False

    async def increment(self, key, ttl):
        value = (await self.get(key) or 0) + 1
        await self.set(key, value, ttl)
        return value

    async def ping(self):
        return True

    async def close(self):
        pass


@pytest.fixture
def memory_store(monkeypatch, tmp_path):
    store = MemoryStore()
    monkeypatch.setattr(main, "store", store)
    monkeypatch.setattr(main, "root", tmp_path / "media")
    return store
