import pika
import json

class RabbitMQBroker(object):
    def __init__(self):
        self.CONNECTION = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.CHANNEL = self.CONNECTION.channel()
        self.CHANNEL.queue_declare(queue='high')
        self.CHANNEL.queue_declare(queue='medium')
        self.CHANNEL.queue_declare(queue='low')
        self.CHANNEL.basic_qos(prefetch_count=1)
    
    @property
    def get_channel(self):
        return self.CHANNEL

    @property
    def get_connection(self):
        return self.CONNECTION

    async def basic_publish(self, message):
        self.CHANNEL.basic_publish(exchange='',
                    routing_key=message["task"]["priority"],
                    body=json.dumps(message["task"]),
                    properties=pika.BasicProperties(
                        delivery_mode = 2, # make message persistent
                    )
            )

    async def basic_get(self, queue):
        method, prop, message =  self.CHANNEL.basic_get(queue, no_ack = False)
        if not message:
            print(f"No tasks in {queue} queue")
        else:
            print("Message recieved")
            message = json.loads(message)
            task = {
                "message": message,
                "delivery_tag": method.delivery_tag,
            }
            return task
        return None