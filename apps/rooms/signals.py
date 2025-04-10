from datetime import datetime
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver, Signal
from apps.rooms.models import Room, RoomMember
from apps.shared.logging import get_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.chat_messages.models import Message

logger = get_logger("chat.signals")

# Définition du nouveau signal
room_join_success = Signal()
room_leave_success = Signal()


@receiver(post_save, sender=Room)
def room_created_or_updated(sender, instance, created, **kwargs):
    try:
        logger.info(f"Room { 'created' if created else 'updated' } - {instance.name}")
    except Exception as e:
        logger.error(f"Error initializing room: {str(e)}")
        raise


@receiver(post_delete, sender=Room)
def room_deleted(sender, instance, **kwargs):
    try:
        logger.info(f"Room deleted - {instance.name}")
    except Exception as e:
        logger.error(f"Error deleting room: {str(e)}")
        raise


@receiver(post_save, sender=RoomMember)
def room_member_created_or_updated(sender, instance, created, **kwargs):
    try:
        logger.info(
            f"Room member { 'created' if created else 'updated' } - Room: {instance.room.name}, "
            f"User: {instance.user.username}"
        )
    except Exception as e:
        logger.error(f"Error initializing room member: {str(e)}")
        raise


@receiver(post_delete, sender=RoomMember)
def room_member_deleted(sender, instance, **kwargs):
    try:
        logger.info(
            f"Room member deleted - Room: {instance.room.name}, "
            f"User: {instance.user.username}"
        )
    except Exception as e:
        logger.error(f"Error cleaning up room member: {str(e)}")
        raise


@receiver(m2m_changed, sender=Room.members.through)
def room_members_changed(sender, instance, action, pk_set, **kwargs):
    """
    Signal to track changes in the ManyToMany Room-User relationship
    """
    try:
        if action == "post_add" and pk_set:
            logger.info(
                f"Members joined the room '{instance.name}' - "
                f"IDs of users: {list(pk_set)}"
            )

        if action == "post_remove" and pk_set:
            logger.info(
                f"Members left the room '{instance.name}' - "
                f"IDs of users: {list(pk_set)}"
            )
    except Exception as e:
        logger.error(f"Error processing m2m_changed signal for Room: {str(e)}")


def _handle_room_event(instance, user, action, event_type, timestamp, content):
    """
    Fonction utilitaire pour gérer les événements de salle (join/leave)
    """
    try:
        logger.info(
            f"User {user.username} successfully {event_type} room {instance.name}"
        )

        # Envoi du message via channel layer
        channel_layer = get_channel_layer()
        room_group_name = f"room_{instance.pk}"

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": f"room_{event_type}",
                "sender": user.username,
                "content": content,
                "timestamp": timestamp,
                "action": action,
            },
        )

        # Création du message système
        if action in [Message.Action.JOIN, Message.Action.LEAVE]:
            message = Message.objects.create(
                room=instance,
                sender=user,
                content=content,
                action=action,
            )
            # Ajout des membres de la salle au message
            room_members = instance.members.exclude(pk=user.pk).all()
            message.recipients.set(room_members)
            message.save()

    except Exception as e:
        logger.error(f"Error handling room {event_type} event: {str(e)}")


@receiver(room_join_success)
def handle_room_join_success(sender, instance, action, user, **kwargs):
    room_member = RoomMember.objects.get(user=user, room=instance)
    joined_at = room_member.joined_at.isoformat(timespec="seconds")
    content = (
        f"{user.get_display_name()} a rejoint la salle {instance.name} à {joined_at}"
    )
    _handle_room_event(instance, user, action, "join", joined_at, content)


@receiver(room_leave_success)
def handle_room_leave_success(sender, instance, action, user, **kwargs):
    left_at = datetime.now().isoformat(timespec="seconds")
    content = f"{user.get_display_name()} a quitté la salle {instance.name} à {left_at}"
    _handle_room_event(instance, user, action, "leave", left_at, content)
