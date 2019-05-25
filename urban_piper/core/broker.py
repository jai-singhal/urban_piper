import pika
import json
from django.conf import settings
import logging


class RabbitMQBroker(object):
    def __init__(self):
        # params = pika.URLParameters(settings.AMPQ_URL)
        # self.CONNECTION = pika.BlockingConnection(params)
        self.connect()

    def connect(self):
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
            #reconnect
            logging.error(str(e))
            self.connect()

    async def basic_consume(self, queue, auto_ack=True):
        try:
            method, header, body = self.CHANNEL.basic_get(
                queue=queue, auto_ack=auto_ack)
            if method:
                if method.NAME == 'Basic.GetEmpty':
                    return None
                else:
                    # self.CHANNEL.basic_ack(delivery_tag=method.delivery_tag)
                    return {
                        "message": json.loads(body),
                        "delivery_tag": method.delivery_tag,
                    }
        except Exception as e:
            logging.error(str(e))
            self.connect()
        return None
