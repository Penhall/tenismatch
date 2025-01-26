# /tenismatch/core/urls.py 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('matching/', include('apps.matching.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:landing'), name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)