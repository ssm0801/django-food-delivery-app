import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Booking, ChatMessage
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'chat_{self.booking_id}'
        
        # Check authentication before accepting
        if not self.scope['user'].is_authenticated:
            await self.close(code=4001)
            return
            
        # Quick access check
        has_access = await self.check_booking_access()
        if not has_access:
            await self.close(code=4003)
            return
        
        await self.accept()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if not message:
                return
                
            # Send message immediately to group
            from datetime import datetime
            timestamp = datetime.now().strftime('%H:%M')
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.scope['user'].username,
                    'timestamp': timestamp
                }
            )
            
            # Save to database asynchronously (non-blocking)
            await self.save_message(message)
            
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def check_booking_access(self):
        try:
            booking = Booking.objects.get(id=self.booking_id)
            user = self.scope['user']
            
            # Check if user has access to this booking
            has_access = booking.customer == user or booking.delivery_partner == user
            
            # Check if booking allows chat (has delivery partner and not pending/cancelled)
            chat_allowed = (booking.delivery_partner is not None and 
                          booking.status not in ['pending', 'cancelled'])
            
            return has_access and chat_allowed
        except Booking.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, message):
        booking = Booking.objects.get(id=self.booking_id)
        return ChatMessage.objects.create(
            booking=booking,
            sender=self.scope['user'],
            message=message
        )