import aio_pika
import json
from aio_pika import ExchangeType

from app.config.logger import logger
from app.config.b_settings import settings
from app.config import client_rabbit


async def send_to_rabbit(message: dict):
    """
    Public sms on RabbitMQ
    :parm message: data-dict publicaition on RabbitMQ
    :parm message_type: type sms (password_reset, email_verification)
    """
    try:
        async with client_rabbit.get_rabbitmq_connection() as connection:
            channel = await connection.channel()
            # обьявляем обменник
            exchange = await channel.declare_exchange(
                name="sending_mail", type=ExchangeType.DIRECT, durable=True
            )
            
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=message.get("queue_name"),
            )
    except Exception as err:
        print(str(err))
