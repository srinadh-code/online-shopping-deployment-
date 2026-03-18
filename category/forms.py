from django import forms
from .models import Address
import re

class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name.replace(" ", "").isalpha():
            raise forms.ValidationError("Name must contain only letters")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if not phone.isdigit():
            raise forms.ValidationError("Phone must be numbers only")

        if len(phone) != 10:
            raise forms.ValidationError("Phone must be 10 digits")

        if phone[0] not in ["6","7","8","9"]:
            raise forms.ValidationError("Phone must start with 6-9")

        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode")

        if not pincode.isdigit():
            raise forms.ValidationError("Pincode must be numbers only")

        if len(pincode) != 6:
            raise forms.ValidationError("Pincode must be 6 digits")

        return pincode