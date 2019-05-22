from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.conf import settings
import threading
import functools
import pika

# import django_rq
from .models import (
    DeliveryTaskState, 
    DeliveryTask, 
    DeliveryStateTransition
)

class DeliveryTaskConsumer(AsyncJsonWebsocketConsumer):
    mq_channel = settings.PIKA_CHANNEL
    group_names = {
            "dp": "delivery_persons",
            "sm": "store_manager"
    }
    events = {
        "CREATE_TASK": "CREATE_TASK",
        "JOIN": "JOIN",
        "TASK_ACCEPTED": "TASK_ACCEPTED",
        "TASK_DECLINED": "TASK_DECLINED",
        "TASK_CANCELLED": "TASK_CANCELLED"
    }
    sm_set = set()
    dp_set = set()
    current_task = None

    async def connect(self):
        requser = self.scope["user"]
        if requser.is_authenticated:
            if requser.is_storage_manager or requser.is_delivery_person:
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()


    async def disconnect(self, close_code):
        # Leave the rooms: TODO
        await self.channel_layer.group_discard(
            self.group_names["sm"],
            self.channel_name
        )


    async def receive(self, text_data):
        response = json.loads(text_data)
        event = response.get("event", None)
        # try:
        message = response.get("message", None)
        if event == self.events["JOIN"]:
            await self.join(group_name = message)
        elif event == self.events["CREATE_TASK"]:
            await self.create_task(message)
        elif event == self.events["TASK_CANCELLED"]:
            await self.task_cancelled(message)

        elif event == self.events["TASK_ACCEPTED"]:
            await self.task_accepted(message)
        elif event == self.events["TASK_DECLINED"]:
            await self.task_declined(message)

        # except Exception as e:
        #     await self.send_json({"error": str(e)})


    # Helping Methods
    async def join(self, group_name):
        print(f"New {group_name} joined with id: {self.channel_name}")
        await self.channel_layer.group_add(
            self.group_names[group_name],
            self.channel_name,
        )
        if group_name == "dp":
            self.dp_set.add(self.channel_name)
            await self.receive_task()
        elif group_name == "sm":
            self.sm_set.add(self.channel_name)
            

    async def create_task(self, message):
        # sending message to sm
        new_state = await self.create_new_state(message["task"]["id"])
        await self.enqueue(message)
        await self.channel_layer.group_send(
            self.group_names["sm"],
            {
                'type': 'send_message',
                'message': message,
            }
        )
        await self.receive_task()


    async def task_cancelled(self, message):
        print("Task Cancelled", message)

    async def task_accepted(self, message):
        """
        TODO: 
            1. Create new state: Accepted, assign to the task with task_id
            2. Assign the task to the current Delivery Person
            3. dispatch from the queue, and show the next available task to other users
        """
        print("Task Accepted", message)

    async def task_declined(self, message):
        print("Task Declined", message)



    # Helping Methods
    async def enqueue(self, message):
        print("Enqueue", message)
        self.mq_channel.basic_publish(exchange='',
                            routing_key=message["task"]["priority"],
                            body=json.dumps(message["task"]),
                            properties=pika.BasicProperties(
                                delivery_mode = 2, # make message persistent
                            )
                    )


    async def get_task_from_queue(self, queue):
        method, prop, message =  self.mq_channel.basic_get(queue, no_ack = False)
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


    async def receive_task(self):
        task = await self.get_task_from_queue(queue="high")
        if not task:
            task = await self.get_task_from_queue(queue="medium")
            if not task:
                task = await self.get_task_from_queue(queue="low")

        print(f"Recieved Task {task}")
        print(self.current_task, "Current task")

        if task:
            self.current_task = task
            # reject the message and requeue it
            self.mq_channel.basic_reject(int(task["delivery_tag"]), requeue = True)
            print("Message rejected")

            await self.channel_layer.group_send(
                self.group_names["dp"],
                {
                    'type': 'send_message',
                    'message': task["message"],
                }
            )
        else:
            # No task in any queue
            pass


    # def on_message(self, channel, method, properties, body):
    #     print(body)
    #     self.mq_channel.basic_ack(delivery_tag=method.delivery_tag)


    @database_sync_to_async
    def create_new_state(self, task_id):
        state= DeliveryTaskState.objects.create(state = "new")
        transition = DeliveryStateTransition(task_id = task_id, state = state)
        transition.save()
        return state

    @database_sync_to_async
    def create_accepted_state(self, task_id):
        state= DeliveryTaskState.objects.create(state = "accepted")
        transition = DeliveryStateTransition(task_id = task_id, state = state)
        transition.save()
        return state

    async def send_message(self, res):
        message = res["message"]
        await self.send(text_data=json.dumps({
            "message": message,
        }))
