import pika
import json
from django.conf import settings
import logging


class RabbitMQBroker(object):
    def __init__(self):
        self.connect()

    def connect(self):
        AMQP_URL = settings.AMQP_URL
        # use cloudamqp url(if have) or use local amqp url.
        if AMQP_URL != "localhost":
            params = pika.URLParameters(AMQP_URL)
            self.CONNECTION = pika.BlockingConnection(params)
        else:
            self.CONNECTION = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )

        self.CHANNEL = self.CONNECTION.channel()
        self.CHANNEL.queue_declare(queue='high', durable=True)
        self.CHANNEL.queue_declare(queue='medium', durable=True)
        self.CHANNEL.queue_declare(queue='low', durable=True)
        self.CHANNEL.basic_qos(prefetch_count=1)
        self.CHANNEL.confirm_delivery()

    async def basic_publish(self, message):
        try:
            self.CHANNEL.basic_publish(exchange='',
                                       routing_key=message["task"]["priority"],
                                       body=json.dumps(message["task"]),
                                       properties=pika.BasicProperties(
                                           content_type='text/plain',
                                           delivery_mode=2
                                       ),
                                       mandatory=True
                                       )
        except Exception as e:
            # reconnect
            logging.error(str(e))
            self.connect()

    async def basic_get(self, queue, auto_ack=False):
        try:
            method, header, body = self.CHANNEL.basic_get(
                queue=queue, auto_ack=auto_ack)
            if method:
                if method.NAME == 'Basic.GetEmpty':
                    return None
                else:
                    # delivery_tag is a unique identifier assigned to each message,
                    return {
                        "message": json.loads(body),
                        "delivery_tag": method.delivery_tag,
                    }
        except Exception as e:
            logging.error(str(e))
            self.connect()
        return None

    async def basic_ack(self, delivery_tag):
        self.CHANNEL.basic_ack(delivery_tag=delivery_tag, multiple=False)

    async def basic_nack(self, delivery_tag):
        self.CHANNEL.basic_nack(delivery_tag=delivery_tag,
                                multiple=False, requeue=True)
