from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class UserType(models.Model):
    utid = models.AutoField(primary_key=True)
    usertype = models.CharField(max_length=50)

    def __str__(self):
        return self.usertype

class User_Reg(models.Model):
    uid = models.AutoField(primary_key=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phoneno = models.CharField(max_length=15)
    date_time_reg = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)  # Automatically set status to True upon registration

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User_Reg, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    status = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)
    is_google_user = models.BooleanField(default=False)
    google_id = models.CharField(max_length=255, null=True, blank=True)

    def set_password(self, raw_password):
        """Hashes the password before storing it."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Checks if the provided password matches the stored hash."""
        return check_password(raw_password, self.password)
    
    def login(self):
        """Logs the user in by updating the login timestamp, status, and login count."""
        self.status = True  # Set status to True on login
        self.last_login = timezone.now()
        self.login_count += 1
        self.save()

    def logout(self):
        """Logs the user out by updating the logout timestamp and status."""
        self.status = False  # Set status to False on logout
        self.last_logout = timezone.now()
        self.save()

    def login_with_google(self, google_id):
        """Special login method for Google users."""
        self.is_google_user = True
        self.google_id = google_id
        self.login()

    def is_google_authenticated(self):
        return bool(self.is_google_user)

    def __str__(self):
        return f'Login entry for {self.email}'

    def get_email_field_name(self):
        return 'email'
    
    def get_username(self):
        return self.email
    
    @property
    def is_active(self):
        return True
    
    def has_usable_password(self):
        return True
    
    def get_session_auth_hash(self):
        return self.password

class Expert(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ]

    expert_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)
    login = models.OneToOneField(Login, on_delete=models.CASCADE)
    expertise_area = models.CharField(max_length=255)
    qualifications = models.TextField()
    description = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='expert_profiles/',
        null=True,
        blank=True
    )
    specialization_tags = models.CharField(max_length=255, null=True, blank=True)
    availability_schedule = models.JSONField(
        null=True, 
        blank=True,
        default=dict,
        help_text="""Format: {
            'monday': {'start': '09:00', 'end': '17:00', 'available': true},
            'tuesday': {'start': '09:00', 'end': '17:00', 'available': true},
            ...
        }"""
    )
    availability_status = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('unavailable', 'Unavailable')],
        default='available'
    )
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    consultation_count = models.IntegerField(default=0)
    certifications = models.TextField(null=True, blank=True)
    total_reviews = models.IntegerField(default=0)
    blog_count = models.IntegerField(default=0)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    languages = models.CharField(max_length=255, null=True, blank=True)
    date_time_joined = models.DateTimeField(auto_now_add=True)
    # New fields for live Q&A
    #chat_enabled = models.BooleanField(default=True)
    phone_enabled = models.BooleanField(default=True)  # Phone call support
    meet_link = models.URLField(null=True, blank=True)
    session_duration = models.IntegerField(default=10)  # Max 10 mins
    session_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Utility methods
    def update_availability(self, status):
        """Update the availability status of the expert."""
        self.availability_status = status
        self.save()

    def update_rating(self, new_rating):
        """Update the average rating of the expert based on a new rating."""
        total_rating = self.rating * self.consultation_count + new_rating
        self.consultation_count += 1
        self.rating = total_rating / self.consultation_count
        self.save()

    def get_published_blog_count(self):
        """Get count of published, non-deleted blogs by this expert"""
        return BlogPost.objects.filter(
            author=self.user,
            status='published',
            is_deleted=False
        ).count()

    def update_blog_count(self):
        """Update the blog_count field with actual count of published blogs"""
        self.blog_count = self.get_published_blog_count()
        self.save()

    def get_consultation_count(self):
        """Get the actual count of completed consultations"""
        return self.consultation_count

    def increment_consultation_count(self):
        """Increment the consultation count"""
        self.consultation_count += 1
        self.save()

    def increment_reviews(self):
        """Increment the total reviews count."""
        self.total_reviews += 1
        self.save()

    # Properties for fetching related data
    @property
    def phone_number(self):
        """Fetch the phone number from the associated User_Reg model."""
        return self.user.phoneno

    def __str__(self):
        return f'Expert: {self.user.first_name} {self.user.last_name} - {self.expertise_area}'

    def get_available_slots(self, date):
        """Get available time slots for a specific date"""
        from datetime import datetime, timedelta
        from django.utils import timezone

        # Convert date string to datetime
        if isinstance(date, str):
            check_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            check_date = date

        # Get day of week in lowercase
        day_of_week = check_date.strftime('%A').lower()

        # Check if day is available in schedule
        schedule = self.availability_schedule or {}
        day_schedule = schedule.get(day_of_week, {})
        
        if not day_schedule.get('available', False):
            return []

        start_time = datetime.strptime(day_schedule.get('start', '09:00'), '%H:%M').time()
        end_time = datetime.strptime(day_schedule.get('end', '17:00'), '%H:%M').time()

        # Combine date with times
        start_datetime = timezone.make_aware(datetime.combine(check_date, start_time))
        end_datetime = timezone.make_aware(datetime.combine(check_date, end_time))

        # If date is today, start from current time
        now = timezone.now()
        if check_date == now.date():
            start_datetime = max(start_datetime, now)

        # Generate slots
        slots = []
        current = start_datetime
        while current + timedelta(minutes=self.session_duration) <= end_datetime:
            # Check if slot is already booked
            from expert_QA_session.models import ExpertSession
            is_booked = ExpertSession.objects.filter(
                expert=self,
                session_date__lt=current + timedelta(minutes=self.session_duration),
                session_date__gt=current - timedelta(minutes=self.session_duration)
            ).exists()

            if not is_booked:
                slots.append(current.strftime('%H:%M'))
            
            current += timedelta(minutes=self.session_duration)

        return slots

    def set_availability(self, day, start_time, end_time, available=True):
        """Set availability for a specific day"""
        if not self.availability_schedule:
            self.availability_schedule = {}
        
        self.availability_schedule[day.lower()] = {
            'start': start_time,
            'end': end_time,
            'available': available
        }
        self.save()

    def set_weekly_schedule(self, schedule_dict):
        """Set the entire weekly schedule at once"""
        self.availability_schedule = {
            day.lower(): {
                'start': times.get('start', '09:00'),
                'end': times.get('end', '17:00'),
                'available': times.get('available', True)
            }
            for day, times in schedule_dict.items()
        }
        self.save()

