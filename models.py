from django.apps import apps
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import IntegrityError, models
from django.db.models import Exists as Ex
from django.db.models import OuterRef
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import NotFound

from brs.models import Group


class Role(models.Model):
    """
    The Role entries are managed by the system,
    automatically created via a Django data migration.
    """

    EMPLOYEE = 1
    ADMIN = 2
    FINANCE = 3
    SUPER = 4
    TEACHER = 5
    STUDENT = 6
    BRS_ADMIN = 7
    DECCAN = 8

    ROLE_CHOICES = (
        (STUDENT, "student"),
        (TEACHER, "teacher"),
        (EMPLOYEE, "employee"),
        (FINANCE, "finance"),
        (ADMIN, "admin"),
        (SUPER, "super"),
        (BRS_ADMIN, "brs_admin"),
        (DECCAN, "deccan"),
    )

    id = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, primary_key=True
    )

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.get_id_display()


class Institute(models.Model):
    INST = 1
    ADMIN = 2

    UNIT_CHOICES = (
        (INST, "inst"),
        (ADMIN, "admin"),
    )
    name = models.CharField(max_length=250)
    unit = models.PositiveSmallIntegerField(choices=UNIT_CHOICES, default=INST)

    class Meta:
        verbose_name = "Институт"
        verbose_name_plural = "Институты"

    def __str__(self):
        return self.name


class Division(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=250)
    institute = models.ForeignKey(
        Institute,
        verbose_name="Институт",
        null=True,
        on_delete=models.SET_NULL,
    )
    division = models.ForeignKey(
        Division,
        verbose_name="Подразделение",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    allow_application = models.BooleanField(
        verbose_name="Использовать в сервисе заявок", default=False
    )

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self):
        return self.name

    @classmethod
    def filter_by_institute(cls, institute):
        if isinstance(institute, (int, str)):
            filters = {"institute__pk": institute}
        else:
            filters = {"institute": institute}
        return cls._query(filters)

    @classmethod
    def _query(cls, filters: dict):
        return cls.objects.filter(**filters)


