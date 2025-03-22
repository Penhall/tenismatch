# /tenismatch/apps/tenis_admin/forms.py
from django import forms
from .models import Dataset, AIModel, ColumnMapping
from .services.model_catalog import ModelCatalog
from .services.model_selector import ModelSelector


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border rounded-md p-2',
                'placeholder': 'Nome do dataset'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-md p-2', 
                'rows': 4,
                'placeholder': 'Descrição do dataset'
            }),
            'file': forms.FileInput(attrs={
                'class': 'border p-2 w-full',
                'accept': '.csv,.json,.xlsx'
            })
        }

class ModelTrainingForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(
        queryset=Dataset.objects.filter(status='ready'),
        widget=forms.Select(attrs={'class': 'w-full border rounded-md p-2'})
    )
    
    model_type = forms.ChoiceField(
        choices=[(k, v['name']) for k, v in ModelCatalog.AVAILABLE_MODELS.items()],
        widget=forms.Select(attrs={'class': 'w-full border rounded-md p-2'})
    )
    
    class Meta:
        model = AIModel
        fields = ['name', 'version', 'description', 'dataset', 'model_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'version': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'description': forms.Textarea(attrs={
                'class': 'w-full border rounded-md p-2',
                'rows': 3
            })
        }
        
    def clean(self):
        cleaned_data = super().clean()
        dataset = cleaned_data.get('dataset')
        model_type = cleaned_data.get('model_type')
        
        if dataset and model_type:
            selector = ModelSelector(dataset.file.path)
            validation = selector.validate_model_selection(model_type)
            
            if not validation['valid']:
                raise forms.ValidationError(validation['message'])
                
        return cleaned_data

class ModelReviewForm(forms.Form):
    DECISION_CHOICES = [
        ('approve', 'Aprovar'),
        ('reject', 'Rejeitar')
    ]
    
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'h-4 w-4 text-purple-600'}),
        required=True,
        label="Decisão"
    )
    
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500',
            'rows': 4,
            'placeholder': 'Adicione observações sobre sua decisão...'
        }),
        required=False,
        label="Observações"
    )

class GenerateDataForm(forms.Form):
    n_samples = forms.IntegerField(
        label='Número de Amostras',
        min_value=10,
        max_value=10000,
        initial=100,
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
    
    save_dataset = forms.BooleanField(
        label='Salvar Dataset',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        help_text='Salvar o dataset no sistema para uso posterior'
    )
    
    dataset_name = forms.CharField(
        label='Nome do Dataset',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
        help_text='Nome do dataset (opcional, apenas se salvar)'
    )
    
    
class DatasetMappingForm(forms.ModelForm):
    """
    Formulário para mapeamento de colunas do dataset.
    """
    class Meta:
        model = Dataset
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded-md p-2'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded-md p-2', 'rows': 3}),
        }

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
    """
    Formulário para confirmação do mapeamento de colunas.
    """
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
