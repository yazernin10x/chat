import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from apps.rooms.models import Room, RoomMember
from apps.chat_messages.models import Message
from apps.rooms.signals import room_join_success, room_leave_success

User = get_user_model()


class RoomConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_pk = None
        self.room_group_name = None
        self.room = None

        # User
        self.user = None
        self.user_inbox = None  # message privés

    def connect(self):
        self.room_pk = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"room_{self.room_pk}"
        self.room = Room.objects.get(pk=self.room_pk)

        # User
        self.user = self.scope["user"]
        self.user_inbox = f"inbox_{self.user.username}"

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
                instance=self.room,
                user=self.user,
                action=Message.Action.SET_STATUS,
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
                instance=self.room,
                user=self.user,
                action=Message.Action.SET_STATUS,
            )

    def receive(self, text_data=None, bytes_data=None):
        content = json.loads(text_data)["content"]

        if not self.user.is_authenticated:
            return

        if content.startswith("@"):
            split = content.split(" ", 1)
            target, target_msg = split[0][1:], split[1]
            recipient = User.objects.get(username=target)

            # Création du message privé
            message = Message.objects.create(
                room=self.room,
                sender=self.user,
                content=target_msg,
                action=Message.Action.PRIVATE,
            )
            message.recipients.add(recipient)
            message.save()

            # send private message to the target
            async_to_sync(self.channel_layer.group_send)(
                f"inbox_{recipient.username}",
                {
                    "type": "private_message",
                    "sender": message.sender.username,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(timespec="seconds"),
                    "action": message.action,
                },
            )

            # send private message delivered to the user
            self.send(
                json.dumps(
                    {"type": "private_message_sent", "recipient": recipient.username}
                )
            )
        else:
            # Création du message normal
            message = Message.objects.create(
                room=self.room,
                sender=self.user,
                content=content,
                action=Message.Action.PUBLIC,
            )
            # Ajout des membres de la salle au message
            room_members = self.room.members.exclude(pk=self.user.pk).all()
            message.recipients.set(room_members)
            message.save()

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "room_message",
                    "sender": message.sender.username,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(timespec="seconds"),
                    "action": Message.Action.PUBLIC,
                },
            )

    def room_message(self, event):
        self.send(text_data=json.dumps({"type": "room_message"} | event))

    def room_join(self, event):
        print(event, "***********************")
        self.send(text_data=json.dumps({"type": "room_join"} | event))

    def room_leave(self, event):
        self.send(text_data=json.dumps({"type": "room_leave"} | event))

    def private_message(self, event):
        self.send(text_data=json.dumps({"type": "private_message"} | event))

    def private_message_delivered(self, event):
        self.send(text_data=json.dumps({"type": "private_message_delivered"} | event))
