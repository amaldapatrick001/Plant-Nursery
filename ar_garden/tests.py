from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import FieldImage, PlantType, UserPlantSelection
import os

class ARGardenTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test image
        self.image_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_field.jpg')
        with open(self.image_path, 'rb') as img:
            self.field = FieldImage.objects.create(
                user=self.user,
                image=SimpleUploadedFile('test_field.jpg', img.read()),
                width=10.0,
                length=10.0
            )
        
        # Create test plant type
        self.plant_type = PlantType.objects.create(
            name='Test Plant',
            icon=SimpleUploadedFile('test_icon.jpg', b''),
            model_3d=SimpleUploadedFile('test_model.glb', b''),
            min_spacing=1.0,
            height=2.0
        )

    def test_upload_field(self):
        response = self.client.post('/ar_garden/upload/', {
            'image': SimpleUploadedFile('new_field.jpg', b''),
            'width': 15.0,
            'length': 15.0
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(FieldImage.objects.filter(width=15.0).exists())

    def test_plant_placement(self):
        response = self.client.post(f'/ar_garden/select/{self.field.id}/', {
            'plant': self.plant_type.id,
            'x_position': 5.0,
            'y_position': 5.0,
            'rotation': 45.0
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserPlantSelection.objects.filter(
            field=self.field,
            x_position=5.0,
            y_position=5.0
        ).exists())

    def test_plant_spacing(self):
        # Create first plant
        UserPlantSelection.objects.create(
            user=self.user,
            field=self.field,
            plant=self.plant_type,
            x_position=5.0,
            y_position=5.0
        )
        
        # Try to place second plant too close
        response = self.client.get(f'/ar_garden/check-plant-distance/{self.field.id}/', {
            'x_position': 5.5,
            'y_position': 5.5,
            'plant_id': self.plant_type.id
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['valid'])

    def test_optimization(self):
        response = self.client.post(f'/ar_garden/optimize/{self.field.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserPlantSelection.objects.filter(
            field=self.field,
            is_ai_placed=True
        ).exists())
