"""
Decorators and utility functions to integrate fresco apps with the Genshi
templating system.
"""

import os
from functools import wraps
from collections import Mapping

from genshi.template.loader import TemplateLoader, TemplateNotFound
from genshi.template.base import Template
from genshi.template.text import NewTextTemplate as TextTemplate
from genshi.filters import HTMLFormFiller

from fresco import FrescoApp, Route, GET, context, urlfor
from fresco import Response
from fresco.exceptions import NotFound
from fresco.routing import MatchAllURLsPattern

from fresco.util.urls import normpath as url_normpath

__version__ = '0.2'
__all__ = 'GenshiRender', 'select', 'formfilled', 'GenshiDirectoryView',\
          'genshi_app_factory'


def _make_decorator(render_method, template, *args, **kwargs):
    """
    Return a decorator wrapping a function so that its return value is passed
    as the data paramter to ``render_method``
    """
    def decorator(func):

        @wraps(func)
        def decorated(*fargs, **fkwargs):
            data = func(*fargs, **fkwargs)
            if template is None:
                try:
                    local_template, data = data
                except (TypeError, ValueError):
                    return data
            else:
                local_template = template
            if data is None:
                data = {}

            # Pass through any response that is not a mapping
            if not isinstance(data, Mapping):
                return data

            return render_method(
                local_template,
                data, _in_decorator=True,
                *args, **kwargs
            )
        return decorated
    return decorator


class TemplateContent(object):
    """
    Wrap a genshi rendering information (template, template vars, filters etc)
    so that it can be used as a WSGI response iterator.

    The template is not rendered until the WSGI response is iterated, giving
    downstream functions a chance to modify the templated response, eg by
    injecting new template variables.
    """

    def __init__(self, renderer, template, template_vars, filters, cls,
                 serializer='xhtml'):

        #: GenshiRender instance
        self.renderer = renderer

        #: Template filename
        self.template = template

        #: Vars passed into template rendering context
        self.template_vars = template_vars

        #: Genshi stream filters
        self.filters = filters or []

        #: Template class used
        self.cls = cls

        #: Serializer to use (eg 'xhtml')
        self.serializer = serializer

    def stream(self):
        """
        Return the rendered template as a Genshi stream
        """
        stream = self.renderer.as_stream(self.template,  self.template_vars)
        for f in self.filters:
            stream = stream.filter(f)
        return stream

    def __iter__(self):
        """
        Return the rendered template as a string
        """
        return iter([self.stream().render(self.serializer)])


