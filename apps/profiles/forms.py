from django import forms
from .models import UserProfile

class TennisPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['preferred_brands', 'style_preferences', 'shoe_size']
        widgets = {
            'preferred_brands': forms.SelectMultiple(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'style_preferences': forms.SelectMultiple(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'shoe_size': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline', 'step': '0.5'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'location', 'user_type', 'fashion_specialization', 'experience_years')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'user_type': forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'fashion_specialization': forms.TextInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
            'experience_years': forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline', 'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        fashion_specialization = cleaned_data.get('fashion_specialization')
        experience_years = cleaned_data.get('experience_years')

        if user_type == 'analyst':
            if not fashion_specialization:
                raise forms.ValidationError('Especialização em moda é obrigatória para analistas.')
            if experience_years is None or experience_years < 0:
                raise forms.ValidationError('Anos de experiência é obrigatório para analistas e deve ser maior ou igual a 0.')
