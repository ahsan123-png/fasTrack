from decimal import Decimal
from django.db import models
from django.utils import timezone
import random
class Client(models.Model):
    client_id = models.CharField(max_length=50, unique=True, verbose_name="Client ID *")  # Unique Client ID
    client_email  = models.EmailField(max_length=255, unique=True, verbose_name="Email Address *")  # Email field
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country  = models.CharField(max_length=15, blank=True, null=True)
    business_name  = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = str(random.randint(10000, 99999))  # Generate a 5-digit client_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_id} - {self.company_name}"
  # You can use `client_id` here instead of the `username`


# Service Plan model to store available service plans
class ServicePlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic Plan'),
        ('normal', 'Normal Plan'),
        ('professional', 'Professional Plan'),
        ('premium', 'Premium Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True, default='basic')  # Default set to 'basic'
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Plan price

    def __str__(self):
        return f"{self.get_name_display()} (${self.price})"

# Add-on services that can be linked to orders
class ServiceSelection(models.Model):
    order = models.ForeignKey('Order', related_name='service_selections', on_delete=models.CASCADE)
    service_plan = models.ForeignKey('ServicePlan', on_delete=models.CASCADE)
    
    multilingual_support_agents = models.PositiveIntegerField(default=0)
    after_hours_support_hours = models.PositiveIntegerField(default=0)
    technical_support_hours = models.PositiveIntegerField(default=0)
    fastrak_briefcase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    starter_prosiwo_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def calculate_total(self):
        multilingual_price = self.multilingual_support_agents * Decimal('200.00')  # $100 per multilingual agent
        after_hours_price = self.after_hours_support_hours * Decimal('10.00')  # $10 per hour for after-hours support
        technical_price = self.technical_support_hours * Decimal('10.00')  # $10 per hour for technical support
        total_price = (self.service_plan.price + multilingual_price + after_hours_price + 
                       technical_price + self.fastrak_briefcase_price + self.starter_prosiwo_price)
        return total_price

    def __str__(self):
        return f"Service Selection for Order #{self.order.sales_order_number}"


# Billing model for handling payment cycles and methods
class Order(models.Model):
    order_id = models.CharField(max_length=4, unique=True, verbose_name="Order ID", default=None)
    sales_order_number = models.CharField(max_length=20, unique=True, verbose_name="Sales Order No *")
    order_date = models.DateField(default=timezone.now, verbose_name="Date of Order *")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client ID *", default=None)

    def generate_order_id(self):
        """Generate a 4-digit unique order ID."""
        while True:
            order_id = str(random.randint(1000, 9999))
            if not Order.objects.filter(order_id=order_id).exists():
                return order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        if not self.sales_order_number:
                    self.sales_order_number = f"SO-{timezone.now().strftime('%Y%m%d')}-{self.pk or random.randint(1000, 9999)}"

        super(Order, self).save(*args, **kwargs)
    def __str__(self):
        return f"Order #{self.sales_order_number} for {self.client.client_id}"
class Billing(models.Model):
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
    
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="billing" ,default=None)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="billing" ,default=None)  # Link back to the order
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    preferred_invoice_delivery = models.CharField(max_length=20, choices=INVOICE_DELIVERY_CHOICES, default='email')
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE , default=None)

    def calculate_total(self, add_ons_total):
        """Calculate the total billing amount based on the service plan and add-ons."""
        plan_price = self.service_plan.price
        if self.billing_cycle == 'annual':
            plan_price *= 0.9  # 10% discount for annual billing cycle
        
        # Add 2% processing fee if payment method is credit card
        if self.payment_method == 'credit_card':
            processing_fee = (plan_price + add_ons_total) * 0.02
        else:
            processing_fee = 0
        
        # Calculate the final total amount
        self.total_amount = plan_price + add_ons_total + processing_fee - self.discount
        self.save()

    def __str__(self):
        return f"Billing info for client {self.client.client_id} with cycle {self.billing_cycle}"


# The Order model for sales orders
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
