from django.contrib import admin
from apps.rooms.models import Room, RoomMember


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "online_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    # filter_horizontal = ("members",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    fieldsets = (
        (
            "Room Information",
            {"fields": ("name", "description", "created_at", "updated_at")},
        ),
    )


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "joined_at")
    list_filter = ("room", "joined_at")
    search_fields = ("user__username", "room__name")
    readonly_fields = ("joined_at",)
    date_hierarchy = "joined_at"
