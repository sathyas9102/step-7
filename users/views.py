from datetime import date
from django.shortcuts import render, redirect 
import openpyxl   
from django.http import HttpResponse 
from django.contrib.auth import authenticate, login as auth_login 
from .forms import  DailyActivityReportForm
from .models import DailyActivityReport, CustomUser , Department
from django.contrib.auth.decorators import login_required , user_passes_test 
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User 
from django.shortcuts import render, redirect 
from django.contrib import messages 
import random
from django.conf import settings
from django.contrib.auth import get_user_model   
from django.core.exceptions import ObjectDoesNotExist 
from .models import Profile


def home(request):
    return render(request, 'users/login.html')

def create_user(request):
    return render(request, 'users/create_user.html' )

# Login Page 
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            # ✅ Retrieve user profile correctly
            user_profile = Profile.objects.filter(user=user).first()
            print(f"User Profile: {user_profile}")  # Debugging

            if user.is_superuser:
                print("Redirecting to admin dashboard")
                return redirect('users:admin_dashboard')

            elif user_profile:
                print(f"User Role: {user_profile.role}")  # Debugging

                if user_profile.role == 'media':
                    print("Redirecting to CRM Dashboard")  # Debugging
                    return redirect('crm_dashboard')  # ✅ Redirect to CRM Dashboard

                # Add more role-based conditions if needed

            messages.error(request, "Your role is not assigned. Contact the admin.")
            return redirect('users:login')

        else:
            messages.error(request, "Invalid username or password!")
            return render(request, 'users/login.html')

    return render(request, 'users/login.html')

@login_required
def export_excel_department(request, department_name):
    user = request.user

    if user.department.name.lower() != department_name.lower():
        messages.error(request, "You don't have access to this department's directory.")
        return redirect('users:daily_activity')

    daily_reports = DailyActivityReport.objects.filter(user__department__name=department_name)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename={department_name}_daily_reports.xlsx'

    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = f"{department_name} Reports"

    # Add headers
    headers = ["Date", "User", "Task", "News Count", "Total News Count"]
    worksheet.append(headers)

    # Populate data
    total_news_count = 0
    for report in daily_reports:
        total_news_count += report.news_count
        worksheet.append([report.date, report.user.username, report.task, report.news_count, total_news_count])

    workbook.save(response)
    return response

# Forgot password request page
def forgot_password(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        CustomUser = get_user_model()
        
        try:
            # Try to find the user by username first
            user = CustomUser.objects.get(username=username_or_email)
        except ObjectDoesNotExist:
            try:
                # If not found, try by email
                user = CustomUser.objects.get(email=username_or_email)
            except ObjectDoesNotExist:
                # If the user is not found by either username or email, show an error message
                messages.error(request, "User with this username or email does not exist.")
                return redirect('users:forgot_password')

        # Debug: Check the user's department
        print(f"User's department: {user.department}")  # Debug print statement

        # If department is None, it will print 'None'
        department_name = user.department.name if user.department else "No department"

        # Debug: Check what department is being set
        print(f"Department Name: {department_name}")  # Debug print statement

        # Generate a random verification code
        verification_code = random.randint(100000, 999999)

        # Prepare the email details
        admin_email = 'sathya9352@gmail.com'
        subject = f"Password Reset Request for {user.username}"
        message = f"""
        A password reset request has been made for the user {user.username}.
        Username: {user.username}
        Department: {department_name}  
        Verification Code: {verification_code}
        """

        # Send the email to admin
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

        # Store the verification code and user ID in the session
        request.session['verification_code'] = verification_code
        request.session['user_id'] = user.id

        messages.success(request, "A password reset request has been sent to the admin.")
        return redirect('users:verify_and_reset_password')

    return render(request, 'users/forgot_password.html')

# Admin view to verify the password reset request and reset the password
@login_required
def verify_and_reset_password(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')

        # Validate verification code
        if str(verification_code) == str(request.session.get('verification_code')):
            user_id = request.session.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            
            # Update password
            user.set_password(new_password)
            user.save()

            messages.success(request, f"Password reset successfully for {user.username}.")
            return redirect('users:login')
        else:
            messages.error(request, "Invalid verification code.")
            return redirect('users:verify_and_reset_password')

    return render(request, 'users/verify_password_reset.html')


# User Daily Activity Page
@login_required
def daily_activity(request, department_name):
    user = request.user
    
    # Safely check if the user belongs to the specified department
    if not user.department or user.department.name.lower() != department_name.lower():
        messages.error(request, "You don't have access to this department's directory.")
        return redirect('users:login') 

    today = date.today()
    daily_reports = DailyActivityReport.objects.filter(user__department__name=department_name, date=today)

    # Handle form submission
    if request.method == 'POST':
        form = DailyActivityReportForm(request.POST)
        if form.is_valid():
            activity_report = form.save(commit=False)
            activity_report.user = user
            activity_report.save()
            messages.success(request, f"Your daily activity report for {department_name} has been updated.")
            return redirect(f'users:daily_activity_{department_name.lower()}')

    else:
        form = DailyActivityReportForm()  # Empty form for GET request

    # Dynamically render the template based on the department name
    return render(request, f'users/daily_activity_{department_name.lower()}.html', {
        'form': form,
        'daily_reports': daily_reports,
        'department_name': department_name
    })


# Admin Dashboard (Add User/Admin page)
@login_required
def admin_dashboard(request):
    action = request.GET.get('action')
    departments = Department.objects.all()

    if request.method == 'POST':
        # Get the form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        department_name = request.POST.get('department')

        # Check if the department exists
        try:
            department = Department.objects.get(name=department_name)
        except Department.DoesNotExist:
            return render(request, 'users/admin_dashboard.html', {
                'action': action,
                'departments': departments,
                'error': f"Department {department_name} does not exist!"
            })

        # Check if the username already exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'users/admin_dashboard.html', {
                'action': action,
                'departments': departments,
                'error': f"Username {username} already exists!"
            })

        # Create the user based on the action
        if action == 'add_user':
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                department=department  # Assign the department here
            )
            user.save()

        elif action == 'add_admin':
            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                department=department  # Assign the department here
            )
            user.is_staff = True
            user.is_superuser = True

            # Assign custom permissions
            permissions = request.POST.getlist('permissions')
            user.can_edit = 'can_edit' in permissions
            user.can_delete = 'can_delete' in permissions
            user.can_add_admin = 'can_add_admin' in permissions
            user.save()

        # Redirect to the same page after the operation
        return redirect('users:admin_dashboard')

    return render(request, 'users/admin_dashboard.html', {
        'action': action,
        'departments': departments
    })

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Customer, Invoice, Payment

