# /tenismatch/apps/users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Páginas principais
    path('', views.LandingView.as_view(), name='landing'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:landing'), name='logout'),
    
    # Cadastro
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/premium/', views.SignupPremiumView.as_view(), name='signup_premium'),
    
    # Perfil e dashboard
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Premium
    path('upgrade/', views.UpgradePremiumView.as_view(), name='upgrade_premium'),
    path('premium/', views.PremiumInfoView.as_view(), name='premium'),
    
    # Aprovação de usuários
    path('approve-analysts/', views.ApproveAnalystsView.as_view(), name='approve_analysts'),
    path('approval-waiting/', views.ApprovalWaitingView.as_view(), name='approval_waiting'),
]