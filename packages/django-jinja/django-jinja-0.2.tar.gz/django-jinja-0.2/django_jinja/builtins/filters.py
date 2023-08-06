# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse as django_reverse

def reverse(value, *args, **kwargs):
    """
    Shortcut filter for reverse url on templates. Is a alternative to
    django {% url %} tag, but more simple.

    Usage example:
        {{ 'web:timeline'|reverse(userid=2) }}

    This is a equivalent to django: 
        {% url 'web:timeline' userid=2 %}

    """
    return django_reverse(value, args=args, kwargs=kwargs)
