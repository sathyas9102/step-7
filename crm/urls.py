from django.urls import path
from . import views
from .views import customer_list, add_customer, download_dar

urlpatterns = [
    path('dashboard/', views.crm_dashboard, name='crm_dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path("download_dar/", download_dar, name="download_dar"),  
    path('log_call/<int:customer_id>/', views.log_call, name='log_call'),
    path('update_status/<int:customer_id>/<str:new_status>/', views.update_status, name='update_status'),

    # path('customers/move/<int:customer_id>/<str:status>/', views.move_customer, name='move_customer'),
    
    # Invoice Management
    path('invoice/', views.invoice_list, name='invoice_list'),
    path('invoice/request/', views.request_invoice, name='request_invoice'),
    path('invoice/approve/<int:invoice_id>/', views.approve_invoice, name='approve_invoice'),
    path('payments/', views.payment_list, name='payment_list'),
]
