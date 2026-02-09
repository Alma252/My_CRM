# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Org, Profile, Team, Tag,
    Comment, Attachment, Activity
)


# Admin برای User سفارشی
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'role', 'org', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'org')
    search_fields = ('email', 'full_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('full_name',)}),
        (_('Organization'), {'fields': ('org', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'org', 'role'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Org)
class OrgAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'email', 'phone', 'is_active', 'api_key_short')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'company_name', 'email')
    readonly_fields = ('api_key', 'created_at', 'updated_at')

    def api_key_short(self, obj):
        return f"{obj.api_key[:8]}..." if obj.api_key else ""

    api_key_short.short_description = 'API Key'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'first_name', 'last_name', 'org', 'job_title', 'is_active')
    list_filter = ('is_active', 'org', 'department')
    search_fields = ('user__email', 'first_name', 'last_name', 'phone')
    raw_id_fields = ('user', 'org')

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'org', 'member_count', 'is_active')
    list_filter = ('is_active', 'org')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = 'Members'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'org')
    list_filter = ('org',)
    search_fields = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'author', 'content_type', 'org', 'created_at')
    list_filter = ('org', 'content_type', 'created_at')
    search_fields = ('text', 'author__user__email')
    readonly_fields = ('content_type', 'object_id', 'created_at', 'updated_at')

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = 'Comment'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'file', 'content_type', 'uploaded_by', 'org', 'created_at')
    list_filter = ('org', 'content_type', 'created_at')
    search_fields = ('name', 'file')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'entity_type', 'entity_name', 'org', 'created_at_short')
    list_filter = ('action', 'entity_type', 'org', 'created_at')
    search_fields = ('entity_name', 'description', 'user__user__email')
    readonly_fields = ('created_at', 'updated_at')

    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")

    created_at_short.short_description = 'Created'