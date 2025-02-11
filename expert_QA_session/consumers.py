import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from userauths.models import User_Reg
from .models import ChatMessage, ExpertSession

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.expert_id = self.scope['url_route']['kwargs']['expert_id']
        self.room_name = f"chat_{self.expert_id}"
        self.room_group_name = f"chat_room_{self.expert_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender']
        recipient_id = text_data_json['recipient']

        # Save message to database
        await self.save_message(sender_id, recipient_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_id,
                'timestamp': timezone.now().strftime('%I:%M %p')
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, message):
        sender = User_Reg.objects.get(uid=sender_id)
        recipient = User_Reg.objects.get(uid=recipient_id)
        
        ChatMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message=message
        )
