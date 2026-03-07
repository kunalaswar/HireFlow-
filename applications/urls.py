from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job
from applications.views.recruiter import (
    RecruiterApplicationListView,
    RecruiterApplicationDetailView,
    preview_resume,
    RecruiterStatusUpdateView
)
from applications.views.public import apply_job, application_success, track_application

urlpatterns = [

    # Candidate Apply
    path("apply/<slug:slug>/", apply_job, name="apply_job"),
    path("success/", application_success, name="application_success"),
    path("track/<str:application_id>/", track_application, name="track_application"),

    # RECRUITER Applications
    path("recruiter/list/", RecruiterApplicationListView.as_view(), name="recruiter_applications_list"),
    path("recruiter/<int:pk>/status/", RecruiterStatusUpdateView.as_view(), name="recruiter_status_update"),
    path("recruiter/<int:pk>/", RecruiterApplicationDetailView.as_view(), name="recruiter_application_detail"),
    path("recruiter/<int:pk>/resume/preview/", preview_resume, name="preview_resume"),
]