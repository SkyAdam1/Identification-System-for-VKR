from django.core.cache import cache
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import (
    CustomUser,
    Department,
    EducationDepartment,
    Institute,
    UserProfile,
)
from authentication.permissions import IsEmployee
from authentication.serializers import (
    DepartmentSerializer,
    EducationDepartmentSerializer,
    InstituteSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from effective_contract.models import EffectiveContract
from effective_contract.serializers import EffectiveContractSerializer


class InstituteList(generics.ListAPIView):
    serializer_class = InstituteSerializer
    queryset = Institute.objects.all()
    permission_classes = []


class InstituteDetail(generics.RetrieveAPIView):
    serializer_class = InstituteSerializer
    queryset = Institute.objects.all()
    permission_classes = []


class DepartmentList(APIView):
    permission_classes = [IsEmployee]

    def get(self, request, pk):
        departments = Department.filter_by_institute(pk)
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EducationDepartmentList(APIView):
    permission_classes = []

    def get(self, request, pk):
        departments = EducationDepartment.filter_by_institute(pk)
        serializer = EducationDepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersList(APIView):
    permission_classes = [IsEmployee]

    def get(self, request, pk):
        department = Department.objects.get(pk=pk)

        _status = request.query_params.get("status")
        istatus = request.query_params.get("istatus")

        users = CustomUser.filter_users_by_ec(
            department, _status, istatus, self.request.user.admin_dep
        )
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEffectiveContractsList(APIView):
    permission_classes = [IsEmployee]

    def get(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        effective_contracts = EffectiveContract.get_user_contracts(user)
        serializer = EffectiveContractSerializer(
            effective_contracts, many=True
        )
        return Response(
            {"fullname": user.fio(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )


class GetUserProfiles(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.get_by_user_or_not_found(self.kwargs["pk"])


class UpdateUserProfiles(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.get_by_user_or_not_found(self.request.user)


class ListUserProfilesBy(generics.ListAPIView):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        filters = {}
        institute = self.request.query_params.get("institute", None)
        education_department = self.request.query_params.get(
            "department", None
        )
        name = self.request.query_params.get("name", None)
        if institute and not education_department:
            filters["education_department__institute__pk"] = institute
        if education_department:
            filters["education_department__pk"] = education_department
        if name:
            filters["fullname__icontains"] = name
        return (
            UserProfile.objects.annotate(
                fullname=Concat(
                    F("user__middle_name"),
                    Value(" "),
                    F("user__first_name"),
                    Value(" "),
                    F("user__last_name"),
                    output_field=CharField(),
                ),
            )
            .filter(**filters)
            .order_by("fullname")
        )


class GetUserProfileStats(APIView):
    permission_classes = [IsEmployee]

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UserProfile.get_stats())


class GetRoles(APIView):
    def get(self, *args, **kwargs):
        user = self.request.user
        return Response(user.get_roles_str())


class TelegramConnectView(APIView):
    def get(self, *args, **kwargs):
        code = self.request.query_params.get("code")

        if not (telegram_id := cache.get(code, None)) or not code:
            return Response(
                {"message": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST
            )

        if self.request.user.telegram_id:
            return Response(
                {"message": "Нельзя подключить телеграм аккаунт"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.request.user.telegram_id = int(telegram_id)
            self.request.user.save()
        except Exception:
            return Response(
                {"message": "Ошибка выполнения"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        cache.delete(code)
        cache.delete(telegram_id)
        return Response(
            {"message": "Аккаунт Telegram привязан"}, status=status.HTTP_200_OK
        )