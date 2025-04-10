from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.chat_messages.models import Message
from apps.shared.logging import get_logger

logger = get_logger("chat.signals")


@receiver(post_save, sender=Message)
def message_created_or_updated(sender, instance, created, **kwargs):
    try:
        logger.info(
            f"Message { 'created' if created else 'updated' } - Room: {instance.room.name}, "
            f"from: {instance.sender.username}"
        )
    except Exception as e:
        logger.error(f"Error updating room after message: {str(e)}")
        raise


@receiver(post_delete, sender=Message)
def message_deleted(sender, instance, **kwargs):
    try:
        logger.info(f"Message deleted - Room: {instance.room.name}")
    except Exception as e:
        logger.error(f"Error updating room after message deletion: {str(e)}")
        raise
