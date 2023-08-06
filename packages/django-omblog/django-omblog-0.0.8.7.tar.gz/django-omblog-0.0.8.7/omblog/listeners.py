import re
import pygments
import markdown
from bs4 import BeautifulSoup
from datetime import datetime
from pygments import lexers, formatters
from django import template
from django.core.urlresolvers import reverse
from django.core.cache import cache
from omblog.cache import get_key


def save_version(sender, instance, **kwargs):
    """Whena post is saved, so is a version of it
    """
    from omblog.models import PostVersion
    v = PostVersion()
    v.instance = instance
    v.save()

def clear_cached_posts(sender, instance, **kwargs):
    """when a model is saved clear the cache on the query and the cache on it's
    rendered page
    
    - archive_dates
    - posts_published
    - posts_idea
    - posts_draft
    - posts_hidden
    - tags_and_counts
    - view post
    - archive month
    - all tags for post
    """
    try:
        saved_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        saved_instance = None
    #
    # TODO: only kill the cache if items have changed .
    # e.g if the description, title, slug has changed nuke the 
    #       index
    #       archive
    #
    kill_list = []
    # dates
    if getattr(saved_instance, 'created', None) != instance.created:
        kill_list.append(get_key('archive_dates'))
        kill_list.append(get_key('month_%s_%s' % (
                        instance.created.year,
                        instance.created.month)))
    try:
        kill_list.append(get_key('month_%s_%s' % (
                        saved_instance.created.year,
                        saved_instance.created.month)))
    except AttributeError:
        pass
    # Just nuke all of the below for now
    kill_list.append(get_key('posts_published'))
    kill_list.append(get_key('posts_idea'))
    kill_list.append(get_key('posts_draft'))
    kill_list.append(get_key('posts_hidden'))
    kill_list.append(get_key('tags_and_counts'))
    kill_list.append(get_key('index_'))
    # always nuke the post
    kill_list.append(get_key('post_%s' % instance.slug ))
    # nuke tags
    try:
        for tag in instance.tags.all():
            kill_list.append(get_key('tag_%s' % tag))
    except ValueError:
        pass
    cache.delete_many(kill_list)


def post_date(sender, instance, **kwargs):
    """add a date to a post object if none is offered"""
    if instance.created is None:
        instance.created = datetime.now()


def post_render_content(sender, instance, **kwargs):
    """render the post content on save.
    Converts all code blocks to syntax highlighted pygments
    """
    content = instance.source_content
    code_regex = re.compile(r'(<code(.*?)</code>)', re.DOTALL)
    code_blocks = []
    for i, m in enumerate(code_regex.finditer(content)):
        code = m.group(0)
        # if there is a lang attribute, use that
        if code.find('lang') > 0:
            soup = BeautifulSoup(code)
            language = soup.code['lang'] 
            # TODO: catch errors here and provide a default lexer
            lexer = lexers.get_lexer_by_name(language)
            # remove the code tags
            code = code.replace('</code>', '')
            code = code.replace('<code>', '')
            code = re.sub('<code(.*?)>', '', code)
            # create the pygmented code with the lexer
            pygmented_string = pygments.highlight(
                    code,
                    lexer,
                    formatters.HtmlFormatter())
            # put the code blocks into the list for processintg later
            code_blocks.append(pygmented_string)
        else:
            # this is for the inline code snippets
            code_blocks.append(code)
        # replace the <code> tags with placeholders that can be used to replace
        content = content.replace(m.string[m.start():m.end()], 'OMCB|%s|OMCB' % i)
    # render the content now that code is out of the way
    # this is very hacky - must find a better way to do it
    c = template.Context({'instance': instance})
    content = '{% load omblog_tags %}' + content
    t = template.Template(content)
    content = t.render(c)
    # replaced placeholders with the actual code
    for i, code in enumerate(code_blocks):
        content = content.replace('<p>OMCB|%s|OMCB</p>' % i, code)
        content = content.replace('OMCB|%s|OMCB' % i, code)
    # do the mark down
    instance.rendered_content = markdown.markdown(content)