class GenshiRender(object):
    """
    A GenshiRender instance provides decorators and functions for rendering
    Genshi templates to fresco Response objects or to strings.

    There are methods to render using both Genshi's MarkupTemplate or
    TextTemplate, and to return the result as a string, a genshi stream, or a
    response object.

    This example shows the class being used as a decorator. Calling ``myfunc``
    will return a fresco.response.Response object to be returned with the
    contents of 'page.html' rendered with the variables provided in the return
    value of ``myfunc``::

        >>> render = GenshiRender(relative_to=__file__)
        >>> @render('page.html') #doctest: +SKIP
        ... def myfunc():
        ...     return {'x': 'foo', 'y': 'bar'}
        ...

    Instead of rendering a response object directly it's also possible to
    simply return the rendered value as string::

        >>> @render.as_string('page.html') #doctest: +SKIP
        ... def myfunc():
        ...     return {'x': 'foo', 'y': 'bar'}
        ...

    For rapid prototyping, it's also possible to render function docstrings as
    Genshi templates::

        >>> @render.docstring()
        ... def myfunc():
        ...    '''
        ...    <html>
        ...        $foo
        ...    </html>
        ...    '''
        ...    return {'foo': 'bar'}


    Each of the rendering methods can also be called as a regular
    (non-decorator) method, for example::

        >>> render.as_string('page.html', {'foo': 'bar'}) #doctest: +SKIP

    """

    #: Variables accessible from Genshi templates
    _default_vars = {
        'context': context,
        'urlfor': urlfor,
    }

    def __init__(self, loader=None, default_vars=None, relative_to=None,
                 search_path=None, serializer='xhtml', **kwargs):
        """
        Initialize a GenshiRender object.

        :param loader: A TemplateLoader instance

        :param default_vars: A dictionary of default values to pass to all
                            templates. These values will be merged with the
                            returned dictionaries from decorated methods. This
                            can also be a callable, in which case it will be
                            called every time a template is rendered to
                            generate the default dictionary of template
                            variables.

        :param search_path: The Genshi TemplateLoader search_path.
        :param relative_to: A path temlates are loaded relative to. This will
                            be appended to ``search_path``.
        :param serializer: The Genshi serializer to use, by default ``'xhtml'``
        :param **kwargs: Any other keyword arguments, passed to the
                         TemplateLoader constructor
        """
        search_path = search_path or []
        if relative_to:
            relative_to = os.path.abspath(relative_to)
            if not os.path.isdir(relative_to):
                relative_to = os.path.dirname(relative_to)
            search_path.append(relative_to)
        if not search_path:
            search_path.append('.')
        if loader is None:
            loader = TemplateLoader(search_path, **kwargs)
        self.loader = loader

        self._default_var_sources = [self._default_vars]
        if default_vars is not None:
            self._default_var_sources.append(default_vars)

        self.serializer = serializer

    def add_default_vars(self, *args):
        for varsource in args:
            self._default_var_sources.append(varsource)

    def default_vars(self):
        """
        Merge all template vars into a single dict
        """
        result = {}
        for source in self._default_var_sources:
            if callable(source):
                result.update(source())
            else:
                result.update(source)
        return result

    def as_stream(self, template=None, data=None, filters=None, cls=None,
                  _in_decorator=False):
        """
        Return a Genshi stream for the rendered template
        """
        if data is None and not _in_decorator:
            return _make_decorator(self.as_stream, template, filters, cls)

        ns = self.default_vars()
        ns.update(data)

        if not isinstance(template, Template):
            template = self.loader.load(template, cls=cls)

        stream = template.generate(**ns)
        if filters:
            for item in filters:
                stream = stream.filter(item)
        return stream

    def text_as_stream(self, *args, **kwargs):
        """
        Same as ``as_stream`` but use a Genshi TextTemplate
        """
        return self.as_stream(cls=TextTemplate, *args, **kwargs)

    def as_string(self, template=None, data=None, serializer=None,
                  filters=None, cls=None, _in_decorator=False):
        """
        Return the string output of the rendered template.
        Can also work as a function decorator
        """
        serializer = serializer if serializer else self.serializer
        if data is None and not _in_decorator:
            return _make_decorator(self.as_string, template, serializer,
                                   filters, cls)
        return self.as_stream(template, data, filters, cls)\
                   .render(serializer, encoding=None)

    def text_as_string(self, *args, **kwargs):
        """
        Same as ``as_string`` but use a Genshi TextTemplate and text serializer
        """
        return self.as_string(cls=TextTemplate, serializer='text', *args,
                              **kwargs)

    def as_response(self, template=None, data=None, serializer=None,
                    filters=None, cls=None, _in_decorator=False,
                    **response_kwargs):
        """
        Return a response object for the rendered template::

            >>> render = GenshiRender(TemplateLoader(['.']))
            >>> response = render.as_response('my_template.html',
            ...                               {'foo': 'bar'}) #doctest: +SKIP

        Can also be used as a decorator. The decorated function will merge the
        original function's return value (a dict) with the specified template::

            >>> render = GenshiRender(TemplateLoader(['.']))
            >>>
            >>> @render.as_response('my_template.html') #doctest: +SKIP
            ... def handler(request):
            ...     return {'foo': 'bar'}
            ...
        """
        serializer = serializer if serializer else self.serializer
        if data is None and not _in_decorator:
            return _make_decorator(self.as_response, template, serializer,
                                   filters, cls, **response_kwargs)

        return Response(TemplateContent(self, template, data, filters, cls,
                                        serializer), **response_kwargs)

    __call__ = as_response

    def text_as_response(self, *args, **kwargs):
        """
        Same as ``as_string`` but use a Genshi TextTemplate and text serializer
        """
        return self.as_string(cls=TextTemplate, serializer='text',
                              *args, **kwargs)

    def docstring(self, serializer=None, filters=None, cls=None,
                  **response_kwargs):
        """
        Render the function's docstring as a genshi template stream::

            >>> render = GenshiRender()
            >>> @render.docstring()
            ... def myhandler(request):
            ...     '''
            ...     <html>
            ...         $foo
            ...     </html>
            ...     '''
            ...     return {'foo': 'bar'}
        """
        serializer = serializer if serializer else self.serializer

        def docstring(func):
            template = (cls or self.loader.default_class)(
                func.func_doc,
                loader=self.loader,
            )
            return _make_decorator(self.as_response, template, serializer,
                                   filters, **response_kwargs)(func)
        return docstring

    def docstring_as_string(self, serializer=None, filters=None, cls=None,
                            **response_kwargs):
        """
        Render the function's docstring as a genshi template stream::

            >>> render = GenshiRender()
            >>> @render.docstring_as_string()
            ... def myfunc():
            ...     '''
            ...     <html>
            ...         $foo
            ...     </html>
            ...     '''
            ...     return {'foo': 'bar'}
        """
        serializer = serializer if serializer else self.serializer

        def docstring(func):
            template = (cls or self.loader.default_class)(
                func.func_doc,
                loader=self.loader,
            )
            return _make_decorator(self.as_string, template, serializer,
                                   filters, **response_kwargs)(func)
        return docstring


