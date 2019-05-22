from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction
import json
import threading
import pika
from .broker import RabbitMQBroker
from .events import events
from .models import (
    DeliveryTaskState, 
    DeliveryTask, 
    DeliveryStateTransition
)

class DeliveryTaskConsumer(AsyncJsonWebsocketConsumer):
    broker = RabbitMQBroker()
    group_names = {
            "dp": "delivery_persons",
            "sm": "store_manager"
    }
    events = events

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
        elif event == self.events["TASK_COMPLETED"]:
            await self.task_completed(message)
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
        # INdividual person group format: user-{dp/sm}-{username}
        await self.channel_layer.group_add(
            "user-%s-%s" %(self.group_names[group_name], self.scope["user"].username),
            self.channel_name,
        )

        if group_name == "dp":
            await self.receive_task()
        elif group_name == "sm":
            pass
            

    async def create_task(self, message):
        # sending message to sm
        await self.create_state(message["task"]["id"], state = "new", by = None)
        await self.broker.basic_publish(message)
        message["event"] = self.events["NEW_TASK"]
        # await self.group_send(message, self.group_names["sm"])
        await self.group_send(
            message, 
            "user-%s-%s" %(self.group_names["sm"], self.scope["user"].username)
        )    

        await self.receive_task()


    async def task_cancelled(self, message):
        print("Task Cancelled", message)


    async def task_accepted(self, message):
        """
        TODO STEPS: 
            1. Create new state: Accepted, assign to the task with task_id, and t dp
            2. dispatch from the queue, and show the next available task to other users
            3. Check if the user have more than 3 pending task
        """
        total_pending_state = self.check_total_pending_tasks(user = self.scope["user"])
        if not total_pending_state:
            await self.create_state(message["id"], state = "accepted", by = self.scope["user"])
            payload = {
                "event": self.events["TASK_ACCEPTED"],
                "message": message
            }
            await self.broker.basic_consume(message["priority"], self.on_message, False)
            await self.receive_task()
        else:
            payload = {
                "event": self.events["TASK_PENDING"],
                "message": "USER EXCEEDS TOTAL PENDING TASKS"
            }    
        await self.group_send(
            payload, 
            "user-%s-%s" %(self.group_names["dp"], self.scope["user"].username)
        )    


    async def task_declined(self, message):
        """
        TODO STEPS: 
            1. Create new state: declined.
            2. Remove the task from user-dp dashboard
            3. Enqueue this task to queue
            4. Send this task to all dp-users
        """
        await self.create_state(message["id"], state = "declined", by = self.scope["user"])
        payload = {
            "event": self.events["TASK_DECLINED_ACK"],
            "message": {"id": message["id"]} # only need id to identify
        }
        await self.group_send(
            payload, 
            "user-%s-%s" %(self.group_names["dp"], self.scope["user"].username)
        )

        task = self.get_task(message["id"])
        message = {
            "task": json.loads(task)
        }
        await self.broker.basic_publish(message)
        await self.receive_task()


    async def task_completed(self, message):
        """
        TODO STEPS: 
            1. Create new state: Completed.
            2. Remove the task from user-dp dashboard
        """
        await self.create_state(message["id"], state = "completed", by = self.scope["user"])
        payload = {
            "event": self.events["TASK_COMPLETED_ACK"],
            "message": {"id": message["id"]} # only need id to identify
        }
        await self.group_send(
            payload, 
            "user-%s-%s" %(self.group_names["dp"], self.scope["user"].username)
        )   
        

    async def receive_task(self):
        task = await self.broker.basic_get(queue="high")
        if not task:
            task = await self.broker.basic_get(queue="medium")
            if not task:
                task = await self.broker.basic_get(queue="low")

        print(f"Recieved Task: {task}")

        if task:
            # reject the message and requeue it
            await self.broker.basic_reject(int(task["delivery_tag"]), requeue = True)
            message = {
                "event": self.events["NEW_TASK"],
                "message": task["message"]
            }
        else:
            message = {
                "event": self.events["NEW_TASK"],
                "message": None
            }
            
        await self.group_send(message, self.group_names["dp"])


    def on_message(self, channel, method, properties, body):
        print(body)


    @transaction.atomic
    @database_sync_to_async
    def create_state(self, task_id, state, by = None):
        try:
            state_instance = DeliveryTaskState.objects.get(state = state)
            task_instance = DeliveryTask.objects.get(id = task_id)
            transition_instance = DeliveryStateTransition(
                    task_id = task_instance.id, 
                    state_id = state_instance.id,
                    by = by
                )
            transition_instance.save()

            task_instance.states.add(state_instance)
            task_instance.save()
            return True
        except Exception as e:
            print(e)
            return False


    @transaction.atomic
    def check_total_pending_tasks(self, user):
        """
            Returns True if no. of states of dp user which 
            is in pending states(accepted but not completed and declined)
            is greater than 3
            Return False otherwise
        """
        user_tasks = DeliveryStateTransition.objects.filter(by = self.request.user)
        total_pending_task = user_tasks.filter(
                state__state = "accepted").values("task").difference(
                    user_tasks.filter(state__state = "completed")).values("task").difference(
                            user_tasks.filter(state__state = "declined")).values("task").count()
        if total_pending_task >= 3:
            return True
        else:
            return False


    def get_task(self, task_id):
        return DeliveryTask.objects.get_object_in_json(task_id)

    async def group_send(self, message, group):
        """
            Helping method: SENDS the message to the group
        """
        await self.channel_layer.group_send(
            group,
            {
                'type': 'send_message',
                'message': message,
            }
        )

    async def send_message(self, res):
        """
            Callback for group_send()
        """
        await self.send(text_data=json.dumps({
            "payload": res["message"],
        }))

