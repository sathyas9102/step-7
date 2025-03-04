from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models


# Department model
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)
    
# Custom User model
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Custom permissions
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_add_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

# Daily Activity Report model
class DailyActivityReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    task=models.CharField(max_length=255,default='No task assigned')
    news_count = models.IntegerField(default=0)
    insta_followers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.task}"


from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.db.models.signals import post_save

# User Roles
from django.conf import settings  # ✅ Import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Use AUTH_USER_MODEL
    role = models.CharField(max_length=50, choices=[('media', 'Media'), ('admin', 'Admin')], default='media')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role="media")  # Default role

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    
# CRM Database
class Customer(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('followup1', 'Follow-up 1'),
        ('followup2', 'Follow-up 2'),
        ('not_interested', 'Not Interested'),
    ]
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=50, default="9999999999")
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    reason = models.CharField(max_length=100, blank=True, null=True)  # WhatsApp, Call, etc.
    created_at = models.DateTimeField(auto_now_add=True)

# Invoice Database
class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('done', 'Done')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

# Payment Tracking
class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
