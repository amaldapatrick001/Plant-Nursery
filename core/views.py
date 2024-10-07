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

def about(request):
    return render(request, 'core/about.html') 

from django.shortcuts import render, redirect
from .models import Contact
from django.contrib import messages

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('contactName')
        email = request.POST.get('contactEmail')
        subject = request.POST.get('contactSubject')
        message = request.POST.get('contactMessage')

        if name and email and subject and message:
            # Create and save the Contact model
            contact = Contact(name=name, email=email, subject=subject, message=message)
            contact.save()
            
            # Display success message
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
        else:
            messages.error(request, 'All fields are required.')
    return render(request, 'core/contact.html')
