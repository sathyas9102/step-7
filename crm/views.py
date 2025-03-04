from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Customer, Invoice

# ✅ CRM Dashboard
@login_required
def crm_dashboard(request):
    return render(request, 'crm/dashboard.html')

# ✅ List All Customers
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'crm/customer_list.html', {'customers': customers})

# ✅ Add a New Customer
# @login_required
# def add_customer(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         details = request.POST.get("details")
#         Customer.objects.create(name=name, details=details, status="new")
#         messages.success(request, "Customer added successfully!")
#         return redirect("customer_list")
#     return render(request, 'crm/add_customer.html')

# ✅ Move Customer to Follow-Up or Not Interested
@login_required
def move_customer(request, customer_id, status):
    customer = get_object_or_404(Customer, id=customer_id)
    if status in ["followup1", "followup2", "not_interested"]:
        customer.status = status
        customer.save()
        messages.success(request, f"Customer moved to {status.replace('_', ' ').title()}.")
    return redirect("customer_list")

# ✅ List All Invoices
@login_required
def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'crm/invoice_list.html', {'invoices': invoices})

# ✅ Request an Invoice
@login_required
def request_invoice(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        amount = request.POST.get("amount")
        customer = get_object_or_404(Customer, id=customer_id)
        Invoice.objects.create(customer=customer, amount=amount, status="Pending")
        messages.success(request, "Invoice requested successfully!")
        return redirect("invoice_list")
    customers = Customer.objects.all()
    return render(request, 'crm/request_invoice.html', {'customers': customers})

# ✅ Approve Invoice (Accounts Team)
@login_required
def approve_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    invoice.status = "Approved"
    invoice.save()
    messages.success(request, "Invoice approved successfully!")
    return redirect("invoice_list")

# ✅ Payment List with Deadline Notification
@login_required
def payment_list(request):
    invoices = Invoice.objects.filter(status="Approved")
    return render(request, 'crm/payment_list.html', {'invoices': invoices})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Customer, CallLog, DAR
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import requests
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import CallLog

# ✅ Media Team: Add Customer
@login_required
def add_customer(request):
    if request.method == "POST":
        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST.get('email', '')
        address = request.POST['address']

        customer = Customer.objects.create(
            name=name, phone=phone, email=email, address=address, added_by=request.user
        )

        # Notify IT Team
        send_mail(
            "New Customer Added",
            f"A new customer {customer.name} has been added by {request.user.username}.",
            "noreply@crm.com",
            ["it-team@crm.com"],
        )

        # WhatsApp Notification (Using Twilio API)
        message = f"New customer added: {customer.name}, Contact: {customer.phone}"
        requests.post(
            "https://api.twilio.com/send-whatsapp-message",
            data={"message": message},
        )

        messages.success(request, "Customer added successfully!")
        return redirect("customer_list")

    return render(request, "crm/add_customer.html")

# ✅ Media Team: View Customers
@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by("-created_at")
    return render(request, "crm/customer_list.html", {"customers": customers})

# ✅ Change Customer Status
# @login_required
# def update_status(request, customer_id, new_status):
#     customer = Customer.objects.get(id=customer_id)

#     # Restrict status rollback
#     if customer.status == 'new' and new_status not in ['followup1', 'followup2', 'not_interested']:
#         messages.error(request, "Invalid status change!")
#         return redirect("customer_list")

#     customer.status = new_status
#     customer.save()
#     messages.success(request, "Customer status updated successfully!")
#     return redirect("customer_list")
@login_required
def update_status(request, customer_id, new_status):
    customer = get_object_or_404(Customer, id=customer_id)

    # Prevent moving back to "New"
    if customer.status == "new" and new_status != "followup1":
        return redirect('customer_list')

    if customer.status == "followup1" and new_status == "new":
        return redirect('customer_list')

    # Update status
    customer.status = new_status
    customer.save()

    # Save to DAR Report
    DARReport.objects.create(customer=customer, status_change=new_status, date=now())

    return redirect('customer_list')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, DARReport
from django.utils.timezone import now

@login_required
def log_call(request, customer_id):
    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":
        call_notes = request.POST.get("call_notes")
        # Save call details to DAR Report
        DARReport.objects.create(customer=customer, call_notes=call_notes, date=now())
        summary = request.POST['summary']
        CallLog.objects.create(customer=customer, caller=request.user, summary=summary)
        messages.success(request, "Call logged successfully!")
        return redirect("customer_list")

    return render(request, "crm/log_call.html", {"customer": customer})

# ✅ Auto-Move Data to DAR on Download

@login_required
def download_dar(request):
    user = request.user
    call_logs = CallLog.objects.filter(caller=user)

    report_content = "\n".join(
        [f"{log.call_time} - {log.customer.name}: {log.summary}" for log in call_logs]
    )

    # Create a response for file download
    response = HttpResponse(report_content, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="DAR_Report.txt"'
    
    return response 

import csv
from django.http import HttpResponse

def download_dar(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="dar_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Customer Name", "Phone", "Email", "Status Change", "Call Notes", "Date"])

    for report in DARReport.objects.all():
        writer.writerow([report.customer.name, report.customer.phone, report.customer.email, 
                         report.status_change, report.call_notes, report.date])

    return response
