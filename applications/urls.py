from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job
from applications.views.hr import (
    HRApplicationListView,
    HRApplicationDetailView,
    preview_resume,
    HRStatusUpdateView
)
from applications.views.public import apply_job, application_success, track_application

urlpatterns = [

    # Candidate Apply
    path("apply/<slug:slug>/", apply_job, name="apply_job"),
    path("success/", application_success, name="application_success"),
    path("track/<str:application_id>/", track_application, name="track_application"),

    # HR Applications
    path("hr/list/", HRApplicationListView.as_view(), name="hr_applications_list"),
    path("hr/<int:pk>/status/", HRStatusUpdateView.as_view(), name="hr_status_update"),
    path("hr/<int:pk>/", HRApplicationDetailView.as_view(), name="hr_application_detail"),
    path("hr/<int:pk>/resume/preview/", preview_resume, name="preview_resume"),
]