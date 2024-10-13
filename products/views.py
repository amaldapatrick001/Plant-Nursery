from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # Make sure to import messages for notifications
from .models import Batch, Category, CultivationMethod, PlantCategory, Product, PlantType
from .forms import BatchForm, CategoryForm, CultivationMethodForm, PlantCategoryForm, ProductForm, PlantTypeForm

# View to list only active categories
def category_list(request):
    active_categories = Category.objects.filter(status=True)
    return render(request, 'products/category_list.html', {'categories': active_categories})

# View to list all categories (both active and inactive)
def category_update(request):
    categories = Category.objects.all().order_by('-status')  # Show active categories on top
    return render(request, 'products/category_update.html', {'categories': categories})
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages framework
from .forms import CategoryForm
from .models import Category  # Make sure to import the Category model

# View to add a new category (status set to active by default)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save(commit=False)
                category.status = True  # Ensure that all new categories are active
                category.save()
                messages.success(request, 'Category added successfully!')
                return redirect('products:category-list')
            except IntegrityError:
                messages.error(request, 'Category with this name already exists. Please choose a different name.')
    else:
        form = CategoryForm()

    return render(request, 'products/add_category.html', {'form': form})

# View to toggle category status (activate/deactivate)
def update_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.status = not category.status  # Toggle the status
    category.save()
    messages.success(request, 'Category status updated successfully!')
    return redirect('products:category-update')

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.description = request.POST.get('description', category.description)
        category.save()  # Save the changes
        messages.success(request, 'Category updated successfully!')
        return redirect('products:category-update')

    return render(request, 'products/edit_category.html', {'category': category})

# View to list only active plant types
def plant_type_list(request):
    active_plant_types = PlantType.objects.filter(status=True)
    return render(request, 'products/plant_type_list.html', {'plant_types': active_plant_types})
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PlantTypeForm
from .models import Category

# View to add a new plant type (status set to active by default)
def add_plant_type(request):
    categories = Category.objects.filter(is_plant=True)
    
    if request.method == 'POST':
        form = PlantTypeForm(request.POST)
        if form.is_valid():
            plant_type = form.save(commit=False)
            plant_type.status = True  # Ensure that all new plant types are active
            plant_type.save()
            messages.success(request, 'Plant type added successfully!')
            return redirect('products:plant-type-list')  # Redirect to plant type list after saving
        else:
            messages.error(request, 'There were errors in your form submission. Please check and try again.')  # Inform user of errors
    else:
        form = PlantTypeForm()
    
    return render(request, 'products/add_plant_type.html', {
        'form': form,
        'categories': categories  # Pass categories to the template
    })



def plant_type_update(request):
    plant_types = PlantType.objects.all().order_by('-status')  # Show active plant types on top
    return render(request, 'products/plant_type_update.html', {'plant_types': plant_types})

def update_plant_type_status(request, plant_type_id):
    plant_type = get_object_or_404(PlantType, id=plant_type_id)
    plant_type.status = not plant_type.status  # Toggle the status
    plant_type.save()
    messages.success(request, 'Plant type status updated successfully!')
    return redirect('products:plant-type-update')

def edit_plant_type(request, plant_type_id):
    plant_type = get_object_or_404(PlantType, id=plant_type_id)
    
    if request.method == 'POST':
        plant_type.description = request.POST.get('description', plant_type.description)
        plant_type.save()  # Save the changes
        messages.success(request, 'Plant type updated successfully!')
        return redirect('products:plant-type-update')

    return render(request, 'products/edit_plant_type.html', {'plant_type': plant_type})

from django.db import IntegrityError

def add_plant_category(request):
    if request.method == 'POST':
        form1 = PlantCategoryForm(request.POST)
        form2 = CultivationMethodForm(request.POST)

        if form1.is_valid():
            # Check for existing plant category with the same name
            name = form1.cleaned_data.get('name')
            if PlantCategory.objects.filter(name=name).exists():
                form1.add_error('name', 'A plant category with this name already exists.')
            else:
                plant_category = form1.save()  # Save PlantCategory
                if form2.is_valid():  # Check if CultivationMethodForm is valid
                    cultivation_method = form2.save(commit=False)  # Don't save yet
                    cultivation_method.plant_category = plant_category  # Link to the new category
                    cultivation_method.save()  # Now save CultivationMethod
                return redirect('products:add_plant_category')

    else:
        form1 = PlantCategoryForm()
        form2 = CultivationMethodForm()
    
    return render(request, 'products/add_plant_category.html', {'form1': form1, 'form2': form2})



from django.shortcuts import render
from .models import PlantCategory

