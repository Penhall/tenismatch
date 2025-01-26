from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('signup/premium/', views.SignUpPremiumView.as_view(), name='signup_premium'),
    path('upgrade/', views.UpgradePremiumView.as_view(), name='upgrade_premium'),
]
