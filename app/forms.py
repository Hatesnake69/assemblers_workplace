from django import forms

from app.models import WbSupplyModel


class MyCustomForm(forms.ModelForm):
    class Meta:
        model = WbSupplyModel
        fields = [
            "wb_name",
            "wb_id",
        ]
        widgets = {
            "wb_name": forms.TextInput(),
        }
