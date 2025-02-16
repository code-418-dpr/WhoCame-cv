import asyncio

from db.seeder import seed


def seed_sync() -> None:
    asyncio.run(seed())
