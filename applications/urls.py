from django.urls import path
from django.shortcuts import render
from applications.views.public import apply_job

from applications.views.hr import (
    HRApplicationListView, HRApplicationDetailView,
    preview_resume,HRStatusUpdateView
)
from applications.views.public import apply_job, application_success,track_application
urlpatterns = [
    # candidate apply form 
    path("apply/<slug:slug>/", apply_job, name="apply_job"),
    # path("success/", lambda r: render(r, "applications/success.html"), name="application_success"),
     path("success/", application_success, name="application_success"),
    # this is for  a track page 
    path("track/<str:application_id>/", track_application, name="track_application"),

    path("hr/list/", HRApplicationListView.as_view(), name="hr_applications_list"),
    path("hr/<int:pk>/", HRApplicationDetailView.as_view(), name="hr_application_detail"),
    
    # NEW   
    path("hr/<int:pk>/status/", HRStatusUpdateView.as_view(), name="hr_application_status"),
    # hr see the uploaded pdf 
    path("hr/<int:pk>/resume/preview/", preview_resume, name="preview_resume"), 
]




