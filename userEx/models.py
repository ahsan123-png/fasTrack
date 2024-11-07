from django.db import models
from django.utils import timezone

# Client model (assuming it's already defined or a custom extension of User model)
class Client(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - {self.company_name}"
# Service Plan model to store available service plans
class ServicePlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.name
# Add-on services that can be linked to orders
class AddOnService(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey('Order', related_name='addon_services', on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.name} (${self.price})"

# The Order model
class Order(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual (10% discount)'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card (2% processing fee)'),
        ('ach_transfer', 'ACH Transfer'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    INVOICE_DELIVERY_CHOICES = [
        ('email', 'Email'),
        ('text', 'Text'),
    ]
    
    # Fields for Sales Order
    sales_order_number = models.CharField(max_length=20, unique=True, verbose_name="Sales Order No *")
    order_date = models.DateField(default=timezone.now, verbose_name="Date of Order *")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client ID *")
    # Fields for billing and payment
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    preferred_invoice_delivery = models.CharField(max_length=20, choices=INVOICE_DELIVERY_CHOICES, default='email')
    # Discounts and totals
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def generate_sales_order_number(self):
        # Generate a unique sales order number (custom logic, can be more complex)
        self.sales_order_number = f"SO-{timezone.now().strftime('%Y%m%d')}-{self.pk}"
        self.save()
    def calculate_total(self):
        # Base service plan price
        plan_price = self.service_plan.price
        # Add total for all add-on services linked to the order
        add_ons_total = sum([addon.price for addon in self.addon_services.all()])
        # Adjust for billing cycle (annual discount)
        if self.billing_cycle == 'annual':
            plan_price *= 0.9  # 10% discount for annual billing cycle
        # Add 2% processing fee if payment method is credit card
        if self.payment_method == 'credit_card':
            processing_fee = (plan_price + add_ons_total) * 0.02
        else:
            processing_fee = 0
        # Calculate final total
        self.total_amount = plan_price + add_ons_total + processing_fee - self.discount
        self.save()
    def __str__(self):
        return f"Order #{self.sales_order_number} for {self.client.user.username}"
# Model for invoices
class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default="unpaid")
    def generate_invoice_number(self):
        # Generate a unique invoice number
        self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{self.pk}"
        self.save()
    def __str__(self):
        return f"Invoice #{self.invoice_number} for Order #{self.order.sales_order_number}"
