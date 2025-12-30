from django import forms
from .models import MarketplaceListing, Comment

class MarketplaceListingForm(forms.ModelForm):
    class Meta:
        model = MarketplaceListing
        fields = ['title', 'description', 'price', 'image', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
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
