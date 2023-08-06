#encoding:utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

"""
This module provides decorators useful to :

(i) render templates from a context
(ii) memorise the last visited and rendered page to use it as a background 
"""

def render_to(template_name):
    """Decorator that do template rendering from a context dictionary."""
    def renderer(func):
        def wrapper(request, dictionary=None, context_instance=None):
            print func.func_name, request
            output = func(request, dictionary, context_instance)
            if isinstance(output, RequestContext) :
                context = output
            elif isinstance(output, dict) : 
                context = RequestContext(request, output)
            else :
                raise NotImplementedError("this decorator works with context defined as a dictionary or a RequestContext")
            return render_to_response(request, template_name, context)
        return wrapper
    return renderer

def memorise_last_page(view_func):
    """Memorise in the user session the last accessed page before entering in a view."""
    def modified_function(request, *args, **kwargs):
        request.session['last_page'] = request.build_absolute_uri()
        request.session.modified = True
        return view_func(request, *args, **kwargs)
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def memorise_last_rendered_page(view_func):
    """Memorise in the user session the last rendered page returned by a response."""
    def modified_function(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        request.session['background_page'] = response._container[0]
        request.session.modified = True
        return response
    modified_function.__doc__ = view_func.__doc__
    return modified_function

def check_rendered_page(view_func):
    """
    Update the last memorised page and its relative
    rendered_page in order to cope browser forward and
    backward buttons that skip the memorisation process.
    """
    
    def modified_function(request, *args, **kwargs):
        raise NotImplementedError()
        new = request.META['HTTP_REFERER']
        memo = request.session['last_page']
        
        if new != memo :
            request.session['last_page'] = request.META['HTTP_REFERER']
            redirection = HttpResponseRedirect(request.META['HTTP_REFERER']) 
            request.session['background_page'] = redirection._container[0]
            request.session.modified = True
        return view_func(request, *args, **kwargs)
    modified_function.__doc__ = view_func.__doc__
    return modified_function
    
    return view_func
