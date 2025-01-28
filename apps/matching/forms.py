from django import forms
from .models import SneakerProfile
from .models import MatchFeedback

class SneakerProfileForm(forms.ModelForm):
    class Meta:
        model = SneakerProfile
        fields = ('brand', 'style', 'color', 'price_range', 'occasion')
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'style': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'color': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'price_range': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'occasion': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        }

class MatchFeedbackForm(forms.ModelForm):
    class Meta:
        model = MatchFeedback
        fields = ['rating', 'feedback_text']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'hidden peer',
            }),
            'feedback_text': forms.Textarea(attrs={
                'class': 'w-full border rounded-lg p-2',
                'rows': 3,
                'placeholder': 'Conte-nos mais sobre sua experiência...'
            })
        }