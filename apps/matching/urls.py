# /tenismatch/apps/matching/urls.py
from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    # URLs existentes
    path('sneaker-form/', views.SneakerFormView.as_view(), name='sneaker_form'),
    path('matches/', views.MatchListView.as_view(), name='match_list'),
    path('match/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('match/<int:match_id>/feedback/', views.MatchFeedbackView.as_view(), name='match_feedback'),
    
    # Novas URLs para funcionalidades adicionais
    path('match/<int:match_id>/<str:status>/', views.update_match_status, name='update_match_status'),
    path('daily/', views.DailyMatchesView.as_view(), name='daily_matches'),
    path('statistics/', views.MatchStatisticsView.as_view(), name='statistics'),
    path('api/matches/', views.api_get_matches, name='api_matches'),
    
]