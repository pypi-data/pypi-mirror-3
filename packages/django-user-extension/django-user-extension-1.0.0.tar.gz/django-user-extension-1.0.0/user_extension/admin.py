from django.contrib.auth.admin import UserAdmin, UserChangeForm
from django.forms.models import ModelForm


class SubUserAdmin(UserAdmin):
    """
    A modified UserAdmin that does a switcheroo on the UserChangeForm so
    that admin validation will pass. Otherwise it will choke on any
    extra fields that don't exist on the User model.
    """
    form = ModelForm

    def __init__(self, model, admin_site):
        if self.form == ModelForm:
            self.form = UserChangeForm
        super(SubUserAdmin, self).__init__(model, admin_site)
