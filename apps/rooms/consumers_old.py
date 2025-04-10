import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from apps.rooms.models import Room
from apps.chat_messages.models import Message
from apps.rooms.signals import room_join_success, room_leave_success


class RoomConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_pk = None
        self.room_group_name = None
        self.room = None
        self.user = None
        self.user_inbox = None  # message privés

    def connect(self):
        self.room_pk = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"room_{self.room_pk}"
        self.room = Room.objects.get(pk=self.room_pk)
        self.user = self.scope["user"]
        self.user_inbox = f"inbox_{self.user.pk}"
        self.accept()

        # add user to room group for all messages
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        # add user inbox group for private messages
        async_to_sync(self.channel_layer.group_add)(
            self.user_inbox,
            self.channel_name,
        )

        # Set user online status
        if self.room.members.filter(pk=self.user.pk).exists():
            self.user.set_online_status(True)
            room_join_success.send(
                sender=Room,
                room=self.room,
                user=self.user,
                type_message=Message.Action.JOIN,
            )

    def disconnect(self, close_code):
        # remove user from room group for all messages
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        # remove user from inbox group for private messages
        async_to_sync(self.channel_layer.group_discard)(
            self.user_inbox,
            self.channel_name,
        )

        # Set user offline status
        if self.room.members.filter(pk=self.user.pk).exists():
            self.user.set_online_status(False)
            room_leave_success.send(
                sender=Room,
                room=self.room,
                user=self.user,
                type_message=Message.Action.LEAVE,
            )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        if not self.user.is_authenticated:
            return

        # Création du message normal
        message = Message.objects.create(
            room=self.room, sender=self.user, content=message
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "room_message",
                "username": self.user.username,
                "message": message.content,
                "created_at": message.created_at.isoformat(timespec="seconds"),
                "sender": message.sender.username,
            },
        )

    def room_message(self, event):
        self.send(text_data=json.dumps({"type": "room_message"} | event))

    def room_join(self, event):
        self.send(text_data=json.dumps({"type": "room_join"} | event))

    def room_leave(self, event):
        self.send(text_data=json.dumps({"type": "room_leave"} | event))
