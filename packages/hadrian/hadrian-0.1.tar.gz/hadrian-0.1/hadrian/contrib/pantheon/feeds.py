from django.contrib.syndication.views import Feed
# Import your models.
from blog.models import *

class BlogFeed(Feed):
    title = "Derek.Stegelman.Com Blog Posts"
    link = "/posts/"
    description = "RSS Feed from derek.stegelman.com"
    
    def items(self):
        return Post.objects.published()[:5]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.content


    