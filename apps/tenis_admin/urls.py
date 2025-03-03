# /tenismatch/apps/tenis_admin/urls.py
from django.urls import path
from . import views

app_name = 'tenis_admin'

urlpatterns = [
    # Analyst URLs
    path('analyst/dashboard/', views.AnalystDashboardView.as_view(), name='analyst_dashboard'),
    
    # Dataset Management
    path('analyst/dataset/generate/', views.GenerateDataView.as_view(), name='generate_data'),
    path('analyst/dataset/upload/', views.DatasetUploadView.as_view(), name='dataset_upload'),
    path('analyst/dataset/<int:pk>/preview/', views.DatasetPreviewView.as_view(), name='dataset_preview'),
    path('analyst/dataset/<int:pk>/mapping/', views.DatasetMappingView.as_view(), name='dataset_mapping'),
        
    # Model Training and Management
    path('analyst/model/create/', views.ModelTrainingView.as_view(), name='model_create'),
    path('analyst/model/<int:pk>/detail/', views.ModelTrainingDetailView.as_view(), name='model_detail'),
    path('model/<int:model_id>/progress/', views.model_training_progress, name='model_progress'),
    
    # Manager URLs
    path('manager/dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/model/<int:pk>/review/', views.ModelReviewView.as_view(), name='model_review'),
    path('manager/model/<int:pk>/performance/', views.ModelPerformanceView.as_view(), name='model_performance'),
    path('manager/metrics/', views.MetricsDashboardView.as_view(), name='metrics_dashboard'),
]
