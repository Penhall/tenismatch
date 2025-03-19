# /tenismatch/core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import AboutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('apps.users.urls', 'users'), namespace='users')),
    path('profile/', include('apps.profiles.urls', namespace='profiles')),
    path('matching/', include('apps.matching.urls', namespace='matching')),
    path('tenis_admin/', include(('apps.tenis_admin.urls', 'tenis_admin'), namespace='tenis_admin')),
    path('sobre/', AboutView.as_view(), name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)