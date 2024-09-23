from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CategoryForm

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new category to the database
            messages.success(request, 'Category added successfully!')  # Add success message
            return redirect('products:category_list')  # Redirect to the category list page
    else:
        form = CategoryForm()

    return render(request, 'products/add_category.html', {'form': form})


from .models import Category

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(status=True)

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




def add_product(request):
    status = True  # Initialize the status to False
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Product added successfully!')
                return redirect('products:aproduct_list')  # Ensure this matches the URL pattern
            except Exception as e:
                messages.error(request, f"An error occurred while uploading the file: {str(e)}")
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f"Non-field error: {error}")
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form, 'status': status})


from django.shortcuts import render, get_object_or_404
from .models import Product

def product_details(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'products/product_details.html', {'product': product})

from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Category
from .forms import ProductForm

def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Set the product status to True before saving
            product.status = True  # Adjust based on your model's field name
            form.save()  # Save the form data
            return redirect('products:aproduct_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/update_product.html', {
        'form': form,
        'product': product,
        'categories': categories
    })




from django.contrib import messages

def aproduct_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(status=True)  # Filter products with status=True

    # Apply additional filters based on request.GET parameters
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
        'products': products,
        'messages': messages.get_messages(request),  # Get messages
    }
    return render(request, 'products/aproduct_list.html', context)


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.status = False  # Soft delete
    product.save()
    messages.success(request, f"Product '{product.product_name}' deleted successfully.")
    return redirect('products:aproduct_list')




def update_stocks(request):
    products = Product.objects.order_by('product_name')

    if request.method == 'POST':
        for product in products:
            if f'update_{product.id}' in request.POST:
                stock_quantity = request.POST.get(f'stock_quantity_{product.id}')
                status = request.POST.get(f'status_{product.id}')  # Checkbox for status

                # Check if both fields are empty
                current_status = product.status
                if not stock_quantity and status is None:
                    messages.error(request, f"Please provide either a new stock quantity or change the status for '{product.product_name}' (current status: {'active' if current_status else 'inactive'}).")
                    continue

                updated = False

                # Process stock quantity if provided
                if stock_quantity:
                    try:
                        stock_quantity = int(stock_quantity)

                        # Allow decreasing stock, check that we don't go below zero
                        if stock_quantity < 0:
                            if product.stock_quantity + stock_quantity < 0:
                                messages.error(request, f"Cannot decrease stock for '{product.product_name}' below zero.")
                            else:
                                product.stock_quantity += stock_quantity
                                updated = True
                                messages.success(request, f"Stock decreased successfully for '{product.product_name}'.")
                        else:
                            if product.stock_quantity + stock_quantity > 1000:
                                messages.error(request, f"Cannot exceed maximum stock of 1000 for '{product.product_name}'.")
                            else:
                                product.stock_quantity += stock_quantity
                                updated = True
                                messages.success(request, f"Stock updated successfully for '{product.product_name}'.")

                    except ValueError:
                        messages.error(request, f"Invalid input for '{product.product_name}'. Please enter a valid integer for stock.")

                # Process status if provided (checkbox for active/inactive)
                if status is not None:
                    new_status = True if status == 'on' else False  # Determine new status
                    if product.status != new_status:  # Only update if there's a change
                        product.status = new_status
                        updated = True
                        if new_status:
                            messages.success(request, f"Status updated successfully for '{product.product_name}' to 'active'.")
                        else:
                            messages.success(request, f"Status updated successfully for '{product.product_name}' to 'inactive'.")

                # Save changes if any updates were made
                if updated:
                    product.save()
                else:
                    messages.error(request, f"No changes were made for '{product.product_name}'. Please ensure stock or status is updated.")

        return redirect('products:update_stocks')

    return render(request, 'products/update_stock.html', {'products': products})
