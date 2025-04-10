from apps.rooms import consumers
from django.urls import path

websocket_urlpatterns = [
    path(
        "ws/rooms/<int:pk>/",
        consumers.RoomConsumer.as_asgi(),
        name="rooms_ws",
    ),
]
