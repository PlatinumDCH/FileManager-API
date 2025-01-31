from aio_pika import connect_robust, exceptions
from aio_pika.abc import AbstractRobustConnection
import asyncio
from contextlib import asynccontextmanager

from app.config.b_settings import settings

class RabbitMQConnectionManager:
    def __init__(self, url: str, retries: int = 5, delay: int = 1):
        """
        Args:
            url (str): url для подключения
            retries (int, optional): count try connection. Defaults to 5.
            delay (int, optional): pause try connection. Defaults to 1.
        """
        self.url = url
        self.retries = retries
        self.delay = delay
        self.connection: AbstractRobustConnection | None = None

    async def connect(self) -> AbstractRobustConnection:
        """return activ connetion or create new"""
        if self.connection and not self.connection.is_closed:
            return self.connection

        for attempt in range(self.retries):
            try:
                self.connection = await connect_robust(self.url)
                return self.connection

            except exceptions.AMQPConnectionError as err:
                if attempt == self.retries - 1:  # if last attempt
                    raise RuntimeError("Could not connect to RabbitMQ")
                await asyncio.sleep(self.delay)
        raise RuntimeError("Unexpected error: connection loop exited without returning")
    
    async def close(self):
        """close current connection if open"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


    async def __aenter__(self) -> AbstractRobustConnection:
        """context manager for auto connection"""

        return await self.connect()

    async def __aexit__(self, exc_type, exc_value, traceback):
        """context manager for auto close"""
        await self.close()


@asynccontextmanager
async def get_rabbitmq_connection():
    manager = RabbitMQConnectionManager(url=settings.RABBITMQ_URL)
    connection = await manager.connect()
    try:
        yield connection
    finally:
        await manager.close()