"""
URL configuration for Enchanted_Eden project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('userauths/', include('userauths.urls')),
    path('products/', include('products.urls')), 
    path('purchase/', include('purchase.urls')),   
    path('delivery/', include('delivery.urls')), 
     path('blog/', include('blog.urls')),  
     path('qa_sessions/', include('qa_sessions.urls')),
    path('expert_QA_session/', include('expert_QA_session.urls')),  # Include expert sessions URLs
    # path('solar/', include('solar_forecast.urls')),  # Include solar forecast URLs
    # path('pdd/', include('pdd.urls')),  # Include the pdd URLs
    path('chatbot/', include('chatbot.urls')),  # Include the chatbot URLs
   path('plant_layout/', include('plant_layout.urls', namespace='plant_layout')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # For serving media files
