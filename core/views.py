<<<<<<< HEAD
# views.py

from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')  # Rendering the core/index.html template


def adminindex(request):
    return render(request, 'core/adminindex.html')
=======
from django.shortcuts import render

def index(request):
    return render(request, 'core/index.html')
>>>>>>> origin/main
