from django.contrib import admin
# Import your models here.
from blog.models import *
from newsfeed.models import Location
from django import forms
from django.conf import settings

class PostAdmin(admin.ModelAdmin):
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'class':'ckeditor'})}, }
    list_display = ('title', 'tags', 'category', 'location', 'published')
    save_on_top = True
    actions = ['publish', 'set_to_manhattan']

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

    def publish(self, request, queryset):
        rows = queryset.update(published=True)
        if rows == 1:
            message_bit = "1 blog post was"
        else:
            message_bit = "%s blog posts were" % rows
        self.message_user(request, "%s successfully published." % message_bit)
        
    if settings.BLOG_HTML_ONLY == False:
        class Media:
            js = ('http://static.derekandlindy.com/staging/iroam/javascript/ckeditor/ckeditor.js',)
            
    def set_to_manhattan(self, request,queryset):
        location = Location.objects.filter(city='Manhattan')
        rows = queryset.update(locaiton=location)
        if rows == 1:
            message_bit = "1 post was"
        else:
            message_bit = "%s posts were" % rows
        self.message_user(request, "%s successfully updated." % message_bit)
        
admin.site.register(Post, PostAdmin)
admin.site.register(Status)

admin.site.register(Category)