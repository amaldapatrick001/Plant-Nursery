# views.py

from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from userauths.models import DeliveryPersonnel, User_Reg, Expert
from purchase.models import Order
from django.contrib import messages
from django.http import JsonResponse
from .models import Contact
from django.core.mail import send_mail
from django.db.models import Avg, Sum

def index(request):
    try:
        # Get all active experts with related user data
        experts = Expert.objects.select_related('user', 'login').filter(
            user__status=True,
            availability_status='available'
        ).order_by('-rating')
        
        # Print for debugging
        print(f"Number of experts found: {experts.count()}")
        for expert in experts:
            print(f"Expert: {expert.user.first_name}, Status: {expert.user.status}")
        
        # Calculate statistics
        stats = {
            'total_experts': Expert.objects.count(),
            'active_experts': experts.count(),
            'avg_rating': experts.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_consultations': experts.aggregate(Sum('consultation_count'))['consultation_count__sum'] or 0
        }

        context = {
            'experts': experts,
            'stats': stats,
        }
        
        return render(request, 'core/index.html', context)
    except Exception as e:
        print(f"Error in index view: {str(e)}")  # For debugging
        return render(request, 'core/index.html', {
            'error_message': f'Error loading experts: {str(e)}',
            'experts': [],
            'stats': {
                'total_experts': 0,
                'active_experts': 0,
                'avg_rating': 0,
                'total_consultations': 0
            }
        })


def adminindex(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    # Count the total number of products
    product_count = Product.objects.count()
    user_count = User_Reg.objects.count()
    order_count = Order.objects.count()


    # Pass the counts to the template
    context = {
        'product_count': product_count,
        'user_count': user_count,
        'order_count':order_count,
    }

    # Pass context to the template
    return render(request, 'core/adminindex.html', context)

def about(request):
    return render(request, 'core/about.html') 

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

def contact_list(request):
    # Fetch contacts sorted by is_responded: False first, True last
    contacts = Contact.objects.all().order_by('is_responded')

    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        response_message = request.POST.get('response_message')

        # Fetch the contact entry to send a response
        contact = Contact.objects.get(id=contact_id)

        # Set the email subject as a response to the inquiry
        subject = f'Response to your inquiry: {contact.subject}'
        
        message = response_message
        from_email = 'your_email@example.com'  # Replace with your email

        # Send the email
        send_mail(subject, message, from_email, [contact.email])

        # Mark the contact as responded
        contact.is_responded = True
        contact.save()

        messages.success(request, 'Response sent successfully!')
        return redirect('contact_list')

    return render(request, 'core/contact_list.html', {'contacts': contacts})
