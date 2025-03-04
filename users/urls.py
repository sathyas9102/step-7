from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('export_excel/<str:department_name>/', views.export_excel_department, name='export_excel_department'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_and_reset_password/', views.verify_and_reset_password, name='verify_and_reset_password'),
    path('daily_activity/<str:department_name>/', views.daily_activity, name='daily_activity'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-customer/', views.add_customer, name='add_customer'),
    path('request-invoice/<int:customer_id>/', views.request_invoice, name='request_invoice'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # CRM
    path('crm/', views.crm_dashboard, name='crm_dashboard'),
    path('crm/add_customer/', views.add_customer, name='add_customer'),
    path('crm/update_status/<int:customer_id>/', views.update_status, name='update_status'),

    # Invoice
    path('invoice/', views.invoice_dashboard, name='invoice_dashboard'),
    path('invoice/request/', views.request_invoice, name='request_invoice'),
    path('invoice/approve/<int:invoice_id>/', views.approve_invoice, name='approve_invoice'),
    
    path("media-login/", views.media_login, name="media_login"),
    path("crm/", views.crm_dashboard, name="crm_dashboard"), 

    # Payment
    path('payment/', views.payment_dashboard, name='payment_dashboard'),


]