class EducationDepartment(models.Model):
    name = models.CharField(max_length=250)
    institute = models.ForeignKey(
        Institute, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"

    def __str__(self):
        return self.name

    @classmethod
    def filter_by_institute(cls, institute):
        if isinstance(institute, (int, str)):
            filters = {"institute__pk": institute}
        else:
            filters = {"institute": institute}
        return cls._query(filters)

    @classmethod
    def _query(cls, filters: dict):
        return cls.objects.filter(**filters)


class AcademicDegree(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Ученая степень"
        verbose_name_plural = "Ученые степени"

    def __str__(self):
        return self.name


class AcademicTitle(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Ученое звание"
        verbose_name_plural = "Ученые звания"

    def __str__(self):
        return self.name


class CustomUserManager(UserManager):
    def get_queryset(self):
        rfilter = Role.objects.filter
        try:
            return (
                super()
                .get_queryset()
                .annotate(
                    is_student=Ex(
                        rfilter(pk=Role.STUDENT, customuser=OuterRef("pk"))
                    ),
                    is_teacher=Ex(
                        rfilter(pk=Role.TEACHER, customuser=OuterRef("pk"))
                    ),
                    is_employee=Ex(
                        rfilter(pk=Role.EMPLOYEE, customuser=OuterRef("pk"))
                    ),
                    is_finance=Ex(
                        rfilter(pk=Role.FINANCE, customuser=OuterRef("pk"))
                    ),
                    is_admin=Ex(
                        rfilter(pk=Role.ADMIN, customuser=OuterRef("pk"))
                    ),
                    is_super=Ex(
                        rfilter(pk=Role.SUPER, customuser=OuterRef("pk"))
                    ),
                    is_brs_admin=Ex(
                        rfilter(pk=Role.BRS_ADMIN, customuser=OuterRef("pk"))
                    ),
                    is_deccan=Ex(
                        rfilter(pk=Role.DECCAN, customuser=OuterRef("pk"))
                    ),
                )
            )
        except AttributeError:
            return super().get_queryset()


class CustomUser(AbstractUser):
    is_student: bool
    is_teacher: bool
    is_employee: bool
    is_finance: bool
    is_admin: bool
    is_super: bool
    is_brs_admin: bool
    is_deccan: bool

    DUMR = 1
    UNIR = 2
    UVR = 3
    OK = 4
    SU = 5
    CDEO = 6

    DEP_CHOICES = (
        (DUMR, "ДУМР"),
        (UNIR, "УНИР"),
        (UVR, "УВР"),
        (OK, "ОК"),
        (SU, "SU"),
        (CDEO, "CDEO"),
    )
    roles = models.ManyToManyField(Role, blank=True)
    middle_name = models.CharField(max_length=150, blank=True)
    admin_dep = models.PositiveSmallIntegerField(
        choices=DEP_CHOICES, null=True, blank=True
    )
    telegram_id = models.PositiveIntegerField(
        null=True, blank=True, unique=True, db_index=True
    )
    objects = CustomUserManager()

    class Meta:
        ordering = ("middle_name",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} | {self.fio()}"

    def fio(self, shorter: bool = False):
        if not shorter:
            return " ".join(
                [self.middle_name, self.first_name, self.last_name]
            )
        name = self.middle_name
        if self.first_name:
            name += f" {self.first_name[0]}."
        if self.last_name:
            name += f" {self.last_name[0]}"
        return name

    def get_roles_str(self):
        roles = [str(role) for role in self.roles.all()]
        if self.admin_dep == CustomUser.DUMR:
            roles.append("dumr")
        return roles

    @classmethod
    def filter_users_by_ec(cls, department, status, istatus, admin_dep):
        _filter = {}
        if status:
            _filter["effectivecontract__status__in"] = status.split(",")
        if istatus:
            _filter[
                "effectivecontract__effectivecontractitem__status"
            ] = istatus
            if admin_dep:
                _filter[
                    "effectivecontract__effectivecontractitem__type_of_work__admin_dep"
                ] = admin_dep
        return CustomUser.objects.filter(
            userprofile__work_department=department,
            roles=Role.EMPLOYEE,
            **_filter,
        ).distinct()


class AliasUser(models.Model):
    user = models.OneToOneField(CustomUser, models.CASCADE, unique=True)
    alias = models.CharField("Alias", max_length=255, unique=True)

    def __str__(self) -> str:
        return self.alias


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, models.CASCADE, unique=True)
    division = models.ForeignKey(
        Division, null=True, blank=True, on_delete=models.SET_NULL
    )
    work_department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL
    )
    institute = models.ForeignKey(
        Institute, null=True, blank=True, on_delete=models.SET_NULL
    )
    education_department = models.ForeignKey(
        EducationDepartment, null=True, blank=True, on_delete=models.SET_NULL
    )
    photo = models.ImageField(null=True, blank=True, upload_to="user_photo")
    position = models.CharField(
        "Должность", max_length=255, null=True, blank=True
    )
    academic_degree = models.CharField(
        verbose_name="Ученая степень", max_length=250, null=True, blank=True
    )
    academic_title = models.CharField(
        verbose_name="Ученое звание", max_length=250, null=True, blank=True
    )
    short_bio = models.TextField("Краткая биография", null=True, blank=True)
    awards_achievements = models.TextField(
        "Награды и достижения", null=True, blank=True
    )
    professional_development = models.TextField(
        "Курсы повышения квалификации и переподготовки", null=True, blank=True
    )
    work_experience = models.TextField(
        "Трудовая деятельность", null=True, blank=True
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        return str(self.user.fio())

    @classmethod
    def get_by_user_or_not_found(cls, user):
        if isinstance(user, (int, str)):
            _filter = {"user__pk": user}
        else:
            _filter = {"user": user}
        try:
            return UserProfile.objects.get(**_filter)
        except Exception:
            raise NotFound

    @classmethod
    def get_stats(cls):
        q = UserProfile.objects.filter()
        return {
            "users_count": q.count(),
            "empty_any": q.filter(
                academic_degree__isnull=True,
                academic_title__isnull=True,
                awards_achievements="",
                professional_development="",
                work_experience="",
            ).count(),
            "empty_academic_degree": q.filter(
                academic_degree__isnull=True
            ).count(),
            "empty_academic_title": q.filter(
                academic_title__isnull=True
            ).count(),
            "empty_short_bio": q.filter(short_bio="").count(),
            "empty_awards_achievements": q.filter(
                awards_achievements=""
            ).count(),
            "empty_professional_development": q.filter(
                professional_development=""
            ).count(),
            "empty_work_experience": q.filter(work_experience="").count(),
        }


class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, models.CASCADE, unique=True)
    number_id = models.CharField(max_length=150)
    group = models.ForeignKey(
        Group,
        models.CASCADE,
        verbose_name="Группа",
        null=True,
        blank=True,
        related_name="students",
    )
    allowed = models.BooleanField(default=True, null=True, blank=True)
    distance_education = models.BooleanField(default=False)

    __group = None

    class Meta:
        verbose_name = "Профиль студента"
        verbose_name_plural = "Профили студентов"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__group = self.group

    def __str__(self) -> str:
        return str(self.user)

    def save_base(self, *args, **kwargs):
        if self.group != self.__group and self.group is not None:
            Discipline = apps.get_model("brs", "Discipline")
            GradeSum = apps.get_model("brs", "GradeSum")
            disciplines = Discipline.objects.filter(group=self.group)
            GradeSum.objects.filter(student=self.user).exclude(
                discipline__group=self.group
            ).delete()
            GradeSum.objects.bulk_create(
                [
                    GradeSum(student=self.user, discipline=discipline)
                    for discipline in disciplines
                ],
                ignore_conflicts=True,
            )

            Journal = apps.get_model("brs", "Journal")
            JournalLog = apps.get_model("brs", "JournalLog")
            journals = Journal.objects.filter(group=self.group)
            JournalLog.objects.filter(student=self.user).exclude(
                discipline__group=self.group
            ).delete()
            JournalLog.objects.bulk_create(
                [
                    JournalLog(
                        journal=journal,
                        discipline=journal.discipline,
                        group=self.group,
                        student=self.user,
                        date=journal.date,
                    )
                    for journal in journals
                ],
                ignore_conflicts=True,
            )

        return super().save_base(*args, **kwargs)


class BrsAdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, models.CASCADE, unique=True)
    institute = models.ForeignKey(
        "brs.Institute",
        models.CASCADE,
        verbose_name="Институт",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Профиль админа БРС"
        verbose_name_plural = "Профили админов БРС"

    def __str__(self) -> str:
        return str(self.user)


class Requirement(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    effective_contract = models.ForeignKey(
        "effective_contract.EffectiveContract", on_delete=models.CASCADE
    )
    confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Зависимость"
        verbose_name_plural = "Зависимости"


@receiver(m2m_changed, sender=CustomUser.roles.through)
def changing_role(sender, instance: CustomUser, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        instance = CustomUser.objects.filter(pk=instance.pk).first()
        if not instance:
            return
        if not (instance.is_employee or instance.is_teacher):
            UserProfile.objects.filter(user=instance).delete()
        if not instance.is_student:
            StudentProfile.objects.filter(user=instance).delete()
        if not (instance.is_brs_admin or instance.is_deccan):
            BrsAdminProfile.objects.filter(user=instance).delete()
        if instance.is_employee or instance.is_teacher:
            try:
                if not UserProfile.objects.filter(user=instance).exists():
                    UserProfile.objects.create(user=instance)
            except IntegrityError:
                pass
        if instance.is_student:
            try:
                if not StudentProfile.objects.filter(user=instance).exists():
                    StudentProfile.objects.create(user=instance)
            except IntegrityError:
                pass
        if instance.is_brs_admin or instance.is_deccan:
            try:
                if not BrsAdminProfile.objects.filter(user=instance).exists():
                    BrsAdminProfile.objects.create(user=instance)
            except IntegrityError:
                pass