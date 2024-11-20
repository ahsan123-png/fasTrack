from django.contrib.auth.models import User
from decimal import Decimal
from django.db import models
from django.utils import timezone
import random
from django.utils.text import slugify
# ================ models =================
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
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

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
class Document(models.Model):
    # user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    google_drive_file_id = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
#=========== Job application Models =================
# Main Job Application Model
class JobApplication(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(null=True, blank=True,default=None)
    phone = models.CharField(max_length=15,blank=True,null=True)
    address = models.TextField(null=True, blank=True, default=None)
    linkedin_profile = models.URLField(blank=True, null=True)
    terms_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)
    def __str__(self):
        return self.name
class PositionInformation(models.Model):
    FULL_TIME = 'Full Time'
    PART_TIME = 'Part Time'
    EMPLOYMENT_TYPE_CHOICES = [
        (FULL_TIME, 'Full Time'),
        (PART_TIME, 'Part Time')
    ]
    SHIFT_6AM_12PM = '6am - 12pm'
    SHIFT_12PM_6PM = '12pm - 6pm'
    SHIFT_6PM_12AM = '6pm - 12am'
    DAY_SHIFT = 'Day'
    NIGHT_SHIFT = 'Night'
    SHIFT_CHOICES = [
        (DAY_SHIFT, 'Day Shift'),
        (NIGHT_SHIFT, 'Night Shift'),
        (SHIFT_6AM_12PM, '6am - 12pm'),
        (SHIFT_12PM_6PM, '12pm - 6pm'),
        (SHIFT_6PM_12AM, '6pm - 12am')
    ]

    job_application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='position_info')
    position_applied_for = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    preferred_shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, null=True, blank=True)
    applied_date = models.DateField()

    def __str__(self):
        return self.position_applied_for


# Step 3: Experience
class Experience(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    duration_from = models.DateField(null=True, blank=True)
    duration_to = models.DateField(null=True, blank=True)
    key_responsibilities = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.job_title


# Step 4: Skills & Assessments
class SkillsAssessment(models.Model):
    job_application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='skills_assessment')
    languages = models.CharField(max_length=200, help_text="Comma-separated values")
    tech_skills = models.CharField(max_length=200, help_text="Comma-separated values")
    certificates = models.TextField(blank=True, null=True)
    tech_experience_description = models.TextField()

    def __str__(self):
        return self.tech_skills


# Step 5: Education
class Education(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=100)
    institute = models.CharField(max_length=100)
    graduation_year = models.IntegerField()

    def __str__(self):
        return self.degree


# Step 6: Additional Information
class AdditionalInformation(models.Model):
    job_application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='additional_info')
    why_interested = models.TextField()
    strong_fit_reason = models.TextField()
    eligible_to_work = models.BooleanField()
    source_of_opportunity = models.CharField(max_length=50, choices=[
        ('Referral', 'Referral'),
        ('Social Media', 'Social Media'),
        ('Job Portal', 'Job Portal'),
        ('Fastrak Connect Website', 'Fastrak Connect Website')
    ])

    def __str__(self):
        return self.why_interested


# Step 7 & 8: Media Uploads
class MediaUploads(models.Model):
    def upload_to_path(instance, filename):
        applicant_name = slugify(instance.job_application.name or "unknown")
        return f"uploads/{applicant_name}/{filename}"
    job_application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='media_uploads')
    video = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    resume = models.FileField(upload_to=upload_to_path, blank=True, null=True)
    cover_letter = models.FileField(upload_to=upload_to_path, blank=True, null=True)

    def __str__(self):
        return f"Uploads for {self.job_application}"
# ================ Admin =============
class Admin(User):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    admin_phone = models.CharField(max_length=50, unique=True)
    admin_password = models.CharField(max_length=128)
    admin_gender = models.CharField(max_length=15, choices=GENDER_CHOICES)
    is_Admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"