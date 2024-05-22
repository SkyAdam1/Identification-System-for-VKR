from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.models import (
    AcademicDegree,
    AcademicTitle,
    AliasUser,
    BrsAdminProfile,
    CustomUser,
    Department,
    Division,
    EducationDepartment,
    Institute,
    Requirement,
    Role,
    StudentProfile,
    UserProfile,
)


class ProfileInline(admin.StackedInline):
    model = BrsAdminProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            ("Personal info"),
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "telegram_id",
                )
            },
        ),
        (("Roles"), {"fields": ("roles",)}),
        (("Admin Department"), {"fields": ("admin_dep",)}),
    )
    list_display = ("username", "middle_name", "first_name", "last_name")
    search_fields = ("username", "middle_name", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "roles")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "email",
                    "telegram_id",
                    "roles",
                    "admin_dep",
                ),
            },
        ),
    )

    def get_inlines(self, request, obj):
        if obj.is_brs_admin or obj.is_deccan:
            return super().get_inlines(request, obj)
        return []

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class ProfileAdmin(admin.ModelAdmin):
    search_fields = [
        "user__middle_name",
        "user__first_name",
        "user__last_name",
        "user__username",
    ]
    list_display = [
        "user",
    ]


class ProfileStudentAdmin(ProfileAdmin):
    search_fields = ProfileAdmin.search_fields + ["group__name"]
    list_display = ["user", "group"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, ProfileAdmin)
admin.site.register(StudentProfile, ProfileStudentAdmin)
admin.site.register(BrsAdminProfile, ProfileAdmin)

admin.site.register(AcademicDegree)
admin.site.register(AcademicTitle)

admin.site.register(Role)
admin.site.register(Department)
admin.site.register(Institute)
admin.site.register(Requirement)
admin.site.register(EducationDepartment)
admin.site.register(Division)

admin.site.register(AliasUser)