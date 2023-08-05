from django.conf.urls.defaults import patterns, include, url
# Uncomment the next two lines to enable the admin:
from bookmarks.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opencookbook.views.home', name='home'),
    # url(r'^opencookbook/', include('opencookbook.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', homepage, name="homepage"),
    url(r'^bookmarks/(?P<username>[-\w]+)/$', user_bookmarks, name="user_bookmarks"),
    url(r'^delete/(?P<slug>[-\w]+)/$', delete, name="delete"),
    url(r'^edit/(?P<slug>[-\w]+)/$', edit, name="edit"),
    url(r'^tag/(?P<tag_slug>[-\w]+)/$', tag, name="tag"),
    url(r'^category/(?P<category_slug>[-\w]+)/$', category, name="category"),
    url(r'^tags/$', tags, name="tags"),
    url(r'^save/$', save_bookmark, name="save_bookmark"),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'bookmarks/login.html'}, name="login"),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', logout_view, name="logout"),
    #url(r'^api/', include('bookmarks.api.urls')),
)