def plant_category_list(request):
    # Fetch all Plant Categories with status=True
    plant_categories = PlantCategory.objects.filter(status=True)  
    return render(request, 'products/plant_category_list.html', {'plant_categories': plant_categories})


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import PlantCategory, CultivationMethod
def get_cultivation_methods(request, category_id):
    cultivation_methods = CultivationMethod.objects.filter(plant_category_id=category_id)

    if not cultivation_methods.exists():
        return HttpResponse('No Cultivation Methods found for this category.')

    response_html = "<h2>Cultivation Methods</h2><ul>"
    for method in cultivation_methods:
        response_html += f"""
        <li>
            <h4>{method.title}</h4>
            <p><strong>Description:</strong> {method.desc}</p>
            <p><strong>Steps:</strong> {method.steps}</p>
            <p><strong>Recommended Tools:</strong> {method.recommended_tools}</p>
            <p><strong>Pit Size:</strong> {method.pit_size_height}m x {method.pit_size_width}m</p>
            <p><strong>Distance Between Plants:</strong> {method.distance_between_plants}m</p>
            <p><strong>Watering Frequency:</strong> {method.watering_frequency}</p>
            <p><strong>Fertilization Guidelines:</strong> {method.fertilization_guidelines}</p>
            <p><strong>Common Issues:</strong> {method.common_issues}</p>
        </li>
        """
    response_html += "</ul>"

    return HttpResponse(response_html)


# View to update PlantCategory
def edit_plant_category(request, category_id):
    category = get_object_or_404(PlantCategory, id=category_id)
    if request.method == 'POST':
        form = PlantCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant category updated successfully!')
            return redirect('products:category-update')
    else:
        form = PlantCategoryForm(instance=category)
    
    return render(request, 'products/edit_plant_category.html', {'form': form, 'category': category})

# View to update CultivationMethod
def edit_cultivation_method(request, category_id):
    category = get_object_or_404(PlantCategory, id=category_id)
    try:
        cultivation_method = category.cultivation_methods.get()
    except CultivationMethod.DoesNotExist:
        cultivation_method = CultivationMethod(plant_category=category)
    
    if request.method == 'POST':
        form = CultivationMethodForm(request.POST, instance=cultivation_method)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cultivation method updated successfully!')
            return redirect('products:category-update')
    else:
        form = CultivationMethodForm(instance=cultivation_method)
    
    return render(request, 'products/edit_cultivation_method.html', {'form': form, 'category': category})









# AJAX View to Load Plant Types
def load_plant_types(request):
    plant_category_id = request.GET.get('plant_category')
    plant_types = PlantType.objects.filter(category_id=plant_category_id).order_by('name')
    return JsonResponse(list(plant_types.values('id', 'name')), safe=False)
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages  # Import messages framework
from .forms import ProductForm
from .models import PlantCategory, PlantType, Product  # Make sure to import the Product model

# View to handle adding a product
def add_product(request):
    plant_types = PlantType.objects.all()  # Fetch all plant types
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data['name']  # Assuming 'name' is the field for product name
            
            # Check for duplicate product name
            if Product.objects.filter(name=product_name).exists():
                messages.error(request, 'Product with this name already exists. Please choose a different name.')
            else:
                form.save()
                return redirect('products:product_list')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'plant_types': plant_types,
    }
    return render(request, 'products/add_product.html', context)

# AJAX view to fetch plant categories based on the selected plant type
from django.http import JsonResponse
from .models import PlantCategory

def get_plant_category(request):
    plant_type_id = request.GET.get('plant_type_id')
    if plant_type_id:
        try:
            # Get the plant categories related to the selected plant type
            categories = PlantCategory.objects.filter(plant_type_id=plant_type_id).values('id', 'name')
            return JsonResponse({'categories': list(categories)}, safe=False)
        except PlantCategory.DoesNotExist:
            return JsonResponse({'error': 'No plant categories found'}, status=404)
    else:
        return JsonResponse({'error': 'No plant type selected'}, status=400)

def product_list(request):
    # Fetch all active products (status=True)
    active_products = Product.objects.filter(status=True).select_related('plant_category', 'plant_type')
    
    context = {
        'active_products': active_products
    }
    
    return render(request, 'products/product_list.html', context)





def add_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch added successfully.")
            return redirect('products:batch_list')  # Redirect to batch list after saving
    else:
        form = BatchForm()

    return render(request, 'products/add_batch.html', {'form': form})

def batch_list_view(request):
    batches = Batch.objects.filter(status=True).select_related(
        'product__plant_category', 'product__plant_type'
    ).prefetch_related('product__plant_category__cultivation_methods')

    context = {'batches': batches}
    return render(request, 'products/batch_list.html', context)









from django.shortcuts import render
from django.db.models import Q
from .models import Batch

