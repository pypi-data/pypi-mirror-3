from datetime import datetime
from django.db import models
from picklefield.fields import PickledObjectField
from omblog import listeners
from omblog import managers


class Tag(models.Model):
    slug = models.SlugField(
                db_index=True)
    tag = models.CharField(
                max_length=255)

    objects = managers.TagManager()

    def __unicode__(self):
        return u'%s' % self.tag

    @models.permalink
    def get_absolute_url(self):
        return ('omblog:tag', (), {
            'slug': self.slug,
        })


class Post(models.Model):
    IDEA = 1
    DRAFT = 2
    PUBLISHED = 3
    HIDDEN = 4
    STATUS_CHOICES = (
        (IDEA, 'Idea'),
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (HIDDEN, 'Hidden'),
    )
    title = models.CharField(
                max_length=255)
    slug = models.SlugField(
                db_index=True,
                unique=True,
                max_length=255)
    description = models.CharField(
                max_length=255,
                blank=True,
                null=True)
    source_content = models.TextField('content')
    rendered_content = models.TextField(
                blank=True,
                null=True)
    status = models.PositiveSmallIntegerField(
                choices=STATUS_CHOICES,
                default=IDEA)
    tags = models.ManyToManyField(
                Tag,
                blank=True,
                null=True)
    created = models.DateTimeField(
                blank=True,
                null=True)

    objects = managers.PostManager()

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return '%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('omblog:post', (), {
            'slug': self.slug,
        })

    def edit_url(self):
        return '/admin/omblog/post/%s/' % self.id

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.now()
        super(Post, self).save(*args, **kwargs)



class PostVersion(models.Model):
    instance = PickledObjectField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s : %s' % (self.instance.title, self.created.strftime('%c'))


models.signals.pre_save.connect(
                listeners.clear_cached_posts,
                sender=Post,
                dispatch_uid='clear_cached_posts')

models.signals.pre_save.connect(
                listeners.post_date,
                sender=Post,
                dispatch_uid='post_date')

models.signals.pre_save.connect(
                listeners.save_version,
                sender=Post,
                dispatch_uid='save_version')

models.signals.pre_save.connect(
                listeners.post_render_content,
                sender=Post,
                dispatch_uid='post_render_content')
