from django.urls import path
from .views import (
    LoginAPI, LogoutAPI, MeAPI,
    PublicJobListAPI, PublicJobDetailAPI,
    RecruiterJobCreateAPI, RecruiterJobUpdateAPI, RecruiterJobDeleteAPI,
    ApplyJobAPI,
    RecruiterApplicationListAPI, RecruiterApplicationDetailAPI, RecruiterUpdateStatusAPI
)

urlpatterns = [
    path("auth/login/", LoginAPI.as_view()),
    path("auth/logout/", LogoutAPI.as_view()),
    path("auth/me/", MeAPI.as_view()),

    path("jobs/", PublicJobListAPI.as_view()),
    path("jobs/<slug:slug>/", PublicJobDetailAPI.as_view()),

    path("jobs/create/", RecruiterJobCreateAPI.as_view()),
    path("jobs/<int:id>/update/", RecruiterJobUpdateAPI.as_view()),
    path("jobs/<int:id>/delete/", RecruiterJobDeleteAPI.as_view()),

    path("apply/<slug:slug>/", ApplyJobAPI.as_view()),

    path("applications/", RecruiterApplicationListAPI.as_view()),
    path("applications/<int:id>/", RecruiterApplicationDetailAPI.as_view()),
    path("applications/<int:id>/status/", RecruiterUpdateStatusAPI.as_view()),
]