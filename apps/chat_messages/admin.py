from django.contrib import admin
from apps.chat_messages.models import Message
from textwrap import shorten


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "room", "short_content", "created_at")
    list_filter = ("room", "sender", "created_at")
    search_fields = ("content", "sender__username", "room__name")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Message Information",
            {"fields": ("sender", "room", "content", "created_at")},
        ),
    )

    def short_content(self, obj):
        """Affiche une version tronquée du contenu du message"""
        return shorten(obj.content, width=50, placeholder="...")

    short_content.short_description = "Content"
