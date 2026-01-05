# catalog/forms.py

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']

        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'font' :'sans-sherif',
                    'placeholder': 'Share your thoughts on this component...',
                    # === ADD THIS STYLE ATTRIBUTE ===
                    'style': 'resize: none;', 
                    # ================================
                }
            ),
        }

        labels = {
            'rating': 'Your Rating',
            'review_text': 'Your Review',
        }