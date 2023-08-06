# Copyright 2009 Tim Savage <tim.savage@poweredbypenguins.org>
# Licensed under the terms of the BSD License (see LICENSE)
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.forms import BaseForm
from django.utils.datastructures import SortedDict
from django.utils.encoding import force_unicode
from django.utils.functional import Promise
from django.utils.translation import ugettext as _
from ajax_forms.ajax_fields import factory as field_factory

__all__ = ('form_to_json', )

class LazyEncoder(DjangoJSONEncoder):
    """
    Encoder that lazily converts to unicode.
    """
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_unicode(obj)
        return obj

json_serializer = LazyEncoder()

def _create_cache_key(form):
    """
    Generate a cache key based on the form.
    """
    cls = form.__class__
    return 'ajax_forms:' + cls.__module__ + '.' + cls.__name__

def form_to_json(form):
    """
    Create a JSON summary of a form for use by client side validation.
    """
    if not isinstance(form, BaseForm):
        raise TypeError(_("Expected Django Form instance"))

    # Check cache first
    result = getattr(form.__class__, '_json', None)
    if result:
        return result   
    
    ajax_directives = getattr(form, 'Ajax', None)

    # Generate ajax fields
    exclude_fields = getattr(ajax_directives, 'exclude_fields', [])
    ajax_fields = SortedDict()
    for field in form:
        html_name = field.html_name
        name = field.name
        field = field.field
        if name in exclude_fields:
            continue
        # If field supplies it's own info use that
        if hasattr(field, 'to_ajax'):
            ajax_fields[html_name] = field.to_ajax()
        else:
            ajax_field = field_factory(field)
            ajax_fields[html_name] = ajax_field.to_ajax()

    # Add ajax callbacks
    #~ callback_url = getattr(ajax_directives, 'callback_url', '')
    #~ for callback_field in getattr(ajax_directives, 'callback_fields', []):
        #~ try:
            #~ ajax_fields[callback_field]['callback'] = callback_url
        #~ except KeyError:
            #~ raise Exception(_('Field "%s" not found in this form') % name)

    # Add additional rules
    for name, rules in getattr(ajax_directives, 'rules', []):
        html_name = form.add_prefix(name)
        try:
            # HACK: This rules parameter requires a prefix
            if rules.has_key('equal_to_field'):
                rules['equal_to_field'] = form.add_prefix(rules['equal_to_field'])
            ajax_fields[html_name].setdefault('rules', {}).update(rules)
        except KeyError:
            raise Exception(_('Field "%s" not found in this form') % name)

    # Add additional messages
    for name, messages in getattr(ajax_directives, 'messages', []):
        html_name = form.add_prefix(name)
        try:
            ajax_fields[html_name].setdefault('msgs', {}).update(messages)
        except KeyError:
            raise Exception(_('Field "%s" not found in this form') % name)

    # Generate result and store in cache
    result = json_serializer.encode(ajax_fields)
    setattr(form.__class__, '_json', result)
    return result
