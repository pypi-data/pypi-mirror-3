from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from tastypie import fields
from blog.models import *
from newsfeed.models import *

class CategoryResource(ModelResource):
    class Meta:
        queryset = Category.objects.all()
        resource = 'category'
        allowed_methods = ['get']

class LocationResource(ModelResource):
    class Meta:
        queryset = Location.objects.all()
        resource = 'location'
        allowed_methods = ['get']


class PostResource(ModelResource):
    category = fields.ForeignKey(CategoryResource, 'category')
    location = fields.ForeignKey(LocationResource, 'location')
    
    class Meta:
        queryset = Post.objects.published()
        resource = 'post'
        allowed_methods = ['get']
        include_absolute_url = True
        always_return_data = True
        

class StatusResource(ModelResource):
    class Meta:
        queryset = Status.objects.all()
        resource = 'status'
        allowed_methods = ['get']
        include_absolute_url = True