# /tenismatch/apps/profiles/urls.py 
from django.urls import path
from .views import ProfileEditView, ProfileDetailView, PreferencesView, DashboardView

app_name = 'profiles'

urlpatterns = [
    path('', ProfileDetailView.as_view(), name='detail'),  # Adicionado caminho raiz para profile/
    path('editar/', ProfileEditView.as_view(), name='edit'),
    path('detalhe/', ProfileDetailView.as_view(), name='detail'),
    path('preferencias/', PreferencesView.as_view(), name='preferences'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]