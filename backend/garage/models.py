from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class ServiceItem(models.Model):
    TYPE_PART = "part"
    TYPE_REPAIR = "repair"
    TYPE_CHOICES = [
        (TYPE_PART, "New Part"),
        (TYPE_REPAIR, "Repair Service"),
    ]

    name = models.CharField(max_length=120)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VehicleJob(models.Model):
    STATUS_OPEN = "open"
    STATUS_PAID = "paid"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_PAID, "Paid"),
    ]

    vehicle_number = models.CharField(max_length=40, unique=True)
    customer_name = models.CharField(max_length=120)
    vehicle_model = models.CharField(max_length=120)
    complaint = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.vehicle_number

    def refresh_total(self):
        self.total_amount = self.services.aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")
        self.save(update_fields=["total_amount", "updated_at"])

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])


class JobService(models.Model):
    job = models.ForeignKey(VehicleJob, on_delete=models.CASCADE, related_name="services")
    service_item = models.ForeignKey(ServiceItem, on_delete=models.CASCADE, related_name="job_services")
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    labor_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        if self.quantity < 1:
            raise ValidationError({"quantity": "Quantity must be at least 1."})

    def save(self, *args, **kwargs):
        self.full_clean()
        self.line_total = (self.service_item.price * self.quantity) + self.labor_charge
        super().save(*args, **kwargs)
        self.job.refresh_total()

    def delete(self, *args, **kwargs):
        job = self.job
        super().delete(*args, **kwargs)
        job.refresh_total()
