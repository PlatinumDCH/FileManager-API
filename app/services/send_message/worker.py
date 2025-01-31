from aio_pika import IncomingMessage, ExchangeType
import asyncio
import json
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pathlib import Path

from app.config.logger import logger
from app.config.b_settings import settings
from app.config.client_rabbit import get_rabbitmq_connection


BASE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Contact server",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=BASE_DIR,
)


async def process_message(message: IncomingMessage):
    """Processing an incoming message from a queue"""
    try:
        async with message.process():
            try:
                task_data = json.loads(message.body)
                email = task_data.get('email')
                username = task_data.get('username')
                host = task_data.get('host')
                message_type = task_data.get('queue_name')
                token = task_data.get('token')
            except KeyError as err:
                return

            if message_type == "reset_password":
                message_schema = MessageSchema(
                    subject="Changer server-pas",
                    recipients=[email],
                    template_body={"host": host, "username": username, "token": token},
                    subtype=MessageType.html,
                )
                logger.info(f'{host}password_reset/{token}')

                template_name = "password_reset/password_reset.html"

            elif message_type == "confirm_email":
                message_schema = MessageSchema(
                    subject="Changer server-email",
                    recipients=[email],
                    template_body={"host": host, "username": username, "token": token},
                    subtype=MessageType.html,
                )
                exemple = f'{host}email_process/confirmed_email/{token}'
                logger.info(exemple)
                template_name = "email_confirm/email_confirm.html"

            else:
                return
            fm = FastMail(conf)
            await fm.send_message(message_schema, template_name=template_name)
            logger.info('sending message')
    except Exception as err:
        raise


async def main():
    """Основной воркер для обработки сообщений из RabbitMQ"""
    max_retires = 5  # max value repit try
    retry_count = 0  # counter trys
    while retry_count < max_retires:
        try:
            async with get_rabbitmq_connection() as connection:

                # Announcing exchanger
                async with connection:
                    channel = await connection.channel()
                    exchange = await channel.declare_exchange(
                        name="sending_mail", type=ExchangeType.DIRECT, durable=True
                    )

                    # Announcing a queue and linking it to routing_key
                    queue = await channel.declare_queue("email_queue", durable=True)
                    await queue.bind(exchange, routing_key="reset_password")
                    await queue.bind(exchange, routing_key="confirm_email")

                    # run processing message
                    await queue.consume(process_message)
                    # await new message
                    while True:
                        await asyncio.sleep(1)

        except Exception as err:
            retry_count += 1
            if retry_count < max_retires:
                await asyncio.sleep(5)
            else:
                print("Max retry attempts reached.Exiting")
        finally:
            print("Worker finished.")


if __name__ == "__main__":
    print("Воркер работат")
    asyncio.run(main())