class DeliveryPersonnel(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)
    vehicle_number = models.CharField(
        max_length=15, 
        help_text="Enter vehicle registration number (e.g., KL-05-AB-1234)",
        null=True,
        blank=True,
        unique=True
    )
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    area_of_delivery = models.CharField(
        max_length=255,
        default='Not Assigned',
        choices=[
            ('kottayam', 'Kottayam'),
            ('pathanamthitta', 'Pathanamthitta'),
            ('idukki', 'Idukki'),
            ('thodupuzha', 'Thodupuzha'),
            ('ernakulam', 'Ernakulam'),
        ]
    )
    date_time_joined = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('busy', 'Busy')],
        default='available'
    )
    assigned_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    profile_picture = models.ImageField(
        upload_to='delivery_personnel/profiles/',
        null=True,
        blank=True,
        help_text="Upload a profile picture (optional)"
    )
    daily_order_count = models.PositiveIntegerField(default=0)
    last_order_date = models.DateField(null=True, blank=True)
    max_daily_orders = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = "Delivery Personnel"
        verbose_name_plural = "Delivery Personnel"

    def __str__(self):
        return f"{self.user.first_name} - {self.vehicle_number} ({self.area_of_delivery})"

    def can_accept_order(self):
        """Check if delivery person can accept more orders today"""
        today = timezone.now().date()
        
        # Reset daily count if it's a new day
        if self.last_order_date != today:
            self.daily_order_count = 0
            self.last_order_date = today
            self.save()
        
        return (
            self.status == 'available' and 
            self.daily_order_count < self.max_daily_orders
        )

    def assign_order(self):
        """Increment order counts when assigned a new order"""
        today = timezone.now().date()
        
        if self.last_order_date != today:
            self.daily_order_count = 0
            self.last_order_date = today
        
        self.daily_order_count += 1
        self.assigned_orders += 1
        
        if self.daily_order_count >= self.max_daily_orders:
            self.status = 'busy'
        
        self.save()

    def complete_order(self):
        """Mark an order as completed"""
        self.completed_orders += 1
        
        # If we're below max daily orders, set status back to available
        if self.daily_order_count < self.max_daily_orders:
            self.status = 'available'
        
        self.save()

    def clean(self):
        """Validate vehicle number format"""
        from django.core.exceptions import ValidationError
        import re
        
        if self.vehicle_number:
            # Kerala vehicle number format: KL-\d{2}-[A-Z]{1,2}-\d{1,4}
            pattern = r'^KL-\d{2}-[A-Z]{1,2}-\d{1,4}$'
            if not re.match(pattern, self.vehicle_number):
                raise ValidationError({
                    'vehicle_number': 'Invalid vehicle number format. Use format: KL-05-AB-1234'
                })

    def save(self, *args, **kwargs):
        """Convert vehicle number to uppercase before saving"""
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.upper()
        super().save(*args, **kwargs)