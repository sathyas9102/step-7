# crm/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.timezone import now

class Customer(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('followup1', 'Follow-up 1'),
        ('followup2', 'Follow-up 2'),
        ('not_interested', 'Not Interested')
    ]
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)  # Follow-up details
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    # added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    prepared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prepared_invoices')

    def due_date(self):
        return self.issued_date + timezone.timedelta(days=30)
    
    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"

# Call Log Model
class CallLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Roohi Ma’am or Media Team
    call_time = models.DateTimeField(default=now)
    summary = models.TextField()  # Summary of what was discussed

    def __str__(self):
        return f"Call with {self.customer.name} by {self.caller.username}"

# DAR Database Model
class DAR(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_details = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DAR - {self.user.username} - {self.recorded_at}"
    
class DARReport(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    call_notes = models.TextField(blank=True, null=True)
    status_change = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)