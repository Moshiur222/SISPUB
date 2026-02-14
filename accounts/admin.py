from django.contrib import admin
from .models import PhotoAlbum, Photo

# This allows you to edit Photos directly inside the PhotoAlbum page
class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1  # Number of empty slots to show for new uploads
    fields = ['image', 'created_at']
    readonly_fields = ['created_at']

@admin.register(PhotoAlbum)
class PhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_preview')
    inlines = [PhotoInline]

    def banner_preview(self, obj):
        if obj.banner:
            return "Image Attached"
        return "No Banner"
    banner_preview.short_description = "Banner Status"

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'album', 'created_at')
    list_filter = ('album', 'created_at')
    search_fields = ('album__title',)