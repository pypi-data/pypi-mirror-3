from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def bootstrap_script(name):
    return '<script src="%sdjungle/bootstrap/js/bootstrap-%s.js"></script>' % \
            (settings.STATIC_URL, name)

@register.simple_tag
def bootstrap_stylesheet(name=''):
    if name != '' and not name.startswith('-'):
        name = '-%s' % name
    
    return \
        '<link rel="stylesheet" type="text/css" ' + \
        'href="%sdjungle/bootstrap/css/bootstrap%s.css"/>' % \
        (settings.STATIC_URL, name)