def cproduct_list(request):
    # Retrieve all GET parameters
    query = request.GET.get('q')
    price = request.GET.get('price')
    sunlight = request.GET.get('sunlight')
    water = request.GET.get('water')
    soil = request.GET.get('soil')
    growth_rate = request.GET.get('growth_rate')
    climate = request.GET.get('climate')
    best_time_to_plant = request.GET.get('best_time_to_plant')

    # Start with all active batches
    products = Batch.objects.filter(status=True).select_related('product', 'product__plant_category')

    # Search functionality: Product Name and Plant Category Name
    if query:
        products = products.filter(
            Q(product__name__icontains=query) |
            Q(product__plant_category__name__icontains=query)
        )

    # Filtering by Price Range
    if price:
        if price == '0-500':
            products = products.filter(price__gte=0, price__lte=500)
        elif price == '500-1000':
            products = products.filter(price__gte=500, price__lte=1000)
        elif price == '1000-1500':
            products = products.filter(price__gte=1000, price__lte=1500)
        elif price == 'above_1500':
            products = products.filter(price__gt=1500)

    # Filtering by Sunlight Requirement
    if sunlight:
        products = products.filter(product__plant_category__sunlight_requirement=sunlight)

    # Filtering by Water Need
    if water:
        products = products.filter(product__plant_category__water_requirement=water)

    # Filtering by Soil Type
    if soil:
        products = products.filter(product__plant_category__soil_type=soil)

    # Filtering by Growth Rate
    if growth_rate:
        products = products.filter(product__plant_category__growth_rate=growth_rate)

    # Filtering by Climate Compatibility
    if climate:
        products = products.filter(product__plant_category__climate_suitability=climate)

    # Filtering by Best Time to Plant (Season)
    if best_time_to_plant:
        products = products.filter(product__plant_category__best_time_to_plant=best_time_to_plant)

    # Optional: Implement pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page')
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    context = {
        'products': products_paginated,
        'query': query,
        'price': price,
        'sunlight': sunlight,
        'water': water,
        'soil': soil,
        'growth_rate': growth_rate,
        'climate': climate,
        'best_time_to_plant': best_time_to_plant,
    }
    return render(request, 'products/cproduct_list.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Product, Batch, CultivationMethod

def cproduct_details(request, product_id):
    # Fetch the product details
    product = get_object_or_404(Product, id=product_id)
    
    # Fetch related PlantCategory details (if available)
    plant_category = product.plant_category
    plant_category_data = {
        'name': plant_category.name if plant_category else 'N/A',
        'sunlight_requirement': plant_category.get_sunlight_requirement_display() if plant_category else 'N/A',
        'water_requirement': plant_category.get_water_requirement_display() if plant_category else 'N/A',
        'soil_type': plant_category.get_soil_type_display() if plant_category else 'N/A',
        'growth_rate': plant_category.get_growth_rate_display() if plant_category else 'N/A',
        'climate_suitability': plant_category.get_climate_suitability_display() if plant_category else 'N/A',
        'best_time_to_plant': plant_category.get_best_time_to_plant_display() if plant_category else 'N/A',
    } if plant_category else None
    
    # Fetch related Batch details (if available)
    batch = product.batches.first()  # Assuming you're showing details of the first batch
    batch_data = {
        'current_height': batch.current_height if batch else 'N/A',
        'price': batch.price if batch else 'N/A',
        'stock_quantity': batch.stock_quantity if batch else 'N/A',
        'discount': batch.discount if batch else 'N/A',
    } if batch else None
    
    # Fetch related CultivationMethod details (if available)
    cultivation_method = plant_category.cultivation_methods.first() if plant_category else None
    cultivation_method_data = {
        'title': cultivation_method.title if cultivation_method else 'N/A',
        'desc': cultivation_method.desc if cultivation_method else 'N/A',
        'steps': cultivation_method.steps if cultivation_method else 'N/A',
        'recommended_tools': cultivation_method.recommended_tools if cultivation_method else 'N/A',
        'pit_size': f"{cultivation_method.pit_size_height}m x {cultivation_method.pit_size_width}m" if cultivation_method else 'N/A',
        'distance_between_plants': cultivation_method.distance_between_plants if cultivation_method else 'N/A',
        'watering_frequency': cultivation_method.watering_frequency if cultivation_method else 'N/A',
        'fertilization_guidelines': cultivation_method.fertilization_guidelines if cultivation_method else 'N/A',
        'common_issues': cultivation_method.common_issues if cultivation_method else 'N/A',
    } if cultivation_method else None

    # Combine all data into context
    context = {
        'product': product,
        'plant_category': plant_category_data,
        'batch': batch_data,
        'cultivation_method': cultivation_method_data,
    }

    # Render the details page
    return render(request, 'products/cproduct_details.html', context)











from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Wishlist

# Add product to wishlist
@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"{product.name} has been added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    
    return redirect('product_detail', product_id=product_id)

# Remove product from wishlist
@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"{product.name} has been removed from your wishlist.")
    else:
        messages.info(request, f"{product.name} is not in your wishlist.")
    
    return redirect('wishlist')  # Redirect to wishlist page

# Display wishlist
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist/wishlist.html', context)

