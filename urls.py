from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from authentication import views

urlpatterns = [
    path("token/", obtain_jwt_token, name="obtain_jwt_token"),
    path("refresh-token/", refresh_jwt_token, name="obtain_jwt_token_refresh"),
    path("institutes/", views.InstituteList.as_view(), name="institutes"),
    path(
        "institutes/<int:pk>/",
        views.InstituteDetail.as_view(),
    ),
    path(
        "institutes/<int:pk>/departments/",
        views.DepartmentList.as_view(),
    ),
    path(
        "institutes/<int:pk>/education-departments/",
        views.EducationDepartmentList.as_view(),
    ),
    path(
        "departments/<int:pk>/users/",
        views.UsersList.as_view(),
    ),
    path(
        "users/<int:pk>/contracts/",
        views.UserEffectiveContractsList.as_view(),
    ),
    path(
        "profiles-stats/",
        views.GetUserProfileStats.as_view(),
    ),
    path(
        "roles/",
        views.GetRoles.as_view(),
    ),
    path("profile/", views.UpdateUserProfiles.as_view()),
    path("profiles/", views.ListUserProfilesBy.as_view()),
    path("profile/<int:pk>/", views.GetUserProfiles.as_view()),
    path("telegram-connect/", views.TelegramConnectView.as_view()),
]