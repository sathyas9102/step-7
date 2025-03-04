from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, CustomUser, DailyActivityReport

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'department', 'is_staff', 'is_admin', 'can_edit', 'can_delete', 'can_add_admin']
    search_fields = ['username', 'email']
    ordering = ['username']
    
    # Include email in fieldsets for both add and edit user views
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('email', 'department', 'can_edit', 'can_delete', 'can_add_admin')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'department', 'can_edit', 'can_delete', 'can_add_admin')}),
    )


admin.site.register(Department)
admin.site.register(CustomUser)
admin.site.register(DailyActivityReport)


from django.contrib import admin
from .models import Profile, Customer, Invoice, Payment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'email', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'contact', 'email')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('customer__name',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'due_date', 'is_paid')
    list_filter = ('is_paid',)
