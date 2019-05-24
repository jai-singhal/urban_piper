from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction
import json
import pika
from urban_piper.core.broker import RabbitMQBroker
from urban_piper.core.events import events
from urban_piper.core.models import (
    DeliveryTaskState,
    DeliveryTask,
    DeliveryStateTransition
)
import logging


class DeliveryTaskConsumer(AsyncJsonWebsocketConsumer):
    broker = RabbitMQBroker()
    group_names = {
        "dp": "delivery_person",
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
        try:
            response = json.loads(text_data)
            event = response.get("event", None)
            message = response.get("message", None)
            if event == self.events["JOIN"]:
                await self.join(group_name=message)
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
            elif event == self.events["LIST_STATES"]:
                await self.list_states(message)

        except Exception as e:
            print(e)

    # Helping Methods

    async def join(self, group_name):
        print(f"New {group_name} joined with id: {self.channel_name}")
        await self.channel_layer.group_add(
            self.group_names[group_name],
            self.channel_name,
        )
        # INdividual person group format: user-{dp/sm}-{username}
        await self.channel_layer.group_add(
            "user-%s-%s" % (self.group_names[group_name],
                            self.scope["user"].username),
            self.channel_name,
        )

        if group_name == "dp":
            await self.receive_task()
        elif group_name == "sm":
            pass

    async def create_task(self, message):
        # sending message to sm
        await self.create_state(message["task"]["id"], state="new", by=None)
        await self.broker.basic_publish(message)
        await self.group_send(
            {
                "event": self.events["NEW_TASK"],
                "message": message

            },
            "user-%s-%s" % (self.group_names["sm"],
                            self.scope["user"].username)
        )

        await self.receive_task()

    async def task_cancelled(self, message):

        """
        TODO STEPS: 
            1. COnsume the task
            1. DElte the task from the database 
            2. SEnd the ack and delete the task from table

        """
        task = await self.get_task(message["id"])
        await self.broker.basic_consume(queue=task["priority"], auto_ack=True)

        await self.delete_task(message["id"])
        await self.group_send(
            {
                "event": self.events["TASK_CANCELLED_ACK"],
                "message": message
            },
            "user-%s-%s" % (self.group_names["sm"],
                            self.scope["user"].username)
        )
        await self.receive_task()

    async def task_accepted(self, message):
        """
        TODO STEPS: 
            1. GET THE total accepted states of current Delivery Person user, 
            and check condition
                If consition(more than 3 pending task) not statisifies
                    1.1. Create new state: Accepted, assign to the task with task_id.
                    1.2. dispatch from the queue, and show next available task 
                    to other dp users
                    1.3. Send a signal to STorage manager ragarding chaneg in state
                Else:
                    - Send a signal to current dp user about exceeding
                     the more than 3 pending state
        """
        total_pending_state = self.check_total_pending_tasks(
            user=self.scope["user"])
        if not total_pending_state:
            await self.create_state(message["id"], state="accepted", by=self.scope["user"])
            payload = {
                "event": self.events["TASK_ACCEPTED"],
                "message": message
            }
            await self.broker.basic_consume(queue=message["priority"], auto_ack=True)
            await self.receive_task()

            # UPDATE THE STATE SM's END
            await self.group_send(
                {
                    "event": self.events["UPDATE_STATE"],
                    "message": {"id": message["id"], "state": "Accepted"}
                },
                "user-%s-%s" % (self.group_names["sm"], message["created_by"])
            )

        else:
            payload = {
                "event": self.events["TASK_PENDING"],
                "message": "USER EXCEEDS TOTAL PENDING TASKS"
            }

        await self.group_send(
            payload,
            "user-%s-%s" % (self.group_names["dp"],
                            self.scope["user"].username)
        )

    async def task_declined(self, message):
        """
        TODO STEPS: 
            1. Create new state: declined.
            2. Send this task to all dp-users
            2. Remove the task from user-dp dashboard
            3. Enqueue this task to queue
        """
        await self.create_state(message["id"], state="declined", by=self.scope["user"])
        task = await self.get_task(message["id"])
        await self.broker.basic_publish({"task": task})

        await self.group_send(
            {
                "event": self.events["TASK_DECLINED_ACK"],
                "message": {"id": message["id"]}  # only need id to identify
            },
            "user-%s-%s" % (self.group_names["dp"],
                            self.scope["user"].username)
        )

        # UPDATE THE STATE SM's END
        await self.group_send(
            {
                "event": self.events["UPDATE_STATE"],
                "message": {"id": message["id"], "state": "Declined"}
            },
            "user-%s-%s" % (self.group_names["sm"], task["created_by"])
        )

        await self.group_send(
            {
                "event": self.events["TASK_DECLINED_ACK_SM"],
                "message": {"id": message["id"], "task": task["title"]}
            },
            "user-%s-%s" % (self.group_names["sm"], task["created_by"])
        )

        await self.receive_task()

    async def task_completed(self, message):
        """
        TODO STEPS: 
            1. Create new state: Completed.
            2. Remove the task from user-dp dashboard
        """
        await self.create_state(message["id"], state="completed", by=self.scope["user"])

        await self.group_send(
            {
                "event": self.events["TASK_COMPLETED_ACK"],
                "message": {"id": message["id"]}  # only need id to identify
            },
            "user-%s-%s" % (self.group_names["dp"],
                            self.scope["user"].username)
        )

        # UPDATE THE STATE SM's END
        task = await self.get_task(message["id"])
        await self.group_send(
            {
                "event": self.events["UPDATE_STATE"],
                "message": {"id": message["id"], "state": "Completed"}
            },
            "user-%s-%s" % (self.group_names["sm"], task["created_by"])
        )

    async def list_states(self, message):
        await self.group_send(
            {
                "event": self.events["LIST_STATES_REPLY"],
                "message": await self.get_all_states(task_id=message["id"])
            },
            "user-%s-%s" % (self.group_names["sm"],
                            self.scope["user"].username)
        )

    async def receive_task(self):
        task = await self.broker.basic_get(queue="high", auto_ack=False)
        if not task:
            task = await self.broker.basic_get(queue="medium", auto_ack=False)
            if not task:
                task = await self.broker.basic_get(queue="low", auto_ack=False)

        if task:
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

    @transaction.atomic
    @database_sync_to_async
    def create_state(self, task_id, state, by=None):
        try:
            state_instance = DeliveryTaskState.objects.get(state=state)
            task_instance = DeliveryTask.objects.get(id=task_id)
            transition_instance = DeliveryStateTransition(
                task_id=task_instance.id,
                state_id=state_instance.id,
                by=by
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
        user_tasks = DeliveryTask.objects.filter(
            states__deliverystatetransition__by=user
        ).distinct()
        total_pending_task = 0
        for task in user_tasks:
            if task.states.all().order_by("-deliverystatetransition__at").first().state == "accepted":
                total_pending_task += 1

        if total_pending_task >= 3:
            return True
        else:
            return False

    @database_sync_to_async
    def get_task(self, task_id):
        return DeliveryTask.objects.get_object_in_json(task_id)

    @database_sync_to_async
    def get_all_states(self, task_id):
        qs = DeliveryStateTransition.objects.get_states_in_json(
            task_id=task_id)
        return qs

    @database_sync_to_async
    def delete_task(self, task_id):
        DeliveryTask.objects.get(id=task_id).delete()

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
