from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'pdd'

urlpatterns = [
    path('upload/', views.detect_disease, name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 