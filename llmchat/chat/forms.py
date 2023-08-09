"""
Defines the forms used in the chat app.
"""

from django import forms
from django.contrib.auth.models import User

from chat.models import Message


class MessageForm(forms.ModelForm):
    """
    A form for creating a Message
    """
    class Meta:
        model = Message
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 1, "cols": 100, "class": "form-control"}),
        }
