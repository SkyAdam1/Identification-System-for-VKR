from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from authentication.models import (
    CustomUser,
    Department,
    EducationDepartment,
    Institute,
    UserProfile,
)


class EnumField(serializers.ChoiceField):
    default_error_messages = {"invalid": "No matching type"}

    def __init__(self, choices, **kwargs):
        self._choices = choices
        super().__init__(choices, **kwargs)

    def to_representation(self, value):
        return self._choices.get(value)

    def to_internal_value(self, data):
        for id, choice in self._choices.items():
            if data == choice:
                return id
        self.fail("invalid")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "roles",
        )


class InstituteSerializer(serializers.ModelSerializer):
    unit = EnumField(choices=Institute.UNIT_CHOICES)

    class Meta:
        model = Institute
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class EducationDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDepartment
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField("get_fullname")
    institute = PrimaryKeyRelatedField(
        queryset=Institute.objects.all(), required=False
    )
    work_department = PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False
    )
    education_department = PrimaryKeyRelatedField(
        queryset=EducationDepartment.objects.all(), required=False
    )

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "user",
            "fullname",
            "institute",
            "work_department",
            "education_department",
            "position",
            "academic_degree",
            "academic_title",
            "short_bio",
            "awards_achievements",
            "professional_development",
            "work_experience",
            "photo",
        )

    def get_fullname(self, obj):
        return obj.user.fio()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["work_department"] = DepartmentSerializer(
            instance.work_department
        ).data
        data["education_department"] = EducationDepartmentSerializer(
            instance.education_department
        ).data

        request = self.context.get("request")
        if instance.photo:
            data["photo"] = request.build_absolute_uri(
                instance.photo.url
            ).replace("http:", "https:")
        return data