def select(path):
    """
    Take a function emitting a genshi stream and apply an XPATH select to it to
    filter out all but the selected elements, eg::

        >>> render = GenshiRender()
        >>> @select("//p[@id='content']")
        ... @render.docstring()
        ... def myfunc():
        ...     '''
        ...     <html>
        ...         <h1>Welcome to $foo!</h1>
        ...         <p id="content">$foo</p>
        ...     </html>
        ...     '''
        ...     return {'foo': 'bar'}
        ...
        >>> list(myfunc().content)
        ['<p id="content">bar</p>']
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            result = func(*args, **kwargs)
            if not isinstance(result, Response):
                return result
            result.content.filters.append(lambda stream: stream.select(path))
            return result
        return decorated
    return decorator


def formfilled(defaults=None, form_id=None, form_name=None, source='form',
               **kwdefaults):
    """
    Apply the genshi ``HTMLFormFiller`` filter to a genshi stream, populating
    form fields from the request object or other specified defaults.

    :param defaults: dictionary of default form values, or any callable
                     returning a dictionary
    :param form_id: HTML id attribute of the form
    :param form_name: HTML name attribute of the form
    :param source: Name of the data source on the request object, ie ``form``
                   (for ``request.form``) or ``query`` (for ``request.query``).
    :param **kwdefaults: Default values passed as keyword arguments
    """

    if defaults is None:
        defaults = {}

    def formfilled(func):
        @wraps(func)
        def formfilled(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                filters = result.content.filters
            except AttributeError:
                return result
            data = {}
            _defaults = defaults() if callable(defaults) else defaults
            _defaults.update(kwdefaults)
            for item, default in _defaults.items():
                data[item] = default() if callable(default) else default
            source_ob = getattr(context.request, source)
            for k in source_ob.keys():
                l = source_ob.getlist(k)
                if len(l) == 1:
                    data[k] = l[0]
                else:
                    data[k] = l
            filters.append(HTMLFormFiller(name=form_name,
                                          id=form_id, data=data))
            return result
        return formfilled
    return formfilled


class GenshiDirectoryView(object):
    """
    Return a WSGI application serving genshi templated HTML pages.

    Example::

        >>> from wsgiref.simple_server import make_server
        >>> render = GenshiRender(TemplateLoader(['path/to/document/root']))
        >>> app = GenshiDirectoryView(render)
        >>> make_server('', 8000, app).serve_forever() #doctest: +SKIP
    """

    __routes__ = [Route(MatchAllURLsPattern('/'), GET, 'view')]

    def __init__(self, renderer):
        self.renderer = renderer
        (self.document_root,) = renderer.loader.search_path

    def view(self, request):
        load = self.renderer.loader.load
        path = request.path_info
        template_path = url_normpath(path)
        while template_path and template_path[0] == '/':
            template_path = template_path[1:]

        fs_path = os.path.join(*template_path.split('/'))

        try:
            template = load(fs_path)
        except TemplateNotFound:
            if os.path.isdir(os.path.join(self.document_root, fs_path)):
                if template_path != "" and not template_path.endswith('/'):
                    redirect = '/' + template_path + '/'
                    if request.script_name != '':
                        redirect = request.script_name + redirect
                    return Response.redirect(redirect, status=302)
            try:
                template = load(os.path.join(fs_path, 'index.html'))
            except TemplateNotFound:
                raise NotFound()

        return self.renderer.as_response(template, {})


def genshi_app_factory(config, document_root, serializer='xhtml',
                       auto_reload=True):
    """
    Return a WSGI app serving Genshi templated pages from a filesystem
    directory.
    """
    return FrescoApp(
        GenshiDirectoryView(
            GenshiRender(
                TemplateLoader([document_root]),
                serializer=serializer
            )
        )
    )
