from django.db import models
from tagging.fields import TagField
from nutsbolts.utils.slugs import *
from tagging.models import Tag
from django.utils import simplejson
import urllib
from django.contrib.auth.models import User
# Create your models here.

# Do categories like gating

class Category(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(editable=False)

    def __unicode__(self):
        return self.name

    def save(self):
        unique_slugify(self, self.name)
        super(Category, self).save()
        
    @models.permalink
    def get_absolute_url(self):
        return ('stegelman.bookmarks.views.category', (), {'category_slug': self.slug})


class Bookmark(models.Model):
    title = models.CharField(max_length=350)
    slug = models.SlugField(editable=False)
    category = models.ForeignKey(Category)
    tags = TagField(help_text='Please use comma seperated values.', blank=True)
    link = models.URLField()
    author = models.ForeignKey(User, editable=False)
    date_created = models.DateField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.title

    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)

    def get_tags(self):
        return Tag.objects.get_for_object(self)

    @models.permalink
    def get_absolute_url(self):
        return self.slug

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(Bookmark, self).save(*args, **kwargs)
        
    class Meta:
        ordering = ['-date_created']
        
def delicious_import():
    feed_source = "http://feeds.delicious.com/v2/json/dstegelman?count=100"
    delicious_open = urllib.urlopen(feed_source)
    delicious_json = delicious_open.read()
    del_json_object = simplejson.loads(delicious_json)
    bkmrk_author = User.objects.get(pk=1)
    bkmrk_category = Category.objects.get(pk=1)
    for bookmark in del_json_object:
        bkmrk = Bookmark(title=bookmark['d'], link=bookmark['u'], author=bkmrk_author, category=bkmrk_category)
        bkmrk.save()
