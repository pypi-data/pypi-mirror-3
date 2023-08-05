from django.db import models
from django.contrib.auth.models import User
from nutsbolts.utils.slugs import unique_slugify
# Import Tagging
from tagging.fields import TagField
from tagging.models import Tag
from xml.etree import ElementTree
# For use with model managers.
from django.db.models.query import QuerySet
from django.template.defaultfilters import truncatewords_html
from newsfeed.models import Location
import twitter
import string
from django.http import HttpResponse

'''
    Define model managers here.

'''

class PostMixin(object):
    def by_author(self, user):
        return self.filter(user=user)

    def published(self):
        return self.filter(published=True)
    
    def by_category(self, category_slug):
        return self.filter(category__slug=category_slug)

class PostQuerySet(QuerySet, PostMixin):
    pass

class PostManager(models.Manager, PostMixin):
    def get_query_set(self):
        return PostQuerySet(self.model, using=self._db)


class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(editable=False)
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('blog.views.category', (), {'category_slug': self.slug})
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Category, self).save(*args, **kwargs)

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(editable=False)
    author = models.ForeignKey(User, editable=False)
    content = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, editable=False, null=True)
    tags = TagField()
    category = models.ForeignKey(Category, blank=True, null=True)
    published_date = models.DateField(auto_now=True, auto_now_add=True)
    location = models.ForeignKey(Location)
    image = models.ImageField(upload_to="blog", blank=True, null=True)
    
    
    published = models.BooleanField()
    objects = PostManager()
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('blog.views.post', (), {'post_slug': self.slug})
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        self.summary = truncatewords_html(self.content, 40)
        super(Post, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-id']
        
    
    '''
        Include your object (single instance) methods here.  Methods for multiple objects
        should be included in the object manager at the top of the module.
    
    '''
    
class Status(models.Model):
    tweet = models.CharField(max_length=250)
    twitter_id = models.BigIntegerField()
    created_at = models.CharField(max_length=200)
    location = models.ForeignKey(Location)
    
    def __unicode__(self):
        return self.tweet
    
    class Meta:
        ordering = ['-twitter_id']
    
def post_sync():
    tree = ElementTree.parse("/home/dstegelman/webapps/cookbook_django/htdocs/apps/stegelman/blog/wordpress.xml")
    category = Category(name="uncategorized")
    category.save()
    content_ns = '{http://purl.org/rss/1.0/modules/content/}'
    for item in tree.findall("channel/item"):
        post = Post(title=item.find("title").text)
        #post.content = item.find("{http://purl.org/rss/1.0/modules/content/}encoded").text
        post.content = item.find(content_ns + 'encoded').text
        post.published = True
        post.published_date = item.find("pubDate").text
        user = User.objects.get(pk=1)
        post.author = user
        post.category = category
        post.save()
        
def status_sync():
    from django.contrib.localflavor.us import us_states
    twitter_api = twitter.Api()
    try:
        statuses = twitter_api.GetUserTimeline("derekstegelman")
    except:
        pass
        return HttpResponse("ok", mimetype="text/plain")
    for tweets in statuses:
        try:
            get_status = Status.objects.get(twitter_id=tweets.id)
        except Status.DoesNotExist:
            new_tweet = Status(tweet=tweets.text)
            new_tweet.twitter_id = tweets.id
            new_tweet.created_at = tweets.created_at
            try:
                try:
                    if tweets.place["place_type"] == "city":
                        loc = Location.objects.get(city=tweets.place["name"])
                    else:
                        loc = Location.objects.get(pk=1)
                except Location.DoesNotExist:
                    loc = Location(city=tweets.place["name"])
                    loc.country = tweets.place["country"]
                    loc.save()
                
            except:
                loc = Location.objects.get(pk=1)
                
                pass
            new_tweet.location = loc
            new_tweet.save()
    
