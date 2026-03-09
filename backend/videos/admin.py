from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "duration", "uploaded_by", "created_at"]
    search_fields = ["title"]
    readonly_fields = ["id", "created_at"]
