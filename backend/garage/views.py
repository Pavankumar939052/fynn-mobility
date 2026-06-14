import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear, TruncDate
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import JobService, ServiceItem, VehicleJob


def api_root(_request):
    return JsonResponse({
        "message": "Fyn Mobility API",
        "endpoints": [
            "/api/items/",
            "/api/jobs/",
            "/api/services/",
            "/api/jobs/<id>/pay/",
            "/api/revenue/",
        ],
    })


def parse_json(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON payload: {exc.msg}") from exc


def parse_decimal(value, field_name):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Enter a valid amount."}) from exc


def parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Enter a valid number."}) from exc


def validation_error_response(exc):
    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = exc.messages
    else:
        payload = [str(exc)]
    return JsonResponse({"errors": payload}, status=400)


def serialize_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "item_type": item.item_type,
        "item_type_label": item.get_item_type_display(),
        "price": float(item.price),
        "notes": item.notes,
    }


def serialize_service(service):
    return {
        "id": service.id,
        "job_id": service.job_id,
        "service_item_id": service.service_item_id,
        "service_item_name": service.service_item.name,
        "description": service.description,
        "quantity": service.quantity,
        "labor_charge": float(service.labor_charge),
        "line_total": float(service.line_total),
    }


def serialize_job(job):
    return {
        "id": job.id,
        "vehicle_number": job.vehicle_number,
        "customer_name": job.customer_name,
        "vehicle_model": job.vehicle_model,
        "complaint": job.complaint,
        "status": job.status,
        "status_label": job.get_status_display(),
        "total_amount": float(job.total_amount),
        "paid_at": job.paid_at.isoformat() if job.paid_at else None,
        "services": [serialize_service(service) for service in job.services.select_related("service_item").all()],
    }


@csrf_exempt
def items_view(request):
    if request.method == "GET":
        return JsonResponse({"items": [serialize_item(item) for item in ServiceItem.objects.all()]})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    try:
        payload = parse_json(request)
        item = ServiceItem(
            name=payload.get("name", ""),
            item_type=payload.get("item_type", ""),
            price=parse_decimal(payload.get("price", 0), "price"),
            notes=payload.get("notes", ""),
        )
        item.full_clean()
        item.save()
        return JsonResponse({"item": serialize_item(item)}, status=201)
    except ValidationError as exc:
        return validation_error_response(exc)


@csrf_exempt
def jobs_view(request):
    if request.method == "GET":
        jobs = VehicleJob.objects.prefetch_related("services__service_item").all()
        return JsonResponse({"jobs": [serialize_job(job) for job in jobs]})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    try:
        payload = parse_json(request)
        job = VehicleJob(
            vehicle_number=payload.get("vehicle_number", "").upper(),
            customer_name=payload.get("customer_name", ""),
            vehicle_model=payload.get("vehicle_model", ""),
            complaint=payload.get("complaint", ""),
        )
        job.full_clean()
        job.save()
        return JsonResponse({"job": serialize_job(job)}, status=201)
    except ValidationError as exc:
        return validation_error_response(exc)


@csrf_exempt
def services_view(request):
    if request.method == "GET":
        services = JobService.objects.select_related("job", "service_item").all()
        return JsonResponse({"services": [serialize_service(service) for service in services]})

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    try:
        payload = parse_json(request)
        job = get_object_or_404(VehicleJob, pk=payload.get("job_id"))
        item = get_object_or_404(ServiceItem, pk=payload.get("service_item_id"))
        service = JobService(
            job=job,
            service_item=item,
            description=payload.get("description", ""),
            quantity=parse_int(payload.get("quantity", 1), "quantity"),
            labor_charge=parse_decimal(payload.get("labor_charge", 0), "labor_charge"),
        )
        service.full_clean()
        service.save()
        job.refresh_from_db()
        return JsonResponse({"service": serialize_service(service), "job": serialize_job(job)}, status=201)
    except ValidationError as exc:
        return validation_error_response(exc)


@csrf_exempt
def job_pay_view(request, job_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    job = get_object_or_404(VehicleJob, pk=job_id)
    job.refresh_total()
    job.mark_paid()
    return JsonResponse({"job": serialize_job(job)})


def revenue_view(_request):
    paid_jobs = VehicleJob.objects.filter(status=VehicleJob.STATUS_PAID, paid_at__isnull=False)

    def build_series(trunc_expression, label_format):
        rows = (
            paid_jobs.annotate(period=trunc_expression)
            .values("period")
            .annotate(revenue=Sum("total_amount"))
            .order_by("period")
        )
        return [{"label": row["period"].strftime(label_format), "revenue": float(row["revenue"] or 0)} for row in rows]

    return JsonResponse({
        "daily": build_series(TruncDate("paid_at"), "%d %b"),
        "monthly": build_series(TruncMonth("paid_at"), "%b %Y"),
        "yearly": build_series(TruncYear("paid_at"), "%Y"),
        "total_revenue": float(paid_jobs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")),
    })
