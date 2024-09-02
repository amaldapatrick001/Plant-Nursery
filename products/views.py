from django.shortcuts import render
from .models import Category, Product

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Apply filters based on request.GET parameters
    if request.GET.get('category'):
        products = products.filter(category_id=request.GET['category'])
    if request.GET.get('sunlight'):
        products = products.filter(sunlight_requirement=request.GET['sunlight'])
    if request.GET.get('water'):
        products = products.filter(water_need=request.GET['water'])
    if request.GET.get('climate'):
        products = products.filter(climate_compatibility=request.GET['climate'])
    if request.GET.get('price'):
        try:
            price_range = request.GET['price'].split('-')
            min_price, max_price = float(price_range[0]), float(price_range[1])
            products = products.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            pass  # Handle invalid price range input

    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'products/product_list.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('products:product_list')  # Ensure this matches the URL pattern
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f"Non-field error: {error}")
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_list')  # Ensure this matches the URL pattern
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f"Non-field error: {error}")
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/update_product.html', {'form': form})
