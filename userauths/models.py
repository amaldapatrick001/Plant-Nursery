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


class DeliveryPersonnel(models.Model):
    delivery_person_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)  # Link to User_Reg for personal details
    login = models.OneToOneField(Login, on_delete=models.CASCADE)  # Link to Login for authentication and status
    current_location = models.CharField(max_length=255, null=True, blank=True)  # GPS coordinates or address
    status = models.CharField(
        max_length=20, 
        choices=[('available', 'Available'), ('busy', 'Busy')],
        default='available'
    )  # Delivery personnel's availability status
    assigned_orders = models.IntegerField(default=0)  # Count of currently assigned orders
    date_time_joined = models.DateTimeField(auto_now_add=True)  # Date and time the delivery person was added

    def update_location(self, latitude, longitude):
        """Update the current GPS location of the delivery personnel."""
        self.current_location = f"{latitude}, {longitude}"
        self.save()

    def mark_as_busy(self):
        """Mark the delivery personnel's status as busy."""
        self.status = 'busy'
        self.save()

    def mark_as_available(self):
        """Mark the delivery personnel's status as available."""
        self.status = 'available'
        self.save()

    def assign_order(self):
        """Increment the assigned order count."""
        self.assigned_orders += 1
        self.mark_as_busy()
        self.save()

    def complete_order(self):
        """Decrement the assigned order count, mark as available if no more orders."""
        if self.assigned_orders > 0:
            self.assigned_orders -= 1
        if self.assigned_orders == 0:
            self.mark_as_available()
        self.save()

    def __str__(self):
        return f'Delivery Personnel: {self.user.first_name} {self.user.last_name}'

    @property
    def phone_number(self):
        """Fetch the phone number from the associated User_Reg model."""
        return self.user.phoneno


class Expert(models.Model):
    expert_id = models.AutoField(primary_key=True)  # Unique identifier for the expert
    user = models.OneToOneField(User_Reg, on_delete=models.CASCADE)  # Link to User_Reg for personal details
    login = models.OneToOneField(Login, on_delete=models.CASCADE)  # Link to Login for authentication and status
    expertise_area = models.CharField(max_length=255)  # Area of expertise (e.g., "Plant Diseases", "Soil Fertility")
    qualifications = models.TextField()  # List of qualifications, certifications, or degrees
    description = models.TextField(null=True, blank=True)  # Detailed description of the expert
    profile_picture = models.ImageField(upload_to='expert_profiles/', null=True, blank=True)  # Profile picture
    specialization_tags = models.CharField(max_length=255, null=True, blank=True)  # Tags for expertise areas
    availability_schedule = models.JSONField(null=True, blank=True)  # Availability schedule (stored as JSON)
    availability_status = models.CharField(
        max_length=20,
        choices=[('available', 'Available'), ('unavailable', 'Unavailable')],
        default='available'
    )  # Availability status for consultations
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Fee for consultations
    rating = models.FloatField(default=0.0)  # Average rating of the expert
    consultation_count = models.IntegerField(default=0)  # Number of consultations provided
    certifications = models.TextField(null=True, blank=True)  # Additional certifications
    total_reviews = models.IntegerField(default=0)  # Total number of reviews received
    blog_count = models.IntegerField(default=0)  # Number of blogs written by the expert
    contact_email = models.EmailField(null=True, blank=True)  # Contact email for direct queries
    contact_phone = models.CharField(max_length=15, null=True, blank=True)  # Alternative phone contact
    location = models.CharField(max_length=255, null=True, blank=True)  # Location of the expert
    languages = models.CharField(max_length=255, null=True, blank=True)  # Languages spoken by the expert
    date_time_joined = models.DateTimeField(auto_now_add=True)  # Date and time the expert was added

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

    def update_blog_count(self):
        """Increment the blog count for the expert."""
        self.blog_count += 1
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
