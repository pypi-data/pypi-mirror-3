#encoding:utf-8
import re
from django import template
from django.template.defaultfilters import urlize, stringfilter

register = template.Library()

formats = ['jpg', 'gif', 'png']
@stringfilter
def auto_markup(value, autoescape=None):
    if True in [value.endswith(k) for k in formats] :
        return """<img src="%s"></img>""" % (value)
    else :
        return urlize(value, autoescape)
auto_markup.is_safe = True
auto_markup.needs_autoescape = True

class StripWhiteSpacesNode(template.Node):
    """
    Strips leading and trailing whitespaces.
    """
    
    def __init__(self, nodelist):
        self.whitespace = re.compile(r'\s*\n+')
        self.nodelist = nodelist

    def render(self, context):
        return self.whitespace.sub('\n', self.nodelist.render(context))

@register.tag
def stripwhitespaces(parser, token):
    nodelist = parser.parse(('endstripwhitespaces',))
    parser.delete_first_token()
    return StripWhiteSpacesNode(nodelist)

register.filter(auto_markup)
