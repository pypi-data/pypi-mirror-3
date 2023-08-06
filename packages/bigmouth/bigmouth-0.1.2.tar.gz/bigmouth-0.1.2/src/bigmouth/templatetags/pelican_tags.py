
import re

from django import template
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.conf import settings

register = template.Library()

@register.inclusion_tag("bigmouth/ttags/article.html", takes_context=True)
def render_article(context):
    """
    """
    return {
        'article': context['article'],
        'SITEURL': context['SITEURL'],
    }

@register.inclusion_tag("bigmouth/ttags/article_summary.html", takes_context=True)
def render_article_summary(context):
    """
    """
    article = context['article']
    has_more = len(article.content) > len(article.summary)
    return {
        'article': article,
        'SITEURL': context['SITEURL'],
        'has_more': has_more,
    }

@register.inclusion_tag("bigmouth/ttags/article_infos.html", takes_context=True)
def render_article_infos(context):
    """
    Article date, author
    """
    return {
        'article': context['article'],
        'SITEURL': context['SITEURL'],
    }

@register.inclusion_tag("bigmouth/ttags/article_tags.html", takes_context=True)
def render_article_tags(context):
    """
    An article's tags.
    """
    try:
        tags = context['article'].tags
    except AttributeError:
        tags = []
    return {
        'tags': tags,
        'SITEURL': context['SITEURL'],
    }

@register.inclusion_tag("bigmouth/ttags/article_list.html", takes_context=True)
def render_article_list(context):
    """
    """
    return {
        'article': context['article'],
        'SITEURL': context['SITEURL'],
    }

@register.inclusion_tag("bigmouth/ttags/article_summary_list.html", takes_context=True)
def render_article_summary_list(context):
    """
    """
    return {
        'articles': context['articles_page'].object_list,
        'SITEURL': context['SITEURL'],
    }

def canonical_url(*args):
    """
    >>> assert canonical_url('index.html') == '/'
    >>> assert canonical_url('/index.html') == '/'
    >>> assert canonical_url('http://localhost', '/index.html') == 'http://localhost/'
    >>> assert canonical_url('http://localhost', 'index.html') == 'http://localhost/'
    >>> assert canonical_url('https://localhost', 'index.html') == 'https://localhost/'
    >>> assert canonical_url('/pages', '/index.html') == '/pages/'
    >>> assert canonical_url('pages/', '/index.html') == '/pages/'
    >>> assert canonical_url('/pages/', '/index.html') == '/pages/'
    >>> assert canonical_url('http://localhost', '/pages/', '/index.html') == \
    'http://localhost/pages/'
    >>> assert canonical_url('http://localhost', 'pages/', '/index.html') == \
    'http://localhost/pages/'
    >>> assert canonical_url('http://localhost/', '/pages/', '/index.html') == \
    'http://localhost/pages/'
    >>> assert canonical_url('http://localhost/', 'category', 'code') == \
    'http://localhost/category/code/'
    """
    if not args:
        return '/'
    else:
        parts = list(args)
        parts[-1] = re.sub(
            r'(/index\.html$|index\.html$|\.html$)', '', parts[-1]
        ).rstrip('/')
        #ensure trailing slash
        if parts[-1]:
            parts = parts + ['']
        #ensure leading slash
        while parts:
            if parts[0]:
                break
            parts[:] = parts[1:]
        else:
            parts = ['']
        if not re.search(r'^http://|^https://', parts[0]):
            parts = [''] + parts
        return '/'.join(part.strip('/') for part in parts)

@register.simple_tag
def permalink_for_article(article):
    return canonical_url(settings.SITEURL, article.url)

@register.simple_tag
def permalink_for_page(page):
    return canonical_url(settings.SITEURL, 'pages', page.url)

@register.simple_tag
def permalink_for_category(s):
    return canonical_url(settings.SITEURL, 'category', s)

@register.simple_tag
def permalink_for_tag(s):
    return canonical_url(settings.SITEURL, 'tag', s)

if __name__ == '__main__':
    import doctest
    doctest.testmod()

