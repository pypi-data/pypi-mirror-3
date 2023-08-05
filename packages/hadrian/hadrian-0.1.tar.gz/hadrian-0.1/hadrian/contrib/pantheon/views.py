# Below are some common methods/functions used in my views.
from django.utils import simplejson
import urllib
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.simple import direct_to_template
# Import your models.
from blog.models import *
# Import forms
from blog.forms import PostForm, ContactForm
# Import tagging stuff if you are using the tagging module. Remove if not.
from tagging.models import Tag, TaggedItem
# Authentication stuff.  This is a handly decorator used to force a user to login.
from django.contrib.auth.decorators import login_required
from brew.models import Beer
from newsfeed.models import Location
from django.core.mail import send_mail
import twitter
from multimedia.models import Photo
#https://github.com/api/v2/json/repos/show/dstegelman


'''
    The following are a few random views that you can use.  

'''

def post(request, post_slug):
    context = {'post': get_object_or_404(Post, slug=post_slug, published=True)}
    return render(request, 'blog/post.html', context)
   


def sync(request):
    yo = post_sync()
    return redirect("home")

def home(request):
    context = {'posts': Post.objects.published()[:2]}
    #context['beers'] = Beer.objects.featured()[:2]
    context['photos'] = Photo.objects.all()[:6]
    try:
        repo_data = urllib.urlopen("https://github.com/api/v2/json/repos/show/dstegelman")
        repo_json = repo_data.read()
        context['repos'] = simplejson.loads(repo_json)['repositories']
    except:
        pass
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            send_mail(name + ' submitted a contact form', form.cleaned_data['message'], from_email,
    ['dstegelman@gmail.com'], fail_silently=False)
            return redirect("/")
    else:
        form = ContactForm()
        context['form'] = form
    return render(request, 'blog/home.html', context)

def posts(request):
    blog_posts = Post.objects.published()
    # Set up the paginator with how many objects you want to limit each page to.
    paginator = Paginator(blog_posts, 4)
    # Get the page paramter to decide what page you want.  Default is set to the first page.
    page = request.GET.get('page', 1)
    try:
        context = {'blog_posts': paginator.page(page)}
    except PageNotAnInteger:
        context = {'blog_posts': paginator.page(1)}
    except EmptyPage:
        context = {'blog_posts': paginator.page(paginator.num_pages)}
    '''
     Its important to note that when the view sends the blog_posts objects back you have to extract the actual objects
     using the object_list.  So to loop through blog posts in the template, it would be like this::
     
     {% for post in blog_posts.object_list %}
    
    '''
    return render(request, 'blog/index.html', context)


def tag(request, tag_slug):
    query_tag = Tag.objects.get(slug=tag_slug)
    blog_posts = TaggedItem.objects.get_by_model(Post, query_tag)
    paginator = Paginator(blog_posts, 4)
    page = request.GET.get('page', 1)
    try:
        context = {'blog_posts': paginator.page(page)}
    except PageNotAnInteger:
        context = {'blog_posts': paginator.page(1)}
    except EmptyPage:
        context = {'blog_posts': paginator.page(paginator.num_pages)}
    
    return render(request, 'blog/index.html', context)


def category_list(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    context = {'blog_posts': Post.objects.published().by_category(category_slug), 'category':category.name}
    return render(request, 'blog/category.html', context)
    
def category(request, category_slug):
    blog_posts = Post.objects.published().by_category(category_slug)
    paginator = Paginator(blog_posts, 4)
    page = request.GET.get('page', 1)
    try:
        context = {'blog_posts': paginator.page(page)}
    except PageNotAnInteger:
        context = {'blog_posts': paginator.page(1)}
    except EmptyPage:
        context = {'blog_posts': paginator.page(paginator.num_pages)}
    return render(request, 'blog/index.html', context)

def twitter_feed(request):
    #twitter_api = twitter.Api()
    #context = {'statuses': twitter_api.GetUserTimeline("derekstegelman")}
    context = {'statuses': Status.objects.all()[:20]}
    return render(request, 'blog/status.html', context)
    
def twitter_sync(request):
    status_sync()
    return redirect("twitter_feed")