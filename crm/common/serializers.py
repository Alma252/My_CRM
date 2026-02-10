from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from common.models import Activity, Attachment, Comment, Org, Profile, Tag, Team, User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Org
        fields = (
            "id",
            "name",
            "api_key",
            "company_name",
            "email",
            "phone",
            "website",
            "address_line",
            "city",
            "country",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "api_key", "created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "org",
            "role",
            "is_active",
            "is_staff",
            "password",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "user_email",
            "org",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "job_title",
            "department",
            "timezone",
            "language",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "org",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all(), many=True)

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "org",
            "members",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TeamListSerializer(serializers.ModelSerializer):
    members = ProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = (
            "id",
            "name",
            "description",
            "members",
            "is_active",
            "created_at",
        )


class CommentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "author",
            "content_type",
            "object_id",
            "org",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            "text",
            "author",
            "content_type",
            "object_id",
            "org",
        )

    def validate_content_type(self, value):
        model_name = value.strip().lower()
        try:
            return ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist as exc:
            raise serializers.ValidationError(f"Invalid content type: {value}") from exc

    def create(self, validated_data):
        validated_data["content_type"] = validated_data.pop("content_type")
        return super().create(validated_data)


class AttachmentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(slug_field="model", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = (
            "id",
            "name",
            "file",
            "file_url",
            "uploaded_by",
            "content_type",
            "object_id",
            "org",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class AttachmentCreateSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(write_only=True)

    class Meta:
        model = Attachment
        fields = (
            "name",
            "file",
            "uploaded_by",
            "content_type",
            "object_id",
            "org",
        )

    def validate_content_type(self, value):
        model_name = value.strip().lower()
        try:
            return ContentType.objects.get(model=model_name)
        except ContentType.DoesNotExist as exc:
            raise serializers.ValidationError(f"Invalid content type: {value}") from exc

    def create(self, validated_data):
        validated_data["content_type"] = validated_data.pop("content_type")
        return super().create(validated_data)


class ActivityUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="user.id")
    email = serializers.EmailField(source="user.user.email")
    full_name = serializers.CharField(source="user.user.full_name", allow_null=True)


class ActivitySerializer(serializers.ModelSerializer):
    user = ActivityUserSerializer(read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    humanized_time = serializers.CharField(source="created_on_arrow", read_only=True)

    class Meta:
        model = Activity
        fields = (
            "id",
            "user",
            "action",
            "action_display",
            "entity_type",
            "entity_id",
            "entity_name",
            "description",
            "org",
            "humanized_time",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "humanized_time")
