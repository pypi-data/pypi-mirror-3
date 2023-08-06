from django import forms
from django.conf import settings

from invitable.models import Invitation

INVITABLE_DEFAULT_ACCOUNT_TYPES = {
    'admin': 'Admin',
    'team': 'Team Member',
    'client': 'Client'
}

INVITABLE_ACCOUNT_TYPES = getattr(settings,
                                  "INVITABLE_ACCOUNT_TYPES",
                                  INVITABLE_DEFAULT_ACCOUNT_TYPES)


class InvitableForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ("email", "account_type")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Invitation.objects.filter(email=email).count():
            raise forms.ValidationError("Invitation already sent")
        return email

    def clean_account_type(self):
        account_type = self.cleaned_data.get("account_type")

        if account_type not in INVITABLE_ACCOUNT_TYPES:
            raise forms.ValidationError("Account type not allowed")
        return account_type
