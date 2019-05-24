import pika
import json
from django.conf import settings


class RabbitMQBroker(object):
    def __init__(self):
        # params = pika.URLParameters(settings.AMPQ_URL)
        # params.socket_timeout = 5

        # self.CONNECTION = pika.BlockingConnection(params)
        self.CONNECTION = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.CHANNEL = self.CONNECTION.channel()
        self.CHANNEL.queue_declare(queue='high', durable=True)
        self.CHANNEL.queue_declare(queue='medium', durable=True)
        self.CHANNEL.queue_declare(queue='low', durable=True)
        self.CHANNEL.basic_qos(prefetch_count=1)

    async def basic_publish(self, message):
        self.CHANNEL.confirm_delivery()
        successful = self.CHANNEL.basic_publish(exchange='',
                                                routing_key=message["task"]["priority"],
                                                body=json.dumps(
                                                    message["task"]),
                                                properties=pika.BasicProperties(
                                                    delivery_mode=2,  # make message persistent
                                                ),
                                                )
        if not successful:
            await self.basic_publish(message)
        print("Basic publish", successful)

    async def basic_get(self, queue):
        method, prop, message = self.CHANNEL.basic_get(queue, no_ack=False)
        if message:
            return {
                "message": json.loads(message),
                "delivery_tag": method.delivery_tag,
            }
        return None

    async def basic_reject(self, delivery_tag, requeue=True):
        self.CHANNEL.basic_reject(delivery_tag, requeue=requeue)

    async def basic_consume(self, queue, no_ack=True):
        self.CHANNEL.basic_consume(self.on_message, queue,  no_ack=no_ack)

    def on_message(self, channel, method, properties, body):
        print(body, channel, method)

