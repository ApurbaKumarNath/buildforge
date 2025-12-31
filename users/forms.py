# users/forms.py

#_________________________________________________________________________________________________________________________ (akn)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# This form inherits from Django's built-in UserCreationForm.
# We are extending it to work with our CustomUser model.
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # We tell the form which model it's responsible for.
        model = CustomUser
        # We specify the fields to include in the form.
        # We can add more fields from our CustomUser model here later if we want!
        # For example, if you wanted email on the registration form, you'd add 'email'.
        fields = ('username', 'email')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['bio', 'avatar']


class PasswordToggleWidget(forms.PasswordInput):
    """
    A custom widget that allows rendering the value for a password field.
    This is necessary for our HTMX toggle to preserve the typed value.
    """
    def render(self, name, value, attrs=None, renderer=None):
        # We force the value to be rendered, overriding the default behavior.
        # The 'value' will be what the user has typed, passed back from our HTMX view.
        return super().render(name, value, attrs, renderer)
# ================================

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    # === ADD THIS __init__ METHOD ===
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tell the password fields to use our new custom widget.
        self.fields['password1'].widget = PasswordToggleWidget()
        self.fields['password2'].widget = PasswordToggleWidget()

#_________________________________________________________________________________________________________________________