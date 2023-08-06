from django import template
from django.conf import settings
from ccstraps.models import Strap

register = template.Library()

@register.inclusion_tag('ccstraps/_css.html')
def strap_css():
    return {
        'STATIC_URL': settings.STATIC_URL}

@register.inclusion_tag('ccstraps/_js.html')
def strap_js():
    return {
        'STATIC_URL': settings.STATIC_URL}

@register.inclusion_tag('ccstraps/_render.html')
def render_strap(strap, *classes):
    try:
        strap = Strap.objects.get(name=strap)
    except Strap.DoesNotExist:
        strap = None
    return {
        'strap': strap,
        'classes': classes}

class StrapNode(template.Node):

    def __init__(self, name, var):
        self.name = name
        self.var = var

    def render(self, context):
        try:
            strap = Strap.objects.get(name=self.name)
        except Strap.DoesNotExist:
            strap = None
        context[self.var] = strap
        return ''

@register.tag
def get_strap(parser, token):
    bits = token.contents.split()
    name = bits[1]
    var = bits.pop()
    return StrapNode(name, var)
