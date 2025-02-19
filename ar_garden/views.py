from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import FieldImage, PlantType, UserPlantSelection
from .forms import FieldImageForm, PlantSelectionForm, PlantTypeForm
import numpy as np
from .optimization import optimize_plant_placement
from userauths.models import User_Reg

def check_auth(view_func):
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('userauths:login')
        return view_func(request, *args, **kwargs)
    return wrapper

@check_auth
def upload_field_image(request):
    if request.method == 'POST':
        form = FieldImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                field = form.save(commit=False)
                field.user = User_Reg.objects.get(uid=request.session['user_id'])
                field.save()
                messages.success(request, 'Field uploaded successfully!')
                return redirect('ar_garden:select_plants', field_id=field.id)
            except Exception as e:
                messages.error(request, f'Error saving field: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FieldImageForm()
    
    return render(request, 'ar_garden/upload_field.html', {
        'form': form,
        'title': 'Upload Field Image'
    })

@check_auth
def select_plant_positions(request, field_id):
    field = get_object_or_404(FieldImage, id=field_id, user__uid=request.session['user_id'])
    plants = PlantType.objects.all()
    user_plants = UserPlantSelection.objects.filter(field=field)

    if request.method == 'POST':
        form = PlantSelectionForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.user = User_Reg.objects.get(uid=request.session['user_id'])
            plant.field = field
            plant.save()
            return JsonResponse({'status': 'success'})
    else:
        form = PlantSelectionForm()

    context = {
        'field': field,
        'form': form,
        'plants': plants,
        'user_plants': user_plants,
    }
    return render(request, 'ar_garden/select_plants.html', context)

@check_auth
def view_3d_garden(request, field_id):
    field = get_object_or_404(FieldImage, id=field_id, user__uid=request.session['user_id'])
    plants = UserPlantSelection.objects.filter(field=field).select_related('plant')
    return render(request, 'ar_garden/view_3d.html', {
        'field': field,
        'plants': plants,
    })

@check_auth
def optimize_placement(request, field_id):
    field = get_object_or_404(FieldImage, id=field_id, user__uid=request.session['user_id'])
    plant_types = PlantType.objects.all()
    
    # Get optimal placements
    placements = optimize_plant_placement(field, list(plant_types))
    
    # Create new plant selections
    UserPlantSelection.objects.filter(field=field, is_ai_placed=True).delete()
    for x, y, plant_type_id, rotation in placements:
        user = User_Reg.objects.get(uid=request.session['user_id'])
        UserPlantSelection.objects.create(
            user=user,
            field=field,
            plant_id=plant_type_id,
            x_position=x,
            y_position=y,
            rotation=rotation,
            is_ai_placed=True
        )
    
    return JsonResponse({'status': 'success'})

@require_http_methods(["GET"])
@check_auth
def check_plant_distance(request, field_id):
    x = float(request.GET.get('x_position'))
    y = float(request.GET.get('y_position'))
    plant_id = int(request.GET.get('plant_id'))
    
    field = get_object_or_404(FieldImage, id=field_id, user__uid=request.session['user_id'])
    plant_type = get_object_or_404(PlantType, id=plant_id)
    
    existing_plants = UserPlantSelection.objects.filter(field=field)
    
    for existing_plant in existing_plants:
        distance = np.sqrt((x - existing_plant.x_position)**2 + 
                         (y - existing_plant.y_position)**2)
        min_spacing = max(plant_type.min_spacing, 
                         existing_plant.plant.min_spacing)
        
        if distance < min_spacing:
            return JsonResponse({
                'valid': False,
                'message': f'Too close to existing plant. Minimum spacing required: {min_spacing}m'
            })
    
    return JsonResponse({'valid': True})

@check_auth
def plant_list(request):
    plants = PlantType.objects.all().order_by('name')
    context = {
        'plants': plants,
        'title': 'Plant Types',
        'section': 'plant_list'
    }
    return render(request, 'ar_garden/plant_list.html', context)

@check_auth
def add_plant_type(request):
    if request.method == 'POST':
        form = PlantTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant type added successfully!')
            return redirect('ar_garden:plant_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PlantTypeForm()
    
    context = {
        'form': form,
        'title': 'Add New Plant Type',
        'section': 'add_plant_type'
    }
    return render(request, 'ar_garden/add_plant_type.html', context)