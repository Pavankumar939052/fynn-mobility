from django.urls import path

from . import views

urlpatterns = [
    path("", views.api_root, name="api-root"),
    path("items/", views.items_view, name="items"),
    path("jobs/", views.jobs_view, name="jobs"),
    path("services/", views.services_view, name="services"),
    path("jobs/<int:job_id>/pay/", views.job_pay_view, name="job-pay"),
    path("revenue/", views.revenue_view, name="revenue"),
]
