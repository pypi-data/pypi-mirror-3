from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from ccgallery import settings as c_settings
try:
    import textile
except ImportError:
    pass

try:
    import markdown
except ImportError:
    pass

register = template.Library()

@register.inclusion_tag('ccgallery/_js.html')
def gallery_js():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccgallery/_css.html')
def gallery_css():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }


@register.filter
def markup(text):
    """output the description according to whatever markup
    language is set in the settings"""
    html = ''
    if c_settings.MARKUP_LANGUAGE == 'textile':
        html = textile.textile(text)

    if c_settings.MARKUP_LANGUAGE == 'markdown':
        html = markdown.markdown(text)

    return mark_safe(html)