# 🔹 Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')

# 🔹 Dashboard (Redirects based on user role)
@login_required
def dashboard(request):
    if request.user.profile.role == 'media':
        return redirect('crm_dashboard')
    elif request.user.profile.role == 'it':
        return redirect('payment_dashboard')
    elif request.user.profile.role == 'accounts':
        return redirect('invoice_dashboard')
    return redirect('login')

# 🔹 CRM Dashboard
@login_required
def crm_dashboard(request):
    customers = Customer.objects.all()
    return render(request, 'crm_dashboard.html', {'customers': customers})

# 🔹 Add Customer (Media Team)
@login_required
def add_customer(request):
    if request.method == "POST":
        name = request.POST['name']
        contact = request.POST['contact']
        email = request.POST['email']
        Customer.objects.create(name=name, contact=contact, email=email, status='new')
        return redirect('crm_dashboard')
    return render(request, 'add_customer.html')

# 🔹 Update Status (Follow-ups)
@login_required
def update_status(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        status = request.POST['status']
        reason = request.POST.get('reason', '')
        if customer.status == 'new' and status != 'new':  # Cannot revert to 'new'
            customer.status = status
            customer.reason = reason
            customer.save()
    return redirect('crm_dashboard')

# 🔹 Invoice Dashboard
@login_required
def invoice_dashboard(request):
    invoices = Invoice.objects.all()
    return render(request, 'invoice_dashboard.html', {'invoices': invoices})

# 🔹 Request Invoice (Media Team)
@login_required
def request_invoice(request):
    if request.method == "POST":
        customer_id = request.POST['customer_id']
        amount = request.POST['amount']
        customer = Customer.objects.get(id=customer_id)
        Invoice.objects.create(customer=customer, amount=amount, status='pending')
        return redirect('invoice_dashboard')
    return render(request, 'request_invoice.html')

# 🔹 Approve Invoice (Accounts Team)
@login_required
def approve_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.status = 'done'
    invoice.save()
    return redirect('invoice_dashboard')

# 🔹 Payment Dashboard
@login_required
def payment_dashboard(request):
    payments = Payment.objects.all()
    return render(request, 'payment_dashboard.html', {'payments': payments})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def media_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # ✅ Redirect only Media Team members to CRM page
            if user.is_staff:  # Assuming Media Team members have `is_staff=True`
                return redirect("crm_database")  
            else:
                return redirect("default_dashboard")  # Redirect other users to a different page
                
        else:
            return render(request, "users/login.html", {"error": "Invalid credentials"})

    return render(request, "users/login.html")  # Render Login Page


@login_required
def crm_dashboard(request):
    return render(request, 'crm/dashboard.html')