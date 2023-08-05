# coding: utf-8

"""
    PyLucid plugin tools
    ~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2009-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""


import re

from django import http
from django.conf import settings
from django.contrib import messages
from django.core import urlresolvers
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_protect

from dbpreferences.forms import DBPreferencesBaseForm


class PyLucidDBPreferencesBaseForm(DBPreferencesBaseForm):
    def get_preferences(self, request, lucidtag_kwargs):
        """
        Update the preferences dict with the given kwargs dict.
        Send a staff user feedback if a kwargs key is invalid.
        """
        preferences = super(PyLucidDBPreferencesBaseForm, self).get_preferences()
        if request.user.is_staff:
            for key in lucidtag_kwargs.keys():
                if key not in preferences:
                    messages.info(request,
                        "Keyword argument %r is invalid for lucidTag %r !" % (key, self.Meta.app_label)
                    )
        preferences.update(lucidtag_kwargs)
        return preferences


class PluginGetResolver(object):
    def __init__(self, resolver):
        self.resolver = resolver
    def __call__(self, *args, **kwargs):
        return self.resolver


def _raise_resolve_error(plugin_url_resolver, rest_url):
    tried = [i[0][0][0] for i in plugin_url_resolver.reverse_dict.values()]
#    for key, value in plugin_url_resolver.reverse_dict.values():
#        print key, value

#    tried = [prefix + pattern.regex.pattern.lstrip("^") for pattern in plugin_urlpatterns]
    raise urlresolvers.Resolver404, {'tried': tried, 'path': rest_url + "XXX"}


def call_plugin(request, url_lang_code, prefix_url, rest_url):
    """
    Call a plugin and return the response.
    used for PluginPage
    """
    lang_entry = request.PYLUCID.current_language
    pluginpage = request.PYLUCID.pluginpage
    pagemeta = request.PYLUCID.pagemeta

    # build the url prefix
    # Don't use pagemeta.language.code here, use the real url_lang_code, because of case insensitivity
    url_prefix = "^%s/%s" % (url_lang_code, prefix_url)

    # Get pylucid_project.system.pylucid_plugins instance
    plugin_instance = pluginpage.get_plugin()

    plugin_url_resolver = plugin_instance.get_plugin_url_resolver(
        url_prefix, urls_filename=pluginpage.urls_filename,
    )
    #for key, value in plugin_url_resolver.reverse_dict.items(): print key, value

    # get the plugin view from the complete url
    resolve_url = request.path_info
    result = plugin_url_resolver.resolve(resolve_url)
    if result == None:
        _raise_resolve_error(plugin_url_resolver, resolve_url)

    view_func, view_args, view_kwargs = result

    if "pylucid.views" in view_func.__module__:
        # The url is wrong, it's from PyLucid and we can get a loop!
        # FIXME: How can we better check, if the view is from the plugin and not from PyLucid???
        _raise_resolve_error(plugin_url_resolver, resolve_url)

    merged_url_resolver = plugin_instance.get_merged_url_resolver(
        url_prefix, urls_filename=pluginpage.urls_filename,
    )

    # Patch urlresolvers.get_resolver() function, so only our own resolver with urlpatterns2
    # is active in the plugin. So the plugin can build urls with normal django function and
    # this urls would be prefixed with the current PageTree url.
    old_get_resolver = urlresolvers.get_resolver
    urlresolvers.get_resolver = PluginGetResolver(merged_url_resolver)

    # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
    request.plugin_name = view_func.__module__.split(".", 1)[0] # FIXME: Find a better way!
    request.method_name = view_func.__name__

    csrf_exempt = getattr(view_func, 'csrf_exempt', False)
    if not csrf_exempt:
        view_func = csrf_protect(view_func)

    # Call the view
    response = view_func(request, *view_args, **view_kwargs)

    if csrf_exempt and isinstance(response, HttpResponse):
        response.csrf_exempt = True

    request.plugin_name = None
    request.method_name = None

    # restore the patched function
    urlresolvers.get_resolver = old_get_resolver

    return response


#______________________________________________________________________________
# ContextMiddleware functions

# TODO: Should we use TemplateResponse?
# https://docs.djangoproject.com/en/dev/ref/template-response/ 

TAG_RE = re.compile("<!-- ContextMiddleware (.*?) -->", re.UNICODE)
from django.utils.importlib import import_module
from django.utils.functional import memoize

_middleware_class_cache = {}

def _get_middleware_class(plugin_name):
    plugin_name = plugin_name.encode('ascii') # check non-ASCII strings

    mod_name = "pylucid_plugins.%s.context_middleware" % plugin_name
    module = import_module(mod_name)
    middleware_class = getattr(module, "ContextMiddleware")
    return middleware_class
_get_middleware_class = memoize(_get_middleware_class, _middleware_class_cache, 1)


def context_middleware_request(request):
    """
    get from the template all context middleware plugins and call the request method.
    """
    context = request.PYLUCID.context
    context["context_middlewares"] = {}

    page_template = request.PYLUCID.page_template # page template content

    # FIXME:
    # We render the page here completely, only to get the ContextMiddlewares
    # This seems to be not the best way.
    #
    request._dont_call_lucid_tags = True # Don't render any lucidTags here
    content = page_template.render(context)
    request._dont_call_lucid_tags = False

    plugin_names = TAG_RE.findall(content)

#    messages.debug(request, "Found ContextMiddlewares in content via RE: %r" % plugin_names)

    for plugin_name in plugin_names:
        # Get the middleware class from the plugin
        try:
            middleware_class = _get_middleware_class(plugin_name)
        except ImportError, err:
            messages.error(request, "Can't import context middleware '%s': %s" % (plugin_name, err))
            continue

        # make a instance 
        instance = middleware_class(request, context)
        # Add it to the context
        context["context_middlewares"][plugin_name] = instance
#        messages.debug(request, "Init ContextMiddleware %r" % plugin_name)


def context_middleware_response(request, response):
    """
    replace the context middleware tags in the response, with the plugin render output
    """
    context = request.PYLUCID.context
    context_middlewares = context["context_middlewares"]
    def replace(match):
        plugin_name = match.group(1)
        try:
            middleware_class_instance = context_middlewares[plugin_name]
        except KeyError, err:
            return "[Error: context middleware %r doesn't exist! Existing middlewares are: %r]" % (
                plugin_name, context_middlewares.keys()
            )

        # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
        request.plugin_name = plugin_name
        request.method_name = "ContextMiddleware"

        middleware_response = middleware_class_instance.render()

        request.plugin_name = None
        request.method_name = None

        if middleware_response == None:
            return ""
        elif isinstance(middleware_response, unicode):
            return smart_str(middleware_response, encoding=settings.DEFAULT_CHARSET)
        elif isinstance(middleware_response, str):
            return middleware_response
        elif isinstance(middleware_response, http.HttpResponse):
            return middleware_response.content
        else:
            raise RuntimeError(
                "plugin context middleware render() must return"
                " http.HttpResponse instance or a basestring or None!"
            )

    # FIXME: A HttpResponse allways convert unicode into string. So we need to do that here:
    # Or we say, context render should not return a HttpResponse?
#    from django.utils.encoding import smart_str
#    complete_page = smart_str(complete_page)

    source_content = response.content

    new_content = TAG_RE.sub(replace, source_content)
    response.content = new_content
    return response

