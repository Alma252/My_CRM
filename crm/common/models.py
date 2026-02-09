import uuid
from django.db import models
from common.base import BaseModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from common.managers import UserManager
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)

    org = models.ForeignKey(
        "Org",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ("SUPER_ADMIN", "Super Admin"),
        ("ORG_ADMIN", "Org Admin"),
        ("USER", "User"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USER")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ("-created_at",)

    def __str__(self):
        return self.email



def generate_unique_key():
    return uuid.uuid4().hex


class Org(BaseModel):
    name = models.CharField(max_length=150)

    api_key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_unique_key,
        editable=False,
    )

    is_active = models.BooleanField(default=True)

    company_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    address_line = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        db_table = "orgs"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="profiles",
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    avatar = models.FileField(upload_to="avatars/", null=True, blank=True)

    job_title = models.CharField(max_length=150, blank=True, null=True)
    department = models.CharField(max_length=150, blank=True, null=True)

    timezone = models.CharField(max_length=50, default="UTC")
    language = models.CharField(max_length=10, default="en")

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "profiles"

    def __str__(self):
        return f"{self.user.email}"

class Team(BaseModel):
    name = models.CharField(max_length=150)

    org = models.ForeignKey(
    Org,
     on_delete=models.CASCADE,
     related_name="teams",
    )

    members = models.ManyToManyField(
        Profile,
        related_name="teams",
        blank=True,
    )

    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "teams"
        unique_together = ("name", "org")

    def __str__(self):
        return f"{self.name} - {self.org.name}"


class Tag(BaseModel):
    name = models.CharField(max_length=100)

    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="tags",
    )

    class Meta:
        db_table = "tags"
        unique_together = ("name", "org")

    def __str__(self):
        return self.name


class Comment(BaseModel):
    # ارتباط generic با هر مدل

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    # متن کامنت
    text = models.TextField()

    # نویسنده کامنت
    author = models.ForeignKey(
        "Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments",
    )

    # سازمان
    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        db_table = "comments"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["org", "-created_at"]),
        ]

    def __str__(self):
        return self.text[:40]



class Attachment(BaseModel):
    # ارتباط generic با هر مدل
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    file = models.FileField(upload_to="attachments/%Y/%m/")
    name = models.CharField(max_length=255, blank=True, null=True)

    uploaded_by = models.ForeignKey(
        "Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )

    org = models.ForeignKey(
        "Org",
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    class Meta:
        db_table = "attachments"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["org", "-created_at"]),
        ]

    def __str__(self):
        return self.name or self.file.name



class Activity(BaseModel):
    """Track user activities across all CRM entities"""

    ACTION_CHOICES = (
        ("CREATE", "Created"),
        ("UPDATE", "Updated"),
        ("DELETE", "Deleted"),
        ("VIEW", "Viewed"),
        ("COMMENT", "Commented"),
        ("ASSIGN", "Assigned"),
    )

    ENTITY_TYPE_CHOICES = (
        ("Account", "Account"),
        ("Lead", "Lead"),
        ("Contact", "Contact"),
        ("Opportunity", "Opportunity"),
        ("Case", "Case"),
        ("Task", "Task"),
        ("Invoice", "Invoice"),
        ("Event", "Event"),
        ("Document", "Document"),
        ("Team", "Team"),
    )

    user = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    entity_id = models.UUIDField()
    entity_name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True, default="")
    org = models.ForeignKey(Org, on_delete=models.CASCADE, related_name="activities")

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        db_table = "activity"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["org", "-created_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.entity_type}: {self.entity_name}"

    @property
    def created_on_arrow(self):
        return timesince(self.created_at) + " ago"












