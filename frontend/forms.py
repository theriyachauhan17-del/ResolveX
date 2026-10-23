
from django import forms
from tickets.models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "title",
            "description",
            "priority",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter ticket title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe the issue",
                    "rows": 4,
                }
            ),
            "priority": forms.Select(
                attrs={"class": "form-select"}
            ),
        }
