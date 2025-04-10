from django.http import HttpResponseNotAllowed
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from apps.rooms.models import Room
from apps.rooms.forms import RoomForm
from apps.chat_messages.models import Message
from apps.rooms.signals import room_join_success, room_leave_success


class RoomListView(LoginRequiredMixin, ListView):
    model = Room
    template_name = "rooms/list.html"
    context_object_name = "rooms"
    paginate_by = 9

    def get_queryset(self):
        queryset = Room.objects.all()

        # Recherche par nom ou description
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Tri des résultats
        sort_by = self.request.GET.get("sort", "recent")
        if sort_by == "recent":
            queryset = queryset.order_by("-created_at")
        elif sort_by == "popular":
            queryset = queryset.annotate(member_count=Count("members")).order_by(
                "-member_count"
            )
        elif sort_by == "name":
            queryset = queryset.order_by("name")

        return queryset


class RoomDetailView(SuccessMessageMixin, LoginRequiredMixin, DetailView):
    model = Room
    template_name = "rooms/detail.html"
    context_object_name = "room"
    success_message = "Room joined successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["room_messages"] = Message.objects.filter(room=self.object)

        context["online_users"] = self.object.members.filter(is_online=True)
        context["offline_users"] = self.object.members.filter(is_online=False)
        return context


class RoomCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = "rooms/partials/room_form_modal.html"
    success_message = "Room created successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        self.object.join(self.request.user)
        return reverse_lazy("rooms:detail", kwargs={"pk": self.object.pk})


class RoomUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = "rooms/partials/room_form_modal.html"
    context_object_name = "room"
    success_message = "Room updated successfully"
    success_url = reverse_lazy("rooms:list")


class RoomDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Room
    template_name = "rooms/partials/delete_room_modal.html"
    success_message = "Room deleted successfully"
    success_url = reverse_lazy("rooms:list")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.leave(request.user)
        return super().get(request, *args, **kwargs)


@require_GET
@login_required
def room_join(request, pk):
    """Vue fonction pour rejoindre une room"""
    room = get_object_or_404(Room, pk=pk)
    if room.join(request.user):
        room_join_success.send(
            sender=Room,
            instance=room,
            action=Message.Action.JOIN,
            user=request.user,
        )
        messages.success(request, f"Vous avez joint la salle {room.name}")
    else:
        messages.error(request, f"Vous êtes déjà dans la salle {room.name}")

    return redirect("rooms:detail", pk=pk)


@login_required
def room_leave(request, pk):
    """Vue fonction pour quitter une room"""
    room = get_object_or_404(Room, pk=pk)

    if request.method == "GET":
        context = {"room": room}
        return render(request, "rooms/partials/leave_room_modal.html", context)
    elif request.method == "POST" and room.leave(request.user):
        room_leave_success.send(
            sender=Room,
            instance=room,
            action=Message.Action.LEAVE,
            user=request.user,
        )
        messages.success(request, f"Vous avez quitté la salle {room.name}")
    else:
        messages.error(request, "Cette opération n'est pas autorisée")
        return HttpResponseNotAllowed(["GET", "POST"])  # 405 Method Not Allowed

    return redirect("rooms:list")
