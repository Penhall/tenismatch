# /tenismatch/apps/profiles/urls.py 
from django.urls import path
from .views import ProfileUpdateView, ProfileDetailView, PreferencesView, DashboardView, ProfileHistoryView

app_name = 'profiles'

urlpatterns = [
    path('', ProfileDetailView.as_view(), name='detail'),  # Caminho raiz para profile/
    path('editar/', ProfileUpdateView.as_view(), name='edit'),
    path('detalhe/', ProfileDetailView.as_view(), name='detail'),
    path('preferencias/', PreferencesView.as_view(), name='preferences'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('historico/', ProfileHistoryView.as_view(), name='history'),  # Adicionado rota para histórico
]