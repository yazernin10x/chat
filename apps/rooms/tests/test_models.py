from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from apps.rooms.models import Room, RoomMember

User = get_user_model()


class RoomModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.room = Room.objects.create(name="test_room")

    def test_room_creation(self):
        """Test la création basique d'un salon"""
        self.assertEqual(self.room.name, "test_room")
        self.assertEqual(self.room.online_count, 0)

    def test_room_unique_name(self):
        """Test que le nom du salon doit être unique"""
        with self.assertRaises(IntegrityError):
            Room.objects.create(name="test_room")

    def test_room_join_leave(self):
        """Test les méthodes join et leave"""
        self.room.join(self.user)
        self.assertEqual(self.room.online_count, 1)

        self.room.leave(self.user)
        self.assertEqual(self.room.online_count, 0)

    def test_room_str_representation(self):
        """Test la représentation string du salon"""
        expected = "Salon 'test_room' | 0 utilisateur(s) en ligne"
        self.assertEqual(str(self.room), expected)

    def test_room_repr_representation(self):
        """Test la représentation repr du salon"""
        expected = "Room(name='test_room', online_count=0)"
        self.assertEqual(repr(self.room), expected)


class RoomMemberModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.room = Room.objects.create(name="test_room")
        self.room_member = RoomMember.objects.create(user=self.user, room=self.room)

    def test_room_member_creation(self):
        """Test la création basique d'une adhésion"""
        self.assertEqual(self.room_member.user, self.user)
        self.assertEqual(self.room_member.room, self.room)

    def test_unique_membership(self):
        """Test qu'un utilisateur ne peut pas rejoindre deux fois le même salon"""
        with self.assertRaises(IntegrityError):
            RoomMember.objects.create(user=self.user, room=self.room)

    def test_room_member_str_representation(self):
        """Test la représentation string de l'adhésion"""
        expected = f"{self.room_member.user.username} - {self.room_member.room.name}"
        self.assertEqual(str(self.room_member), expected)

    def test_room_member_repr_representation(self):
        """Test la représentation repr de l'adhésion"""
        expected = (
            f"RoomMember(user={self.room_member.user.username!r}, "
            f"room={self.room_member.room.name!r}, "
            f"joined_at={self.room_member.joined_at.strftime('%d/%m/%Y %H:%M')!r})"
        )
        self.assertEqual(repr(self.room_member), expected)

    def test_room_member_ordering(self):
        """Test que les adhésions sont ordonnées par date d'adhésion"""
        user2 = User.objects.create_user(username="testuser2", password="testpass123")
        room_member2 = RoomMember.objects.create(user=user2, room=self.room)
        room_members = RoomMember.objects.all()
        self.assertEqual(room_members[0], room_member2)
        self.assertEqual(room_members[1], self.room_member)
