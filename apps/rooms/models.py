from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Room(models.Model):
    """
    A chat room.

    This model manages chat rooms and keeps track of currently
    connected users in each room.

    Parameters
    ----------
    name : CharField
        Unique name of the chat room.
    members : ManyToManyField
        List of users currently connected in the room.
    created_at : DateTimeField
        Room creation date.

    Properties
    ----------
    online_count : int
        Number of connected users.

    Methods
    -------
    join(user)
        Adds a user to the list of connected users.
    leave(user)
        Removes a user from the list of connected users.
    """

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
        ]

    name: models.CharField = models.CharField(
        max_length=128, unique=True, verbose_name="Room Name", db_index=True
    )
    description: models.TextField = models.TextField(
        blank=True, null=True, verbose_name="Room Description"
    )
    author: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rooms"
    )

    members: models.ManyToManyField = models.ManyToManyField(
        User, through="RoomMember", related_name="joined_rooms"
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    @property
    def online_count(self):
        return self.members.filter(is_online=True).count()

    def join(self, user):
        if user not in self.members.all():
            user.set_online_status(True)
            self.members.add(user)
            self.save()
            return True
        return False

    def leave(self, user):
        if user in self.members.all():
            user.set_online_status(False)
            self.members.remove(user)
            self.save()
            return True
        return False

    def __str__(self):
        return f"Salon '{self.name}' | {self.online_count} utilisateur(s) en ligne"

    def __repr__(self):
        return f"Room(name={self.name!r}, online_count={self.online_count})"


class RoomMember(models.Model):
    """
    Modèle de liaison entre User et Room pour suivre la date d'adhésion

    Parameters
    ----------
    user : ForeignKey
        The user who is a member of the room.
    room : ForeignKey
        The room where the user is a member.
    joined_at : DateTimeField
        The date and time when the user joined the room.
    """

    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="room_memberships"
    )
    room: models.ForeignKey = models.ForeignKey(
        "Room", on_delete=models.CASCADE, related_name="memberships"
    )
    joined_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "room")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user.username} - {self.room.name}"

    def __repr__(self):
        return (
            f"RoomMember(user={self.user.username!r}, "
            f"room={self.room.name!r}, "
            f"joined_at={self.joined_at.strftime('%d/%m/%Y %H:%M')!r})"
        )
