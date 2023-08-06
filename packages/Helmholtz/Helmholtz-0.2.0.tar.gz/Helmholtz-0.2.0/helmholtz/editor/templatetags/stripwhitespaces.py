#encoding:utf-8
import re
from django import template
from django.template.defaultfilters import urlize, stringfilter

register = template.Library()

formats = ['jpg', 'gif', 'png']

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
