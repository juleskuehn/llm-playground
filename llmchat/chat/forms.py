"""
Defines the forms used in the chat app.
"""

from django import forms
from django.contrib.auth.models import User

from chat.models import Message, Document, UserSettings


class MessageForm(forms.ModelForm):
    """
    A form for creating a Message
    """

    class Meta:
        model = Message
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 1, "cols": 100, "class": "form-control"}
            ),
        }


class UploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class QueryForm(forms.Form):
    query = forms.CharField(
        label="Query",
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 1, "cols": 100, "class": "form-control"}),
    )


class QAForm(forms.Form):
    query = forms.CharField(
        label="Question",
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 1, "cols": 100, "class": "form-control"}),
    )


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ["system_prompt", "model_name", "temperature", "max_output_tokens", "debug"]
        widgets = {
            "system_prompt": forms.Textarea(
                attrs={"rows": 5, "cols": 100, "class": "form-control"}
            ),
            "model_name": forms.Select(attrs={"class": "form-select"}),
            # Slider to select temperature between 0 and 1
            "temperature": forms.NumberInput(
                attrs={
                    "type": "range",
                    "min": 0,
                    "max": 1,
                    "step": 0.01,
                    "class": "form-range",
                }
            ),
            # Manually enter max number of tokens
            "max_output_tokens": forms.NumberInput(
                attrs={
                    "type": "number",
                    "min": 128,
                    "max": 8192,
                    "step": 128,
                    "class": "form-control",
                }
            ),
            "debug": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
