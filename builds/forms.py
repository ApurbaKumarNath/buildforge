# builds/forms.py

#__________ akn

from django import forms
from .models import Build

# This is a ModelForm, a special type of form that is automatically
# created from a Django model. It's very convenient.
class BuildForm(forms.ModelForm):
    class Meta:
        # Tell the form which model to use.
        model = Build
        # Specify which fields from the model should be included in the form.
        # We don't include 'user' because we will set that automatically in the view.
        fields = ['name', 'description']
        
        # Optional: Add widgets to customize the form fields' appearance.
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., My Dream Gaming PC'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A short description of your build...'}),
        }