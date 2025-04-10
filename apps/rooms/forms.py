from django import forms
from apps.rooms.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "description"]
