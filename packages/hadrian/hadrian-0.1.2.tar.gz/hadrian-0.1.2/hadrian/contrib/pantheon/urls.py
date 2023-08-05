from django.conf.urls.defaults import patterns, include, url
# Import your views and feeds from your app.
from blog.views import *
from blog.feeds import BlogFeed
from django.views.generic.simple import direct_to_template
from blog.api import PostResource, StatusResource, LocationResource, CategoryResource
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(PostResource())
v1_api.register(StatusResource())
v1_api.register(LocationResource())
v1_api.register(CategoryResource())

urlpatterns = patterns('',
    
    # Homepage url , always name your URLS
    url(r'^$', home, name="home"),
    url(r'^posts/$', posts, name="posts"),
    # URl with add and nothing after
    # Feed URL
    url(r'^feed/$', BlogFeed(), name="blogfeed"),
    url(r'^status/$', twitter_feed, name="twitter_feed"),
    url(r'^status_sync/$', twitter_sync, name="twitter_sync"),
    url(r'^post/(?P<post_slug>[-\w]+)/$', post, name="post"),
    url(r'^category/list/(?P<category_slug>[-\w]+)/$', category_list, name="category_list"),
    url(r'^category/(?P<category_slug>[-\w]+)/$', category, name="category"),
    
    #url(r'^sync/', sync),
    url(r'^about/', direct_to_template, {'template': 'blog/about.html'}, name="about"),
    #url(r'^tag/(?P<tag_slug>[-\w]+)/$', tag, name="tag"),
    url(r'^apis/$', 'api_docs.views.home', name="api_listing"),
    
    url(r'^api/', include(v1_api.urls)),
    
)
