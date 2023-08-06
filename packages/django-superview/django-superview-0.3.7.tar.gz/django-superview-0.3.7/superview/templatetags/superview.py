# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe
from ..utils import LazyEncoder

import types, json

register = template.Library()

@register.simple_tag(takes_context=True, name='call_view_method')
def call_view_method(context, method_name, *args, **kwargs):
    view = context['view']
    default_method = lambda x, *args, **kwargs: ''

    view.current_context = context
    method_response = getattr(view, method_name, default_method)(*args, **kwargs)
    del view.current_context

    return method_response


@register.simple_tag(name="as_json")
def as_json(data):
    if isinstance(data, types.GeneratorType):
        data = tuple(data)
    json_data = json.dumps(data, cls=LazyEncoder)
    return mark_safe(json_data)
