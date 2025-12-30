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

#_________________________________________________________________________________________________________________________