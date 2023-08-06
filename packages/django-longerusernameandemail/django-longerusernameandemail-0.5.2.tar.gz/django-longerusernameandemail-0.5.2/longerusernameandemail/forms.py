from django.utils.translation import ugettext as _
from django.core.validators import MaxLengthValidator
from django.contrib.auth import forms as auth_forms


from longerusernameandemail import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


def update_field_length(field, length):
    field.widget.attrs['maxlength'] = length
    field.max_length = length
    field.help_text = _("Required, %s characters or fewer. Only letters, "
                        "numbers, and characters such as @.+_- are "
                        "allowed." % length)

    # we need to find the MaxLengthValidator and change its
    # limit_value otherwise the auth forms will fail validation
    for v in field.validators:
        if isinstance(v, MaxLengthValidator):
            v.limit_value = length


class UserCreationForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        update_field_length(self.fields['username'], MAX_USERNAME_LENGTH())
        update_field_length(self.fields['email'], MAX_EMAIL_LENGTH())


class UserChangeForm(auth_forms.UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        update_field_length(self.fields['username'], MAX_USERNAME_LENGTH())
        update_field_length(self.fields['email'], MAX_EMAIL_LENGTH())


class AuthenticationForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        update_field_length(self.fields['username'], MAX_USERNAME_LENGTH())