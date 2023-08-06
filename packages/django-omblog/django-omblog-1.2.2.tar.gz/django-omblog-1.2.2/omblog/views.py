import datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from omblog import settings
from omblog.decorators import cache_page, login_required
from omblog.models import Post, Tag
from omblog import settings as om_settings

def login(request):
    """Authenticates a user and logs them in"""


@login_required
def edit(request, pk):
    # get the post
    get_object_or_404(Post, pk=pk)
    # 
    return render_to_response('omblog/edit.html', {
        'post': post,
    },
    context_instance=RequestContext(request))


@cache_page
def tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.visible(user=request.user)
    posts = posts.filter(tags=tag)
    
    return render_to_response('omblog/tags.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
        'tag': tag
    },
    context_instance=RequestContext(request))

@cache_page
def index(request):
    """The index"""
    posts = Post.objects.visible(user=request.user)
    if posts.count() > om_settings.INDEX_ITEMS:
        posts = posts[:om_settings.INDEX_ITEMS]
    return render_to_response('omblog/index.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
    },
    context_instance=RequestContext(request))

@cache_page
def month(request, year, month):
    """The month archive"""
    date = datetime.date(year=int(year), month=int(month), day=1)
    posts = Post.objects.visible(user=request.user).filter(
                                    created__year=year,
                                    created__month=month)

    return render_to_response('omblog/month.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
        'date': date
    },
    context_instance=RequestContext(request))


@cache_page
def post(request, slug):
    """view post"""
    try:
        post = Post.objects.visible(user=request.user).select_related('tags').get(slug=slug)
    except Post.DoesNotExist:
        raise Http404
    return render_to_response('omblog/post.html', {
        'post': post,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
    },
    context_instance=RequestContext(request))

