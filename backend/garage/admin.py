from django.contrib import admin

from .models import JobService, ServiceItem, VehicleJob


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ("name", "item_type", "price")
    list_filter = ("item_type",)
    search_fields = ("name",)


class JobServiceInline(admin.TabularInline):
    model = JobService
    extra = 0


@admin.register(VehicleJob)
class VehicleJobAdmin(admin.ModelAdmin):
    list_display = ("vehicle_number", "customer_name", "vehicle_model", "status", "total_amount")
    list_filter = ("status",)
    search_fields = ("vehicle_number", "customer_name", "vehicle_model")
    inlines = [JobServiceInline]


@admin.register(JobService)
class JobServiceAdmin(admin.ModelAdmin):
    list_display = ("job", "service_item", "quantity", "line_total")
