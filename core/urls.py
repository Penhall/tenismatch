# /tenismatch/core/urls.py 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from apps.users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('matching/', include('apps.matching.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:landing'), name='logout'),
    path('tenis_admin/', include(('apps.tenis_admin.urls', 'tenis_admin'), namespace='tenis_admin')),
    path('sobre/', views.about, name='about'),# nova url para o dashboard
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
