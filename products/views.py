from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # Make sure to import messages for notifications
from .models import Batch, Category, CultivationMethod, PlantCategory, Product, PlantType, Wishlist
from .forms import BatchForm, CategoryForm, CultivationMethodForm, PlantCategoryForm, ProductForm, PlantTypeForm
import numpy as np
from PIL import Image
# import tensorflow as tf
# from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
# from tensorflow.keras.preprocessing.image import img_to_array
import io
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from purchase.models import OrderItem, Order, Cart
from userauths.models import Login, User_Reg

# # Initialize the ML model (do this at module level)
# model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

# def extract_features(image):
#     # Preprocess image for ResNet50
#     img = Image.open(io.BytesIO(image.read())).convert('RGB')
#     img = img.resize((224, 224))
#     x = img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
    
#     # Extract features
#     features = model.predict(x)
#     return features.flatten()

# def cosine_similarity(a, b):
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# View to list only active categories
def category_list(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    
    active_categories = Category.objects.filter(status=True)
    return render(request, 'products/category_list.html', {'categories': active_categories})

# View to list all categories (both active and inactive)
def category_update(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    categories = Category.objects.all().order_by('-status')  # Show active categories on top
    return render(request, 'products/category_update.html', {'categories': categories})
from django.shortcuts import render, redirect
from django.contrib import messages  # Import messages framework
from .forms import CategoryForm
from .models import Category  # Make sure to import the Category model

# View to add a new category (status set to active by default)
def add_category(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    category = get_object_or_404(Category, id=category_id)
    category.status = not category.status  # Toggle the status
    category.save()
    messages.success(request, 'Category status updated successfully!')
    return redirect('products:category-update')

def edit_category(request, category_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.description = request.POST.get('description', category.description)
        category.save()  # Save the changes
        messages.success(request, 'Category updated successfully!')
        return redirect('products:category-update')

    return render(request, 'products/edit_category.html', {'category': category})

# View to list only active plant types
def plant_type_list(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    active_plant_types = PlantType.objects.filter(status=True)
    return render(request, 'products/plant_type_list.html', {'plant_types': active_plant_types})
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PlantTypeForm
from .models import Category

# View to add a new plant type (status set to active by default)
def add_plant_type(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    plant_types = PlantType.objects.all().order_by('-status')  # Show active plant types on top
    return render(request, 'products/plant_type_update.html', {'plant_types': plant_types})

def update_plant_type_status(request, plant_type_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    plant_type = get_object_or_404(PlantType, id=plant_type_id)
    plant_type.status = not plant_type.status  # Toggle the status
    plant_type.save()
    messages.success(request, 'Plant type status updated successfully!')
    return redirect('products:plant-type-update')

def edit_plant_type(request, plant_type_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    plant_type = get_object_or_404(PlantType, id=plant_type_id)
    
    if request.method == 'POST':
        plant_type.description = request.POST.get('description', plant_type.description)
        plant_type.save()  # Save the changes
        messages.success(request, 'Plant type updated successfully!')
        return redirect('products:plant-type-update')

    return render(request, 'products/edit_plant_type.html', {'plant_type': plant_type})

from django.db import IntegrityError

def add_plant_category(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    # Fetch all Plant Categories with status=True
    plant_categories = PlantCategory.objects.filter(status=True)  
    return render(request, 'products/plant_category_list.html', {'plant_categories': plant_categories})


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import PlantCategory, CultivationMethod
def get_cultivation_methods(request, category_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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

from django.http import JsonResponse
from .models import PlantCategory

def get_plant_category(request):
    
    plant_type_id = request.GET.get('plant_type_id')
    if plant_type_id:
        categories = PlantCategory.objects.filter(plant_type_id=plant_type_id).values('id', 'name')
        return JsonResponse({'categories': list(categories)}, safe=False)
    return JsonResponse({'error': 'No plant type selected'}, status=400)

def product_list(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    # Fetch all active products (status=True)
    active_products = Product.objects.filter(status=True).select_related('plant_category', 'plant_type')
    
    context = {
        'active_products': active_products
    }
    
    return render(request, 'products/product_list.html', context)





def add_batch(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

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
from django.db.models import Q, Avg, Count
from .models import Batch
from purchase.models import Review

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

    # Text Search functionality - moved before image search
    if query:
        products = products.filter(
            Q(product__name__icontains=query) |
            Q(product__description__icontains=query) |
            Q(product__plant_category__name__icontains=query) |
            Q(product__plant_type__name__icontains=query)
        ).distinct()

    # Handle image search
    similarity_scores = {}
    image_search_performed = False
    
    if request.method == 'POST' and request.FILES.get('search_image'):
        image_search_performed = True
        search_image = request.FILES['search_image']
        search_features = extract_features(search_image)

        # Get features for all products
        product_features = []
        for batch in products:
            if batch.product.image_1:
                try:
                    product_image = batch.product.image_1.open()
                    features = extract_features(product_image)
                    similarity = cosine_similarity(search_features, features)
                    similarity_scores[batch.id] = int(similarity * 100)
                    if similarity > 0.5:  # Threshold for similarity
                        product_features.append((batch.id, similarity))
                except Exception as e:
                    print(f"Error processing image for product {batch.id}: {e}")

        if product_features:
            product_features.sort(key=lambda x: x[1], reverse=True)
            top_batch_ids = [batch_id for batch_id, _ in product_features[:20]]
            products = products.filter(id__in=top_batch_ids)
        else:
            products = products.none()

    # Apply other filters
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

    # Annotate with ratings
    products = products.annotate(
        avg_rating=Avg('product__reviews__rating'),
        review_count=Count('product__reviews')  # Fixed: Changed to Count
    )

    # Pagination
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)

    # # Get recommendations if user is logged in
    # recommendations = []
    # if 'user_id' in request.session:
    #     user_id = request.session['user_id']
    #     print(f"User ID from session: {user_id}")  # Debug print
    #     try:
    #         recommendations = get_collaborative_recommendations(user_id)
    #         print(f"Got {len(recommendations)} recommendations")  # Debug print
    #     except Exception as e:
    #         print(f"Error getting recommendations: {e}")
    #         recommendations = []
    # else:
    #     print("No user_id in session")  # Debug print

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
        'image_search_performed': image_search_performed,
        'similarity_scores': similarity_scores,
        # 'recommendations': recommendations,
    }
    print("Context recommendations:", context['recommendations'])  # Debug print
    return render(request, 'products/cproduct_list.html', context)
from django.shortcuts import render, get_object_or_404
from purchase.models import Review
from userauths.models import User_Reg  # Adjust the import path as per your project structure
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
    batch = product.batches.first()
    batch_data = {
        'id': batch.id if batch else None,
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

    # Fetch reviews for the product
    reviews = Review.objects.filter(product=product).select_related('user')

    # Get user's name from session or User_Reg table
    user_fname = request.session.get('user_first_name')
    user_lname = request.session.get('user_last_name')

    if not user_fname or not user_lname:
        user = User_Reg.objects.filter(login__login_id=request.session.get('user_id')).first()
        user_fname = user.first_name if user else 'Guest'
        user_lname = user.last_name if user else ''

    # Combine all data into context
    context = {
    'product': product,
    'plant_category': plant_category_data,
    'batch': batch_data,
    'cultivation_method': cultivation_method_data,
    'reviews': reviews,
    'user_fname': user_fname,
    'user_lname': user_lname,
    'rating_range': range(1, 6),  # Passing the range for the stars
}


    # Render the details page
    return render(request, 'products/cproduct_details.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Wishlist, Batch
from userauths.models import Login

# View to handle displaying the wishlist
def wishlist_view(request):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to access the wishlist.')
        return redirect('userauths:login')

    # Fetch the user from the Login model based on session user_id
    user_login = get_object_or_404(Login, login_id=request.session['user_id'])
    
    # Fetch all wishlist items for the logged-in user
    wishlist_items = Wishlist.objects.filter(email=user_login)
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'products/wishlist.html', context)

# View to add an item to the wishlist
def add_to_wishlist(request, batch_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the wishlist.')
        return redirect('userauths:login')

    user_login = get_object_or_404(Login, login_id=request.session['user_id'])
    batch = get_object_or_404(Batch, pk=batch_id)
    
    # Check if the item is already in the wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(email=user_login, batch=batch)
    
    if created:
        messages.success(request, 'Item added to your wishlist!')
    else:
        messages.info(request, 'This item is already in your wishlist.')

    return redirect('products:wishlist')

# View to remove an item from the wishlist
def remove_from_wishlist(request, batch_id):
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to remove items from the wishlist.')
        return redirect('userauths:login')

    user_login = get_object_or_404(Login, login_id=request.session['user_id'])
    batch = get_object_or_404(Batch, pk=batch_id)
    
    # Try to delete the item from the wishlist
    Wishlist.objects.filter(email=user_login, batch=batch).delete()
    
    messages.success(request, 'Item removed from your wishlist.')
    return redirect('products:wishlist')
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from purchase.models import Cart, CartItem 
from purchase.models import Cart, CartItem
def wishlist_addtocart(request, batch_id):
    # Ensure the user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to add items to the cart.')
        return redirect('userauths:login')

    # Retrieve the current user and the batch (product) from the wishlist
    user_login = get_object_or_404(Login, login_id=request.session['user_id'])
    batch = get_object_or_404(Batch, pk=batch_id)
    
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user_id=request.session['user_id'], is_completed=False)

    # Check if the item is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, batch=batch)

    # If the item is already in the cart, update the quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{batch.product.name} quantity updated in your cart.")
    else:
        messages.success(request, f"{batch.product.name} added to your cart.")
    
    # Now remove the item from the wishlist
    Wishlist.objects.filter(email=user_login, batch=batch).delete()

    # Show a success message that the item was moved to the cart
    messages.success(request, f"{batch.product.name} has been moved to your cart from the wishlist.")

    # Redirect back to the wishlist page (or cart page, depending on the flow)
    return redirect('purchase:cart_detail')  # or 'purchase:cart_detail' if you want to redirect to the cart page directly

# def get_collaborative_recommendations(user_id):
#     """
#     Get personalized recommendations
#     """
#     print(f"Starting recommendations for user_id: {user_id}")
    
#     try:
#         # 1. First get available products with stock
#         available_products = Product.objects.filter(
#             status=True,
#             batches__status=True,  # Using correct relationship name
#             batches__stock_quantity__gt=0
#         ).distinct()
        
#         print(f"Found {available_products.count()} available products")  # Debug print

#         if not available_products.exists():
#             print("No available products found!")
#             return []

#         # 2. Get highly rated products
#         highly_rated = available_products.annotate(
#             avg_rating=Avg('reviews__rating')
#         ).filter(
#             avg_rating__isnull=False  # Has at least one review
#         ).order_by('-avg_rating')[:2]
        
#         print(f"Found {highly_rated.count()} highly rated products")  # Debug print

#         recommendations = []

#         # Add highly rated products
#         for product in highly_rated:
#             batch = Batch.objects.filter(  # Using Batch model directly
#                 product=product,
#                 status=True,
#                 stock_quantity__gt=0
#             ).first()
            
#             if batch:
#                 recommendations.append({
#                     'batch': batch,
#                     'reason': f'Highly Rated Product',
#                     'score': float(product.avg_rating or 3.0)
#                 })
#                 print(f"Added recommendation: {product.name}")  # Debug print

#         # 3. Get popular products (most ordered)
#         if len(recommendations) < 3:
#             popular = available_products.annotate(
#                 order_count=Count('batches__orderitem')  # Using correct relationship path
#             ).order_by('-order_count')[:2]
            
#             print(f"Found {popular.count()} popular products")  # Debug print

#             for product in popular:
#                 # Skip if already in recommendations
#                 if not any(r['batch'].product.id == product.id for r in recommendations):
#                     batch = Batch.objects.filter(  # Using Batch model directly
#                         product=product,
#                         status=True,
#                         stock_quantity__gt=0
#                     ).first()
                    
#                     if batch:
#                         recommendations.append({
#                             'batch': batch,
#                             'reason': 'Popular Choice',
#                             'score': 2.0
#                         })
#                         print(f"Added popular product: {product.name}")  # Debug print

#         # 4. If still need more, add random products
#         if len(recommendations) < 3:
#             remaining_needed = 3 - len(recommendations)
#             existing_ids = [r['batch'].product.id for r in recommendations]
            
#             random_products = available_products.exclude(
#                 id__in=existing_ids
#             ).order_by('?')[:remaining_needed]
            
#             print(f"Adding {random_products.count()} random products")  # Debug print

#             for product in random_products:
#                 batch = Batch.objects.filter(  # Using Batch model directly
#                     product=product,
#                     status=True,
#                     stock_quantity__gt=0
#                 ).first()

#                 if batch:
#                     recommendations.append({
#                         'batch': batch,
#                         'reason': 'You Might Like This',
#                         'score': 1.0
#                     })
#                     print(f"Added random product: {product.name}")  # Debug print

#         # Sort and return top 3
#         recommendations.sort(key=lambda x: x['score'], reverse=True)
#         final_recommendations = recommendations[:3]

#         print(f"Final recommendations count: {len(final_recommendations)}")
#         for rec in final_recommendations:
#             print(f"Final recommendation: {rec['batch'].product.name} - {rec['reason']}")

#         return final_recommendations

#     except Exception as e:
#         print(f"Error in get_collaborative_recommendations: {str(e)}")
#         import traceback
#         traceback.print_exc()  # Print full error traceback
#         return []

# def get_general_recommendations():
#     """
#     Get general recommendations (top 3 rated products)
#     """
#     try:
#         recommendations = []
        
#         # Get top rated products with stock
#         top_products = Product.objects.filter(
#             status=True,
#             batches__status=True,  # Using correct relationship name
#             batches__stock_quantity__gt=0
#         ).annotate(
#             avg_rating=Avg('reviews__rating'),
#             review_count=Count('reviews')
#         ).filter(
#             review_count__gt=0
#         ).order_by('-avg_rating')[:3]

#         for product in top_products:
#             batch = Batch.objects.filter(  # Using Batch model directly
#                 product=product,
#                 status=True,
#                 stock_quantity__gt=0
#             ).first()
#             if batch:
#                 recommendations.append({
#         'batch': batch,
#                     'reason': 'Top Rated Product',
#                     'score': float(product.avg_rating or 3.0)
#                 })

#         return recommendations

#     except Exception as e:
#         print(f"Error in get_general_recommendations: {str(e)}")
#         return []
