from rest_framework.permissions import SAFE_METHODS, BasePermission

from authentication.models import CustomUser


class IsOwner(BasePermission):
    message = "You don't have access to his object"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsEmployee(BasePermission):
    message = "You are not a employee"

    def has_permission(self, request, view):
        return (
            request.user.is_employee
            or request.user.is_admin
            or request.user.is_staff
        )


class IsStudent(BasePermission):
    message = "You are not a student"

    def has_permission(self, request, view):
        return request.user.is_student


class IsTeacher(BasePermission):
    message = "You are not a teacher"

    def has_permission(self, request, view):
        return request.user.is_teacher


class IsBrsAdmin(BasePermission):
    message = "You are not a brs admin"

    def has_permission(self, request, view):
        return request.user.is_brs_admin


class IsDeccan(BasePermission):
    message = "You are not a deccan"

    def has_permission(self, request, view):
        if request.user.admin_dep == CustomUser.DUMR:
            return True
        return request.user.is_deccan or request.user.is_staff