# /tenismatch/apps/tenis_admin/urls.py
from django.urls import path
from . import views

app_name = 'tenis_admin'

urlpatterns = [
    # Analyst URLs
    path('analyst/dashboard/', 
        views.AnalystDashboardView.as_view(), 
        name='analyst_dashboard'),
    
    # Dataset Management
    path('analyst/dataset/upload/', 
        views.DatasetUploadView.as_view(), 
        name='dataset_upload'),
    path('analyst/dataset/generate/', 
        views.GenerateDataView.as_view(), 
        name='generate_data'),
        
    # Model Training
    path('analyst/model/create/', 
        views.ModelTrainingView.as_view(), 
        name='model_create'),
    path('analyst/model/detail/<int:pk>/', 
        views.ModelTrainingDetailView.as_view(), 
        name='model_detail'),
    
    # Manager URLs
    path('manager/dashboard/', 
        views.ManagerDashboardView.as_view(), 
        name='manager_dashboard'),
    
    # Model Review and Approval
    path('manager/model/review/<int:pk>/', 
        views.ModelReviewView.as_view(), 
        name='model_review'),
    path('manager/model/performance/<int:pk>/', 
        views.ModelPerformanceView.as_view(), 
        name='model_performance'),
    
    # Metrics and Analytics
    path('manager/metrics/', 
        views.MetricsDashboardView.as_view(), 
        name='metrics_dashboard'),
]