# /tenismatch/apps/admin/forms.py 
from django import forms
from .models import AIModel, Dataset, ModelMetrics

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ModelTrainingForm(forms.ModelForm):
    dataset = forms.ModelChoiceField(queryset=Dataset.objects.filter(is_processed=True))
    
    class Meta:
        model = AIModel
        fields = ['name', 'version', 'description', 'model_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ModelReviewForm(forms.ModelForm):
    APPROVAL_CHOICES = [
        ('approved', 'Aprovar'),
        ('rejected', 'Rejeitar'),
    ]
    decision = forms.ChoiceField(choices=APPROVAL_CHOICES)
    review_notes = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = AIModel
        fields = ['status']