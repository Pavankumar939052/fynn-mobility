import json
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import JobService, ServiceItem, VehicleJob


class GarageApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = ServiceItem.objects.create(name="Battery Check", item_type="repair", price=Decimal("500.00"))

    def test_service_updates_job_total(self):
        job = VehicleJob.objects.create(vehicle_number="DL01AA1001", customer_name="Ravi", vehicle_model="Ola S1", complaint="Battery issue")
        JobService.objects.create(job=job, service_item=self.item, description="Check battery", quantity=2, labor_charge=Decimal("100.00"))
        job.refresh_from_db()
        self.assertEqual(job.total_amount, Decimal("1100.00"))

    def test_item_endpoint_creates_item(self):
        response = self.client.post(reverse("items"), data=json.dumps({"name": "Brake Set", "item_type": "part", "price": "1200.00", "notes": "Front"}), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ServiceItem.objects.count(), 2)

    def test_payment_endpoint_marks_job_paid(self):
        job = VehicleJob.objects.create(vehicle_number="DL01AA1002", customer_name="Mina", vehicle_model="Ather 450X", complaint="Service")
        JobService.objects.create(job=job, service_item=self.item, description="General check", quantity=1, labor_charge=Decimal("50.00"))
        response = self.client.post(reverse("job-pay", args=[job.id]))
        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.status, VehicleJob.STATUS_PAID)
        self.assertIsNotNone(job.paid_at)

    def test_revenue_endpoint(self):
        VehicleJob.objects.create(vehicle_number="DL01AA1003", customer_name="Tina", vehicle_model="Ampere Magnus", complaint="Wheel issue", status=VehicleJob.STATUS_PAID, total_amount=Decimal("2100.00"), paid_at=timezone.now())
        response = self.client.get(reverse("revenue"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_revenue"], 2100.0)
