# views.py

from django.shortcuts import render
from products.models import Product
from userauths.models import User_Reg

def index(request):
    return render(request, 'core/index.html')  # Rendering the core/index.html template


def adminindex(request):
    # Count the total number of products
    product_count = Product.objects.count()
    user_count = User_Reg.objects.count()


    # Pass the counts to the template
    context = {
        'product_count': product_count,
        'user_count': user_count,
    }

    # Pass context to the template
    return render(request, 'core/adminindex.html', context)
