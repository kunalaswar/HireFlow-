from django.urls import path
from .views import (
    LoginAPI, LogoutAPI, MeAPI,
    PublicJobListAPI, PublicJobDetailAPI,
    HRJobCreateAPI, HRJobUpdateAPI, HRJobDeleteAPI,
    ApplyJobAPI,
    HRApplicationListAPI, HRApplicationDetailAPI, HRUpdateStatusAPI
)

urlpatterns = [
    path("auth/login/", LoginAPI.as_view()),
    path("auth/logout/", LogoutAPI.as_view()),
    path("auth/me/", MeAPI.as_view()),

    path("jobs/", PublicJobListAPI.as_view()),
    path("jobs/<slug:slug>/", PublicJobDetailAPI.as_view()),

    path("jobs/create/", HRJobCreateAPI.as_view()),
    path("jobs/<int:id>/update/", HRJobUpdateAPI.as_view()),
    path("jobs/<int:id>/delete/", HRJobDeleteAPI.as_view()),

    path("apply/<slug:slug>/", ApplyJobAPI.as_view()),

    path("applications/", HRApplicationListAPI.as_view()),
    path("applications/<int:id>/", HRApplicationDetailAPI.as_view()),
    path("applications/<int:id>/status/", HRUpdateStatusAPI.as_view()),
]
