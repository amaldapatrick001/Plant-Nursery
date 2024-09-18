<<<<<<< HEAD
# urls.py

from django.urls import path
from core.views import index,adminindex # Importing the index view from the core app

urlpatterns = [
    path("", index, name="index"),
    path('adminindex/', adminindex, name='adminindex'), # Mapping the root URL to the index view
=======
from django.urls import path

from core.views import index

app_name="bananas"
urlpatterns=[
    path("",index)
>>>>>>> origin/main
]