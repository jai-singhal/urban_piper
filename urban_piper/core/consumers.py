from channels.generic.websocket import AsyncWebsocketConsumer
import json
import django_rq
from .models import DeliveryTaskState, DeliveryTask

events = {
    "CREATE_TASK": "CREATE_TASK",
}


class StorageManagerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "dp_room"

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event = text_data_json["event"]
        message = text_data_json["message"]
        if event == "CREATE_TASK":
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'task_message',
                    'message': message,
                }
            )
        elif event == "":
            pass
        else:
            pass

    async def task_message(self, res):
        message = res["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
















class DeliveryPersonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "sm_room"
        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'task_message',
                'message': message
            }
        )

    # Receive message from room group
    async def task_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))






