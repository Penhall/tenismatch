# /tenismatch/apps/profiles/forms.py
from django import forms
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class TennisPreferencesForm(forms.ModelForm):
    # Campos para marcas favoritas
    BRAND_CHOICES = [
        ('nike', 'Nike'),
        ('adidas', 'Adidas'),
        ('puma', 'Puma'),
        ('reebok', 'Reebok'),
        ('newbalance', 'New Balance'),
        ('converse', 'Converse'),
        ('vans', 'Vans'),
        ('asics', 'Asics')
    ]
    
    # Campos para estilos preferidos
    STYLE_CHOICES = [
        ('casual', 'Casual'),
        ('esportivo', 'Esportivo'),
        ('vintage', 'Vintage'),
        ('social', 'Social'),
        ('fashion', 'Fashion')
    ]
    
    # Campos para cores favoritas
    COLOR_CHOICES = [
        ('preto', 'Preto'),
        ('branco', 'Branco'),
        ('cinza', 'Cinza'),
        ('azul', 'Azul'),
        ('vermelho', 'Vermelho'),
        ('verde', 'Verde'),
        ('amarelo', 'Amarelo'),
        ('rosa', 'Rosa')
    ]
    
    # Campos para importância de características
    IMPORTANCE_CHOICES = [
        (1, 'Não é importante'),
        (2, 'Pouco importante'),
        (3, 'Neutro'),
        (4, 'Importante'),
        (5, 'Muito importante'),
    ]
    
    # Faixas etárias
    AGE_RANGE_CHOICES = [
        ('18-25', '18 a 25 anos'),
        ('26-35', '26 a 35 anos'),
        ('36-45', '36 a 45 anos'),
        ('46+', 'Mais de 46 anos'),
        ('all', 'Todas as idades')
    ]

    # Campos para seleção múltipla
    favorite_brands = forms.MultipleChoiceField(
        choices=BRAND_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    preferred_styles = forms.MultipleChoiceField(
        choices=STYLE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    favorite_colors = forms.MultipleChoiceField(
        choices=COLOR_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )
    
    # Campos para faixa de preço
    price_min = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    price_max = forms.IntegerField(
        min_value=0,
        max_value=5000,
        widget=forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    # Campos para importância
    brand_importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    style_importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    color_importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    price_importance = forms.ChoiceField(
        choices=IMPORTANCE_CHOICES,
        widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    # Outros campos
    max_distance = forms.IntegerField(
        min_value=1,
        max_value=500,
        widget=forms.NumberInput(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    age_range = forms.ChoiceField(
        choices=AGE_RANGE_CHOICES,
        widget=forms.Select(attrs={'class': 'shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline'}),
        required=False
    )
    
    show_only_premium = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox h-4 w-4 text-purple-600'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['shoe_size']  # Removidos 'preferred_brands' e 'style_preferences'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Inicializar valores do formulário a partir do modelo
        instance = kwargs.get('instance')
        if instance:
            # Logging para diagnóstico
            logger.debug(f"Inicializando formulário com dados do perfil: {instance.id}")
            logger.debug(f"Marcas preferidas: {instance.preferred_brands}")
            logger.debug(f"Preferências de estilo: {instance.style_preferences}")
            
            preferences = instance.style_preferences or {}
            
            # Converter valores do modelo para formato do formulário
            if instance.preferred_brands:
                self.initial['favorite_brands'] = instance.preferred_brands
                logger.debug(f"Inicializando favorite_brands com: {instance.preferred_brands}")
            
            if preferences.get('preferred_styles'):
                self.initial['preferred_styles'] = preferences.get('preferred_styles', [])
                logger.debug(f"Inicializando preferred_styles com: {preferences.get('preferred_styles')}")
                
            if preferences.get('favorite_colors'):
                self.initial['favorite_colors'] = preferences.get('favorite_colors', [])
                logger.debug(f"Inicializando favorite_colors com: {preferences.get('favorite_colors')}")
            
            if preferences.get('price_range'):
                price_range = preferences.get('price_range', {})
                self.initial['price_min'] = price_range.get('min')
                self.initial['price_max'] = price_range.get('max')
                logger.debug(f"Inicializando price_range com min: {price_range.get('min')}, max: {price_range.get('max')}")
            
            if preferences.get('importance'):
                importance = preferences.get('importance', {})
                self.initial['brand_importance'] = importance.get('brand')
                self.initial['style_importance'] = importance.get('style')
                self.initial['color_importance'] = importance.get('color')
                self.initial['price_importance'] = importance.get('price')
            
            if preferences.get('matching'):
                matching = preferences.get('matching', {})
                self.initial['max_distance'] = matching.get('max_distance')
                self.initial['age_range'] = matching.get('age_range')
                self.initial['show_only_premium'] = matching.get('show_only_premium', False)
    
    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Dados limpos no formulário: {cleaned_data}")
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Logging para diagnóstico
        logger.debug(f"Salvando formulário para o perfil: {instance.id}")
        logger.debug(f"Dados limpos: {self.cleaned_data}")
        
        # Garantir que preferred_brands e style_preferences não sejam None
        if instance.preferred_brands is None:
            instance.preferred_brands = []
            
        if instance.style_preferences is None:
            instance.style_preferences = {}
        
        # Salvar as preferências no formato correto do modelo
        preferences = instance.style_preferences
        
        # Marcas favoritas - salvar diretamente no campo próprio
        if self.cleaned_data.get('favorite_brands'):
            brands = self.cleaned_data.get('favorite_brands')
            instance.preferred_brands = list(brands)  # Converter para lista explicitamente
            logger.debug(f"Salvando preferred_brands: {instance.preferred_brands}")
        
        # Estilos preferidos
        if self.cleaned_data.get('preferred_styles'):
            preferences['preferred_styles'] = list(self.cleaned_data.get('preferred_styles'))
            logger.debug(f"Salvando preferred_styles: {preferences['preferred_styles']}")
        
        # Cores favoritas
        if self.cleaned_data.get('favorite_colors'):
            preferences['favorite_colors'] = list(self.cleaned_data.get('favorite_colors'))
            logger.debug(f"Salvando favorite_colors: {preferences['favorite_colors']}")
        
        # Faixa de preço
        price_min = self.cleaned_data.get('price_min')
        price_max = self.cleaned_data.get('price_max')
        if price_min is not None or price_max is not None:
            preferences['price_range'] = {
                'min': price_min,
                'max': price_max
            }
            logger.debug(f"Salvando price_range: {preferences['price_range']}")
        
        # Importância
        brand_imp = self.cleaned_data.get('brand_importance')
        style_imp = self.cleaned_data.get('style_importance')
        color_imp = self.cleaned_data.get('color_importance')
        price_imp = self.cleaned_data.get('price_importance')
        
        if any([brand_imp, style_imp, color_imp, price_imp]):
            preferences['importance'] = {
                'brand': brand_imp,
                'style': style_imp,
                'color': color_imp,
                'price': price_imp
            }
            logger.debug(f"Salvando importance: {preferences['importance']}")
        
        # Matching
        max_distance = self.cleaned_data.get('max_distance')
        age_range = self.cleaned_data.get('age_range')
        show_premium = self.cleaned_data.get('show_only_premium')
        
        if any([max_distance, age_range, show_premium]):
            preferences['matching'] = {
                'max_distance': max_distance,
                'age_range': age_range,
                'show_only_premium': show_premium or False
            }
            logger.debug(f"Salvando matching: {preferences['matching']}")
        
        # Atualizar o campo JSON
        instance.style_preferences = preferences
        logger.debug(f"Salvando style_preferences final: {instance.style_preferences}")
        
        if commit:
            instance.save()
            logger.debug(f"Perfil salvo com sucesso: {instance.id}")
        
        return instance

# Resto do código permanece inalterado
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