from django.contrib import admin
from bookmarks.models import *


class BookmarkAdmin(admin.ModelAdmin):
    
    list_display = ('title', 'link', 'category', 'tags')
    search_fields = ['title']
    
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()


admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Category)