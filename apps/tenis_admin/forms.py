# /tenismatch/apps/tenis_admin/forms.py 
from django import forms
from .models import Dataset, AIModel

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-md p-2',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={'class': 'w-full border rounded-md p-2'})
        }

class ModelTrainingForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.filter(is_processed=True),
        widget=forms.Select(attrs={'class': 'w-full border rounded-md p-2'})
    )
    
    class Meta:
        model = AIModel
        fields = ['name', 'version', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'version': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-md p-2',
                'rows': 3
            })
        }

class ModelReviewForm(forms.Form):
    DECISIONS = [
        ('approved', 'Aprovar'),
        ('rejected', 'Rejeitar')
    ]
    
    decision = forms.ChoiceField(
        choices=DECISIONS,
        widget=forms.RadioSelect(attrs={'class': 'mr-2'})
    )
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full border rounded-md p-2',
            'rows': 3
        }),
        required=True
    )
    
class GenerateDataForm(forms.Form):
    n_samples = forms.IntegerField(
        label='Número de Amostras',
        min_value=100,
        max_value=10000,
        initial=1000,
        widget=forms.NumberInput(attrs={'class': 'w-full border rounded-md p-2'}),
        help_text='Quantidade de dados sintéticos a serem gerados'
    )
    
    include_labels = forms.BooleanField(
        label='Incluir Labels',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        help_text='Incluir labels para treinamento supervisionado'
    )