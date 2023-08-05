from django import template
from django.template.loader import render_to_string
from django.db import models

register = template.Library()

class AlohaNode(template.Node):

    def __init__(self, nodelist, obj=None, field_name=None, url=None):
        self.obj = template.Variable(obj) if obj else None
        self.field_name = template.Variable(field_name) if field_name else None
        self.nodelist = nodelist
        self.url = template.Variable(url) if url else None

    def render(self, context):
        inner_content = self.nodelist.render(context)
        if not context['request'].user.is_staff:
            return inner_content

        obj = self.obj.resolve(context) if self.obj else None
        if obj:
            assert isinstance(obj, models.Model), 'The object passed to aloha tag should be a django model'
        field_name = self.field_name.resolve(context) if self.field_name else None
        if field_name:
            assert isinstance(field_name, basestring), 'The field name passed to aloha tag should be a string'

        url = self.url.resolve(context) if self.url else None

        object_name = '%s.%s' % (obj._meta.app_label, obj._meta.object_name) if obj else None

        if obj:
            assert hasattr(obj, 'pk') and obj.pk, 'The model "%s" doesn\'t have a primary key, it cannot be used with aloha tag'
        context.update({
            'post_url': url,
            'object_name': object_name,
            'object_pk': obj.pk if obj else None,
            'field_name': field_name,
            'content': inner_content,
        })
        result = render_to_string('aloha/postform.html', context_instance=context)
        context.pop()
        return result
 

@register.tag('aloha')
def aloha(parser, token):
    """Django aloha main tag

    Use in your templates like this::

    {% load aloha_tags %}

    1. Option one - you want to edit a certain field on a model instance:

    {% aloha my_object_from_the_database 'fieldname_where_text_is' [url_to_save] %}
        {{ my_object_from_the_database.fieldname_where_text_is|safe }}
    {% endaloha %}

    If you want, you can add an optional "url" parameter to do custom
    POST processing. If not provided, aloha.views.save will be used.

    2. Option two - you want to edit arbitrary text, and provide and url to save:

    {% aloha [url_to_save_to] %}
       <p>Place here what you want to edit</p>
    {% endaloha %}
    """

    bits = token.split_contents()

    if len(bits) > 4:
        raise template.TemplateSyntaxError("Aloha tag takes maximum 4 arguments: %s given" % len(bits))

    elif len(bits) <= 2:
        url = bits[1] if len(bits) == 2 else None
        obj, field_name = None, None
    else:
        tag_name, obj, field_name = bits[:3]
        url = bits[3] if len(bits) == 4 else None
    nodelist = parser.parse(('endaloha',))
    parser.delete_first_token()
    return AlohaNode(nodelist, obj, field_name, url)
