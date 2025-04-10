from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from faker import Faker

from apps.rooms.models import Room, RoomMember
from apps.chat_messages.models import Message

User = get_user_model()


class Command(BaseCommand):
    help = "Charger des données factices dans la base de données"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker("fr_FR")

    def handle(self, *args, **kwargs):
        # Supprimer la base de données si elle existe
        db_path = Path("db.sqlite3")
        if db_path.exists():
            db_path.unlink()

        # Exécuter les migrations
        self.stdout.write("Exécution des migrations...")
        call_command("makemigrations")
        call_command("migrate")

        users_created = self.create_fake_users(10)
        # rooms_created = self.create_fake_rooms(5, users_created)
        # self.create_fake_room_members(20, rooms_created, users_created)
        # self.create_fake_messages(50, rooms_created, users_created)

    def create_fake_users(self, users_number):
        users_created = []
        with open("fake_users.txt", "w") as f:
            for _ in range(users_number):
                username = self.fake.user_name()
                password = self.fake.password()
                f.write(f"Username: {username}, Password: {password}\n")

                user = User.objects.create_user(
                    username=username,
                    email=self.fake.email(),
                    password=password,
                )
                users_created.append(user)

        # Créer un kk
        kk = User.objects.create_user(
            username="kk", email="KK@example.com", password="chat#123"
        )
        users_created.append(kk)
        # Créer un admin
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="chat#123"
        )
        users_created.append(admin)

        return users_created

    # def create_fake_rooms(self, rooms_number, users_created):
    #     rooms_created = [
    #         Room.objects.create(
    #             name=self.fake.word() + " Room",
    #             description=self.fake.text(),
    #             author=self.fake.random_element(users_created),
    #         )
    #         for _ in range(rooms_number)
    #     ]
    #     return rooms_created

    # def create_fake_room_members(self, members_number, rooms_created, users_created):
    #     for _ in range(members_number):
    #         room = self.fake.random_element(rooms_created)
    #         user = self.fake.random_element(users_created)

    #         if not RoomMember.objects.filter(room=room, user=user).exists():
    #             RoomMember.objects.create(
    #                 room=room,
    #                 user=user,
    #             )

    # def create_fake_messages(self, messages_number, rooms_created, users_created):
    #     for _ in range(messages_number):
    #         room = self.fake.random_element(rooms_created)
    #         sender = self.fake.random_element(room.members.all())

    #         Message.objects.create(
    #             sender=sender,
    #             room=room,
    #             content=self.fake.text(max_nb_chars=200),
    #             created_at=self.fake.date_time_between(
    #                 start_date="-30d",
    #                 end_date="now",
    #             ),
    #         )
