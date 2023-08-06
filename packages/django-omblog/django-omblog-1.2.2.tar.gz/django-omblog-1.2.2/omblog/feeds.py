from django.contrib.syndication.views import Feed
from omblog.models import Post
from omblog import settings

class PostFeed(Feed):
    title = settings.RSS_TITLE
    link = settings.RSS_LINK 

    def items(self):
        return Post.objects.published()[:20]
