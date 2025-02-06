# urls.py

from django.urls import path
from core.views import about,contact, contact_list,index,adminindex # Importing the index view from the core app

urlpatterns = [
    path("", index, name="index"),
    path('adminindex/', adminindex, name='adminindex'), # Mapping the root URL to the index view
    path('about/', about, name='about'),  # Define URL for the about page
    path('contact/', contact, name='contact'),
    path('contact-list/', contact_list, name='contact_list'),
    
]