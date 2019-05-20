from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
# import django_rq
from .models import (
    DeliveryTaskState, 
    DeliveryTask, 
    DeliveryStateTransition
)

class DeliveryTaskConsumer(AsyncJsonWebsocketConsumer):
    group_names = {
            "dp": "delivery_persons",
            "sm": "store_manager"
    }
    events = {
        "CREATE_TASK": "CREATE_TASK",
        "JOIN": "JOIN"
    }
    sm_set = set()
    dp_set = set()

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
        elif group_name == "sm":
            self.sm_set.add(self.channel_name)


    async def create_task(self, message):
        # sending message to sm
        new_state = await self.create_new_state(message["task"]["id"])
        await self.save_task_to_queue(message)
        await self.channel_layer.group_send(
            self.group_names["sm"],
            {
                'type': 'task_message',
                'message': message,
            }
        )

    async def save_task_to_queue(self, message):
        pass
        # queue = django_rq.get_queue(message["task"]["priority"], 
        #         autocommit=True, 
        #         is_async=True, 
        # )
        # queue.enqueue(self.show_task, message = message)


    def show_task(self, message):
        # Sending message to dp
        self.channel_layer.group_send(
            self.group_names["dp"],
            {
                'type': 'task_message',
                'message': message,
            }
        )


    @database_sync_to_async
    def create_new_state(self, task_id):
        state= DeliveryTaskState.objects.create(state = "new")
        transition = DeliveryStateTransition(task_id = task_id, state = state)
        transition.save()
        return state


    async def task_message(self, res):
        message = res["message"]
        await self.send(text_data=json.dumps({
            "message": message,
        }))
