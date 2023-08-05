from django.forms import ModelForm
from bookmarks.models import *

class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
