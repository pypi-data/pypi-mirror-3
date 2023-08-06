#encoding:utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page

@memorise_last_page
@memorise_last_rendered_page
def home(request, template):
    """Return the homepage of the website."""
    response = render_to_response(template, RequestContext(request, {'user':request.user}))
    return response

def project_url(request):
    return "fake url"
