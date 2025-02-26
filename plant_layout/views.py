from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from blog.views import ensure_user_logged_in
from plant_layout.forms import PlantForm
from .models import Plant, UserLayout
from .serializers import PlantSerializer, UserLayoutSerializer
from django.shortcuts import get_object_or_404
from userauths.models import Login, User_Reg
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.files.base import ContentFile
import base64
from django.views.decorators.http import require_http_methods
from .forms import UserLayoutForm

class PlantListView(APIView):
    def get(self, request):
        plants = Plant.objects.all().order_by('name')
        serializer = PlantSerializer(plants, many=True)
        return Response(serializer.data)

class UserLayoutView(APIView):
    def get(self, request, layout_id=None):
        user = self._get_user(request)
        if layout_id:
            layout = get_object_or_404(UserLayout, id=layout_id, user=user)
            serializer = UserLayoutSerializer(layout)
            return Response(serializer.data)
        else:
            layouts = UserLayout.objects.filter(user=user).order_by('-updated_at')
            serializer = UserLayoutSerializer(layouts, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = self._get_user(request)
        serializer = UserLayoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, layout_id):
        user = self._get_user(request)
        layout = get_object_or_404(UserLayout, id=layout_id, user=user)
        layout.delete()
        return Response({"message": "Layout deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

    def _get_user(self, request):
        if not request.session.get('user_id'):
            raise PermissionDenied("You must be logged in to access this feature.")
        user_login = Login.objects.get(login_id=request.session['user_id'])
        return User_Reg.objects.get(uid=user_login.uid.uid)
    



def add_plant(request):
    if not request.session.get('user_id'):
        messages.error(request, 'You must be logged in to add plants.')
        return redirect('userauths:login')

    try:
        user_login = Login.objects.get(login_id=request.session['user_id'])
        user = User_Reg.objects.get(uid=user_login.uid.uid)
        
        if request.method == 'POST':
            form = PlantForm(request.POST, request.FILES)
            if form.is_valid():
                plant = form.save()
                messages.success(request, 'Plant added successfully!')
                return redirect('plant_layout:plant_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = PlantForm()
        
        return render(request, 'add_plant.html', {'form': form, 'is_logged_in': True})
        
    except Exception as e:
        print(f"Add plant error: {str(e)}")  # Debug print
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'add_plant.html', {'form': PlantForm()})

def plant_layout(request):
    """Render the main plant layout page"""
    if not request.session.get('user_id'):
        return redirect('userauths:login')
    
    plants = Plant.objects.all().order_by('name')
    user_layouts = UserLayout.objects.filter(
        user__login__login_id=request.session['user_id']
    ).order_by('-updated_at')
    
    context = {
        'plants': plants,
        'user_layouts': user_layouts,
    }
    return render(request, 'plant_layout.html', context)

# plant_layout/views.py
from django.http import JsonResponse
from .models import UserLayout
def get_layout(request, layout_id):
    """API endpoint to get a specific layout"""
    print(f"Fetching layout with ID: {layout_id}")  # Debug print
    if not request.session.get('user_id'):
        print("User not authenticated")  # Debug print
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        print(f"Session user_id: {request.session['user_id']}")  # Debug print
        layout = UserLayout.objects.get(
            id=layout_id,
            user__login__login_id=request.session['user_id']
        )
        print(f"Layout found: {layout}")  # Debug print
        
        # Prepare the response data
        response_data = {
            'id': layout.id,
            'name': layout.layout_name,
            'plot_width': layout.plot_width,
            'plot_length': layout.plot_length,
            'plant_positions': layout.plant_positions,
            'plot_image': layout.plot_image.url if layout.plot_image else None,
        }
        
        return JsonResponse(response_data)
    except UserLayout.DoesNotExist:
        print(f"Layout with ID {layout_id} not found")  # Debug print
        return JsonResponse({'error': 'Layout not found'}, status=404)
    except Exception as e:
        print(f"Error fetching layout: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)
@require_http_methods(["POST"])
def save_layout(request):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = User_Reg.objects.get(login__login_id=request.session['user_id'])
        
        layout_data = {
            'user': user,
            'layout_name': request.POST.get('layout_name'),
            'plot_width': float(request.POST.get('plot_width')),
            'plot_length': float(request.POST.get('plot_length')),
            'background_type': request.POST.get('background_type', 'image'),
            'background_color': request.POST.get('background_color', '#FFFFFF'),
            'plant_positions': json.loads(request.POST.get('plant_positions', '{}')),
        }
        
        # Handle image if present
        if 'plot_image' in request.FILES and layout_data['background_type'] == 'image':
            layout_data['plot_image'] = request.FILES['plot_image']
        
        layout = UserLayout.objects.create(**layout_data)
        
        return JsonResponse({
            'id': layout.id,
            'message': 'Layout saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["POST"])
def update_layout(request, layout_id):
    """API endpoint to update plant positions in a layout"""
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        layout = UserLayout.objects.get(
            id=layout_id,
            user__login__login_id=request.session['user_id']
        )
        
        data = json.loads(request.body)
        layout.plant_positions = data.get('plant_positions', {'plants': []})
        layout.save()
        
        return JsonResponse({
            'message': 'Layout updated successfully',
            'id': layout.id,
            'plant_positions': layout.plant_positions
        })
    except UserLayout.DoesNotExist:
        return JsonResponse({'error': 'Layout not found'}, status=404)
    except Exception as e:
        print(f"Error updating layout: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=400)

def delete_layout(request, layout_id):
    """API endpoint to delete a layout"""
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        layout = UserLayout.objects.get(
            id=layout_id,
            user__login__login_id=request.session['user_id']
        )
        layout.delete()
        return JsonResponse({'message': 'Layout deleted successfully'})
    except UserLayout.DoesNotExist:
        return JsonResponse({'error': 'Layout not found'}, status=404)

def plant_list(request):
    """API endpoint to get list of plants"""
    plants = Plant.objects.all().order_by('name')
    data = [{
        'id': plant.id,
        'name': plant.name,
        'image': plant.image.url,
        'min_spacing': plant.min_spacing_m,
        'max_spacing': plant.max_spacing_m,
    } for plant in plants]
    return JsonResponse(data, safe=False)

def get_all_layouts(request):
    """API endpoint to get all layouts for the current user"""
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # Get the user first
        user = User_Reg.objects.get(login__login_id=request.session['user_id'])
        
        # Get layouts for the current user
        layouts = UserLayout.objects.filter(user=user).order_by('-updated_at')
        
        # Debug print
        print(f"Found {layouts.count()} layouts for user {user.uid}")
        
        # Prepare the response data
        layouts_data = []
        for layout in layouts:
            layout_data = {
                'id': layout.id,
                'name': layout.layout_name,
                'plot_width': layout.plot_width,
                'plot_length': layout.plot_length,
                'created_at': layout.created_at.isoformat(),
                'updated_at': layout.updated_at.isoformat()
            }
            
            # Handle plot image URL
            if layout.plot_image:
                try:
                    layout_data['plot_image'] = layout.plot_image.url
                except Exception as e:
                    print(f"Error getting image URL: {e}")
                    layout_data['plot_image'] = None
            else:
                layout_data['plot_image'] = None
            
            layouts_data.append(layout_data)
        
        return JsonResponse(layouts_data, safe=False)
        
    except User_Reg.DoesNotExist:
        print("User not found")
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print(f"Error loading layouts: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


















from django.views.decorators.csrf import ensure_csrf_cookie
def ensure_user_logged_in(request):
    """Ensure the user is logged in; if not, redirect to login with an error message."""
    if 'user_id' not in request.session:
        messages.error(request, 'You must be logged in to proceed.')
        return False
    return True


@ensure_csrf_cookie
def upload_layout(request):
    if not ensure_user_logged_in(request):
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    if request.method == 'POST':
        form = UserLayoutForm(request.POST, request.FILES)
        if form.is_valid():
            layout = form.save(commit=False)
            user_login = Login.objects.get(login_id=request.session['user_id'])
            layout.user = user_login.uid
            layout.save()

            response_data = {
                'status': 'success',
                'layout_id': layout.id,
                'layout_details': {
                    'name': layout.layout_name,
                    'width': layout.plot_width,
                    'length': layout.plot_length,
                    'background_type': layout.background_type,
                    'background_color': layout.background_color,
                }
            }
            
            if layout.background_type == 'image' and layout.plot_image:
                response_data['layout_details']['image_url'] = layout.plot_image.url
                
            return JsonResponse(response_data)
        else:
            errors = {field: error[0] for field, error in form.errors.items()}
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
    else:
        form = UserLayoutForm()
        plants = Plant.objects.all().order_by('name')
        
        # Get user's previous layouts
        user_login = Login.objects.get(login_id=request.session['user_id'])
        previous_layouts = UserLayout.objects.filter(user=user_login.uid).order_by('-updated_at')
        
        return render(request, 'upload_layout.html', {
            'form': form,
            'plants': plants,
            'previous_layouts': previous_layouts
        })

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json

@require_http_methods(["POST"])
def save_plant_positions(request, layout_id):
    """API endpoint to update plant positions in a layout"""
    if not ensure_user_logged_in(request):
        return JsonResponse({'status': 'error', 'error': 'Not authenticated'}, status=401)
    
    try:
        # Get the layout for the current user
        user_login = Login.objects.get(login_id=request.session['user_id'])
        layout = get_object_or_404(UserLayout, id=layout_id, user=user_login.uid)
        
        # Parse the request data
        data = json.loads(request.body)
        plant_positions = data.get('plant_positions')
        
        # Validate plant_positions structure
        if not isinstance(plant_positions, list):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid plant positions data'
            }, status=400)
        
        # Update plant positions
        layout.plant_positions = {'plants': plant_positions}
        layout.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Layout updated successfully',
            'id': layout.id
        })
    except UserLayout.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Layout not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error saving plant positions: {str(e)}")  # Debug print
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_layout(request, layout_id):
    """Endpoint to get a specific layout with all its details"""
    if not ensure_user_logged_in(request):
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    try:
        user_login = Login.objects.get(login_id=request.session['user_id'])
        layout = get_object_or_404(UserLayout, id=layout_id, user=user_login.uid)
        
        response_data = {
            'layout_name': layout.layout_name,
            'plot_width': layout.plot_width,
            'plot_length': layout.plot_length,
            'background_type': layout.background_type,
            'background_color': layout.background_color,
            'plant_positions': layout.plant_positions,
            'plot_image': layout.plot_image.url if layout.plot_image else None,
            'status': 'success'
        }
        
        return JsonResponse(response_data)
    except UserLayout.DoesNotExist:
        return JsonResponse({'error': 'Layout not found', 'status': 'error'}, status=404)
    except Exception as e:
        print(f"Error in get_layout: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)