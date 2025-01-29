# /tenismatch/apps/tenis_admin/forms.py 
from django import forms
from .models import AIModel, Dataset

class DatasetUploadForm(forms.ModelForm):
    file_type = forms.ChoiceField(
        choices=Dataset.FILE_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'w-full border rounded-md p-2'})
    )

    class Meta:
        model = Dataset
        fields = ['name', 'file', 'file_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'file': forms.FileInput(attrs={'class': 'w-full border rounded-md p-2'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_type = cleaned_data.get('file_type')
        
        if file and file_type:
            ext = file.name.split('.')[-1].lower()
            if file_type == 'xlsx' and ext == 'xls':
                ext = 'xlsx'  # Treat .xls as .xlsx
            if ext != file_type:
                self.add_error('file', f"O tipo de arquivo selecionado não corresponde à extensão do arquivo. Esperado: {file_type}, Recebido: {ext}")
        
        return cleaned_data

class ModelTrainingForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.filter(is_processed=True),
        widget=forms.Select(attrs={'class': 'w-full border rounded-md p-2'})
    )
    
    class Meta:
        model = AIModel
        fields = ['name', 'version', 'dataset']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'version': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'})
        }

class ModelReviewForm(forms.Form):
    decision = forms.ChoiceField(
        choices=[('approved', 'Aprovar'), ('rejected', 'Rejeitar')],
        widget=forms.RadioSelect(attrs={'class': 'mr-2'})
    )
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'w-full border rounded-md p-2'}),
        required=True
    )
    
class GenerateDataForm(forms.Form):
    n_samples = forms.IntegerField(
        min_value=100,
        max_value=10000,
        initial=1000,
        label='Número de Amostras',
        widget=forms.NumberInput(attrs={'class': 'w-full border rounded-md p-2'})
    )
