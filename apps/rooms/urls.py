from django.urls import path

from apps.rooms import views

app_name = "rooms"

urlpatterns = [
    path("", views.RoomListView.as_view(), name="list"),
    path("<int:pk>/", views.RoomDetailView.as_view(), name="detail"),
    path("create/", views.RoomCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.RoomUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.RoomDeleteView.as_view(), name="delete"),
    path("<int:pk>/join/", views.room_join, name="join"),
    path("<int:pk>/leave/", views.room_leave, name="leave"),
]
