from django import forms
from .models import Dataset, AIModel, ColumnMapping  

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file', 'file_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-md p-2',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'file_type': forms.Select(attrs={'class': 'w-full border rounded-md p-2'}),
        }

class ModelTrainingForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.filter(is_processed=True),  # Alterado apenas esta linha
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
    
class DatasetMappingForm(forms.Form):
    def __init__(self, *args, columns=None, **kwargs):
        super().__init__(*args, **kwargs)
        if columns:
            column_choices = [(col, col) for col in columns]
            # Criar campos dinâmicos baseados nas colunas necessárias
            for required_col, label in ColumnMapping.required_columns.items():
                self.fields[f'mapping_{required_col}'] = forms.ChoiceField(
                    label=label,
                    choices=[('', '---')] + column_choices,
                    required=True,
                    widget=forms.Select(attrs={
                        'class': 'w-full border rounded-md p-2',
                        'data-required-column': required_col
                    })
                )

    def clean(self):
        cleaned_data = super().clean()
        # Verificar se não há mapeamentos duplicados
        mappings = [value for key, value in cleaned_data.items() if key.startswith('mapping_') and value]
        if len(mappings) != len(set(mappings)):
            raise forms.ValidationError("Cada coluna do dataset só pode ser mapeada uma vez")
        return cleaned_data

class MappingConfirmationForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label='Confirmo que o mapeamento está correto',
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'})
    )
    process_now = forms.BooleanField(
        required=False,
        initial=True,
        label='Processar dataset imediatamente após confirmação',
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'})
    )
