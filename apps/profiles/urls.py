# /tenismatch/apps/profiles/urls.py 
from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('edit/', views.ProfileEditView.as_view(), name='edit'),
    path('detail/', views.ProfileDetailView.as_view(), name='detail'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
]