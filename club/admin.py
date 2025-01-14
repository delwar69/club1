from django.contrib import admin
from .models import Notice, Member, GalleryImage

#admin.site.register(Notice)
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'pdf_file')
    search_fields = ('title',)
admin.site.register(Member)
admin.site.register(GalleryImage)
