# /tenismatch/apps/tenis_admin/urls.py
from django.urls import path
from . import views
from .views import ModelMetricsAPIView

app_name = 'tenis_admin'

urlpatterns = [
    # Páginas Iniciais
    path('', views.ManagerDashboardView.as_view(), name='index'),
    
    # Área do Analista
    path('analyst/dashboard/', views.AnalystDashboardView.as_view(), name='analyst_dashboard'),
    path('analyst/dataset/upload/', views.DatasetUploadView.as_view(), name='dataset_upload'),
    path('analyst/dataset/<int:pk>/preview/', views.DatasetPreviewView.as_view(), name='dataset_preview'),
    path('analyst/dataset/<int:pk>/mapping/', views.DatasetMappingView.as_view(), name='dataset_mapping'),
    path('analyst/dataset/generate/', views.GenerateDataView.as_view(), name='generate_data'),
    path('analyst/model/create/', views.ModelTrainingView.as_view(), name='model_create'),
    path('analyst/model/<int:pk>/', views.ModelTrainingDetailView.as_view(), name='model_detail'),
    path('analyst/model/<int:model_id>/progress/', views.model_training_progress, name='model_progress'),
    
    # Área do Gerente
    path('manager/dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/metrics/', views.MetricsDashboardView.as_view(), name='metrics_dashboard'),
    path('manager/approvals/', views.ApprovalsView.as_view(), name='approvals'),
    path('manager/model/<int:pk>/review/', views.ModelReviewView.as_view(), name='model_review'),
    path('manager/model/<int:pk>/performance/', views.ModelPerformanceView.as_view(), name='model_performance'),
    
    # Endpoints de ação direta (novas rotas)
    path('model/<int:model_id>/review/', views.review_model, name='review_model'),
    path('model/<int:model_id>/deploy/', views.deploy_model, name='deploy_model'),
    
    # Endpoints de API
    path('api/model/<int:model_id>/metrics/', ModelMetricsAPIView.as_view(), name='model_metrics_api'),
]