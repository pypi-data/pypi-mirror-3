from django.shortcuts import render, redirect
from bookmarks.models import *
from django.contrib.auth.models import User
from bookmarks.forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout
from tagging.models import Tag, TaggedItem


def get_common():
    context = {'categories': Category.objects.all()}
    return context

def sync(request):
    
    delicious_import()
    return render(request, 'multimedia/test.html')


def user_bookmarks(request, username):
    user = User.objects.get(username=username)
    context = get_common()
    context['bookmarks'] = Bookmark.objects.filter(author=user)
    
    return render(request, 'bookmarks/user_bookmarks.html', context)

def delete(request, slug):
    bkmrk = Bookmark.objects.get(slug=slug)
    bkmrk.delete()
    return redirect('user_bookmarks', username=request.user.username)

def edit(request, slug):
    bkmrk = Bookmark.objects.get(slug=slug)
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bkmrk)
        if form.is_valid():
            sub_bkmrk = form.save(commit=False)
            sub_bkmrk.author = request.user
            sub_bkmrk.save()
            return redirect('user_bookmarks', username=request.user.username)
    else:
        form = BookmarkForm(instance=bkmrk)
    context = {}
    context['form'] = form
    return render(request, 'bookmarks/save_bookmark.html', context)

def tag(request, tag_slug):
    query_tag = Tag.objects.get(slug=tag_slug)
    bkmrks = TaggedItem.objects.get_by_model(Bookmark, query_tag)
    context = {'bookmarks': bkmrks}
    return render(request, 'bookmarks/index.html', context)

def category(request, category_slug):
    context = get_common()
    bkmrks = Bookmark.objects.filter(category__slug=category_slug)
    context['bookmarks'] = bkmrks
    return render(request, 'bookmarks/index.html', context)
def save_bookmark(request):
    if request.method == "POST":
        form = BookmarkForm(request.POST)
        
        if form.is_valid():
            bkmrk = form.save(commit=False)
            bkmrk.author = request.user
            bkmrk.save()
            return redirect('user_bookmarks', username=request.user.username)
    else:
        form = BookmarkForm()
    context = {}
    context['form'] = form
    return render(request, 'bookmarks/save_bookmark.html', context)

def homepage(request):
    context = {}
    context['bookmarks'] = Bookmark.objects.all()
    return render(request, 'bookmarks/index.html', context)

def logout_view(request):
    logout(request)
    return redirect('homepage')


def tags(request):
    return render(request, 'bookmarks/user_bookmarks.html')