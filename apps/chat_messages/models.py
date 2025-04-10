from textwrap import shorten

from django.db import models
from django.contrib.auth import get_user_model

from apps.rooms.models import Room


User = get_user_model()


class Message(models.Model):
    """
    A message sent in a chat room.

    This model is used to store the history of all messages
    sent in chat rooms.

    Parameters
    ----------
    sender : ForeignKey
        The user who sent the message.
    room : ForeignKey
        The room where the message was sent.
    content : CharField
        The message content.
    created_at : DateTimeField
        The date and time when the message was sent, added automatically.

    See Also
    --------
    Room : The associated chat room model.
    """

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
        ]

    # UserAction, user_action
    class Action(models.TextChoices):  # Actions des utilisateurs
        PRIVATE = "private", "Envoyer un message privé"
        PUBLIC = "public", "Envoyer un message public"
        JOIN = "join", "Rejoindre une salle"
        LEAVE = "leave", "Quitter une salle"
        SET_STATUS = "set_status", "Définir le statut"

    sender: models.ForeignKey = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="Sender",
    )
    recipients: models.ManyToManyField = models.ManyToManyField(
        to=User,
        related_name="received_messages",
        verbose_name="Recipients",
    )
    room: models.ForeignKey = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="messages"
    )
    content: models.CharField = models.CharField(max_length=512)
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, db_index=True
    )
    action: models.CharField = models.CharField(
        max_length=255,
        choices=Action.choices,
        default=Action.PUBLIC,
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"[{self.created_at.strftime('%d/%m/%Y %H:%M')}] "
            f"{self.sender.username} dans {self.room.name}: "
            f"{shorten(self.content, width=50, placeholder='...')}"
        )

    def __repr__(self):
        return (
            f"Message(sender={self.sender.username!r}, room={self.room.name!r}, "
            f"content={shorten(self.content, width=50, placeholder='...')!r})"
        )
