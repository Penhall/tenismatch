# /tenismatch/apps/matching/urls.py 
from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    path('sneaker-form/', views.SneakerFormView.as_view(), name='sneaker_form'),
    path('matches/', views.MatchListView.as_view(), name='match_list'),
    path('match/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
]