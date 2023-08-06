#encoding:utf-8
import random
from django import template

register = template.Library()

def multiply(value, arg):
    return value * arg

class RandomizeNode(template.Node):
    
    def __init__(self, mn, mx):
        self.min = int(mn)
        self.max = int(mx)
    
    def render(self, context):
        return str(round(random.random()*random.randint(self.min, self.max), 2))

def do_randomization(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, min, max = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires min and max arguments" % token.contents.split()[0]
#    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
#        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return RandomizeNode(min, max)

register.filter('multiply', multiply)
register.tag('randomize', do_randomization)
