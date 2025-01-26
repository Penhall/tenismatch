# /tenismatch/apps/admin/urls.py 
from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    # Analyst URLs
    path('analyst/dashboard/', views.AnalystDashboardView.as_view(), name='analyst_dashboard'),
    path('analyst/dataset/upload/', views.DatasetUploadView.as_view(), name='dataset_upload'),
    path('analyst/model/create/', views.ModelCreationView.as_view(), name='model_create'),
    path('analyst/model/train/', views.ModelTrainingView.as_view(), name='model_training'),
    path('analyst/model/detail/<int:pk>/', views.ModelTrainingDetailView.as_view(), name='model_detail'),
    
    # Manager URLs
    path('manager/dashboard/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/model/review/<int:pk>/', views.ModelReviewView.as_view(), name='model_review'),
    path('manager/model/approve/<int:pk>/', views.ModelApprovalView.as_view(), name='model_approve'),
    path('manager/model/deploy/<int:pk>/', views.DeployModelView.as_view(), name='model_deploy'),
    path('manager/metrics/', views.MetricsView.as_view(), name='metrics'),
    path('manager/approvals/', views.ApprovalsView.as_view(), name='approvals'),
]