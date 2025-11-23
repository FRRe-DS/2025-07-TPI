from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', include('portal_compras.urls')),
    path('login-error/', TemplateView.as_view(template_name='portal_compras/login_error.html'), name='login_error'),
    path('api/', include('portal_compras.urls')), 
]