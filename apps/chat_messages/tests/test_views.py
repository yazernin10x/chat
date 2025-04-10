from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.rooms.models import Room
from apps.chat_messages.models import Message
from textwrap import shorten

User = get_user_model()


class MessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.room = Room.objects.create(name="test_room")
        self.message = Message.objects.create(
            sender=self.user, room=self.room, content="Test message"
        )

    def test_message_creation(self):
        """Test la création basique d'un message"""
        self.assertEqual(self.message.content, "Test message")
        self.assertEqual(self.message.sender, self.user)
        self.assertEqual(self.message.room, self.room)

    def test_message_ordering(self):
        """Test que les messages sont ordonnés par date de création"""
        message2 = Message.objects.create(
            sender=self.user, room=self.room, content="Second message"
        )
        messages = Message.objects.all()
        self.assertEqual(messages[0], self.message)
        self.assertEqual(messages[1], message2)

    def test_message_str_representation(self):
        """Test la représentation string du message"""
        expected = (
            f"[{self.message.created_at.strftime('%d/%m/%Y %H:%M')}] "
            f"{self.message.sender.username} dans {self.message.room.name}: "
            f"{shorten(self.message.content, width=50, placeholder='...')}"
        )
        self.assertEqual(str(self.message), expected)

    def test_message_repr_representation(self):
        """Test la représentation repr du message"""
        expected = (
            f"Message(sender={self.message.sender.username!r}, "
            f"room={self.message.room.name!r}, "
            f"content={shorten(self.message.content, width=50, placeholder='...')!r})"
        )
        self.assertEqual(repr(self.message), expected)
