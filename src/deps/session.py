from ..core import db_helper


async def open_session():
    async with db_helper.session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
