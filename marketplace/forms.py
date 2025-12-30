from django import forms
from .models import MarketplaceListing, Comment

class MarketplaceListingForm(forms.ModelForm):
    class Meta:
        model = MarketplaceListing
        fields = ['title', 'description', 'price', 'contact_info', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'contact_info': forms.TextInput(attrs={'placeholder': 'E.g. Phone: 555-0100 or Email: me@example.com'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ask a question or leave a comment...'}),
        }
        labels = {
            'body': '',
        }
