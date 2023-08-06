from os import path
from unittest import TestCase
from functools import wraps

from genshi.template.loader import TemplateNotFound, TemplateLoader
from genshi.template import Template
from genshi.core import Stream

from pesto.testing import MockRequest
from fresco import Response

from fresco import context
from frescoext.genshi import *

testdir = path.dirname(__file__)
testloader = TemplateLoader([path.join(testdir, 'templates')])

render = GenshiRender(testloader)

def getoutput(func, *args, **kwargs):
    context.request = MockRequest(*args, **kwargs).request
    result = func(context.request)
    output = ''.join(result.content)
    for close in result.onclose:
        close()
    return output

class TestRender(object):

    def test_render_uses_loader(self):

        @render('template_with_include.html')
        def test(request):
            return {}
        assert getoutput(test) == '<html><div>t1</div></html>'

    def test_render_as_string_returns_string(self):
        def test():
            return render.as_string('t1.html', {})
        assert test() == '<div>t1</div>', getoutput(test)

    def test_render_as_string_works_as_decorator(self):
        @render.as_string('t1.html')
        def test():
            return {}
        assert test() == '<div>t1</div>', getoutput(test)

    def test_render_as_string_works_as_decorator_with_no_template_arg(self):
        @render.as_string()
        def test():
            return 't1.html', {}
        assert test() == '<div>t1</div>', getoutput(test)

    def test_render_as_response_returns_response(self):
        def test():
            return render.as_response('t1.html', {})
        assert isinstance(test(), Response)
        assert list(test().content) == ['<div>t1</div>']

    def test_render_as_response_works_as_decorator(self):
        @render.as_response('t1.html')
        def test():
            return {}
        assert isinstance(test(), Response)
        assert list(test().content) == ['<div>t1</div>']

    def test_render_as_response_works_as_decorator_with_no_template_arg(self):
        @render.as_response()
        def test():
            return 't1.html', {}
        assert isinstance(test(), Response)
        assert list(test().content) == ['<div>t1</div>']

    def test_render_as_stream_returns_stream(self):
        def test():
            return render.as_stream('t1.html', {})
        assert isinstance(test(), Stream)
        assert test().render('xhtml') == '<div>t1</div>'

    def test_render_as_stream_works_as_decorator(self):
        @render.as_stream('t1.html')
        def test():
            return {}
        assert isinstance(test(), Stream)
        assert test().render('xhtml') == '<div>t1</div>'

    def test_render_as_stream_works_as_decorator_with_no_template_arg(self):
        @render.as_stream()
        def test():
            return 't1.html', {}
        assert isinstance(test(), Stream)
        assert test().render('xhtml') == '<div>t1</div>'

    def test_select(self):

        @select('//div')
        @render.docstring()
        def test(request):
            """
            <html xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="t1.html" /></html>
            """
            return {}
        assert getoutput(test) == '<div>t1</div>'

    def test_non_mapping_return_value_is_passed_through_render_docstring(self):
        @render.docstring()
        def test(request):
            """
            <html></html>
            """
            return "<div>whoa nelly!</div>"

        assert test(None) == "<div>whoa nelly!</div>", test(None)

    def test_non_mapping_return_value_is_passed_through_render(self):

        @render('t1.html')
        def test(request):
            return "<div>whoa nelly!</div>"
        assert test(None) == "<div>whoa nelly!</div>"

class TestFormfilled(object):

    def test_formfilled(self):

        @formfilled(form_name="form1")
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test) == '<html><form name="form1"><input name="a" /></form></html>', getoutput(test)
        print getoutput(test, QUERY_STRING='a=b')
        assert getoutput(test, QUERY_STRING='a=b') == '<html><form name="form1"><input name="a" value="b" /></form></html>'

    def test_formfilled_sets_default(self):

        @formfilled(a='foo')
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test) == '<html><form name="form1"><input name="a" value="foo" /></form></html>'
        assert getoutput(test, QUERY_STRING='a=b') == '<html><form name="form1"><input name="a" value="b" /></form></html>'

    def test_formfilled_sets_callable_default(self):

        @formfilled(a=lambda: 'foo' + 'bar')
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test) == '<html><form name="form1"><input name="a" value="foobar" /></form></html>'
        assert getoutput(test, QUERY_STRING='a=b') == '<html><form name="form1"><input name="a" value="b" /></form></html>'

        @formfilled(defaults=lambda: {'a': 'xyz'})
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test) == '<html><form name="form1"><input name="a" value="xyz" /></form></html>'
        assert getoutput(test, QUERY_STRING='a=b') == '<html><form name="form1"><input name="a" value="b" /></form></html>'

    def test_formfilled_default_called_after_handler_func(self):
        from pesto import currentrequest
        @formfilled(defaults=lambda: currentrequest().environ['app.formvalues'])
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form></html>
            """
            request.environ['app.formvalues'] = {'a': 'hoopy!'}
            return {}

        assert getoutput(test) == '<html><form name="form1"><input name="a" value="hoopy!" /></form></html>'

    def test_formfilled_selected_by_name(self):

        @formfilled(form_name='form2')
        @render.docstring()
        def test(request):
            """
            <html><form name="form1"><input name="a" /></form><form name="form2"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test, QUERY_STRING='a=b') == '<html><form name="form1"><input name="a" /></form><form name="form2"><input name="a" value="b" /></form></html>'

    def test_formfilled_selected_by_id(self):

        @formfilled(form_id='form2')
        @render.docstring()
        def test(request):
            """
            <html><form id="form1"><input name="a" /></form><form id="form2"><input name="a" /></form></html>
            """
            return {}

        assert getoutput(test, QUERY_STRING='a=b') == '<html><form id="form1"><input name="a" /></form><form id="form2"><input name="a" value="b" /></form></html>'

    def test_non_stream_return_value_is_passed_through_formfilled(self):

        @formfilled()
        def test(request):
            return "<div>whoa nelly!</div>"

        assert test(None) == "<div>whoa nelly!</div>"

    def test_response_is_passed_through_render(self):

        @render()
        def test(request):
            return Response.not_found()

        assert isinstance(test(None), Response)
        assert test(None).status_code == 404

class TestFilters(object):

    def test_filter_is_applied(self):

        from genshi.filters import Transformer
        from genshi.builder import tag

        @render.docstring_as_string(filters=[Transformer('//body/em').wrap(tag.p)])
        def test():
            "<html><body><em>some text</em></body></html>"

        assert test() == '<html><body><p><em>some text</em></p></body></html>'

    def test_filters_are_applied_in_order(self):

        from genshi.filters import Transformer
        from genshi.builder import tag

        @render.docstring_as_string(filters=[
            Transformer('//body/em').wrap(tag.p),
            Transformer('//p').prepend('whoa nelly! ')
        ])
        def test():
            "<html><body><em>some text</em></body></html>"

        assert test() == '<html><body><p>whoa nelly! <em>some text</em></p></body></html>'


class TestRenderDocstring(object):

    def test_render_docstring(self):

        @render.docstring()
        def test(request):
            """
            <html>1 + 1 = ${1 + 1}</html>
            """
            return {}

        assert getoutput(test) == '<html>1 + 1 = 2</html>'

    def test_make_render_docstring_cant_include_without_loader(self):

        render = GenshiRender()
        @render.docstring()
        def test(request):
            """
            <html xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="t1.html" /></html>
            """
            return {}

        try:
            getoutput(test)
        except TemplateNotFound:
            pass
        else:
            raise AssertionError("TemplateNotFound not raised")

    def test_make_render_docstring_uses_loader(self):

        render = GenshiRender(testloader)
        @render.docstring()
        def test(request):
            """
            <html xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="t1.html" /></html>
            """
            return {}
        assert getoutput(test) == '<html><div>t1</div></html>'

class TestDefaultVars(object):

    def test_dict_default_vars(self):
        render = GenshiRender(default_vars={'foo': 'bar'})
        @render.docstring()
        def test(request):
            """
            <html>foo is $foo</html>
            """
        assert getoutput(test) == '<html>foo is bar</html>'

    def test_callable_default_vars(self):
        render = GenshiRender(default_vars=lambda: {'foo': 'bar'})
        @render.docstring()
        def test(request):
            """
            <html>foo is $foo</html>
            """
        assert getoutput(test) == '<html>foo is bar</html>'

    def test_add_default_vars(self):
        render = GenshiRender(default_vars=lambda: {'foo': 'bar'})
        render.add_default_vars({'bar': 'foo'})
        @render.docstring()
        def test(request):
            """
            <html>foo is $foo, bar is $bar</html>
            """
        assert getoutput(test) == '<html>foo is bar, bar is foo</html>'


class TestLoadRelativeTo(object):

    def test_relative_to_file(self):
        render = GenshiRender(relative_to=__file__)
        assert render.as_string('templates/t1.html', {}) == '<div>t1</div>'

        render = GenshiRender(relative_to=path.join(path.dirname(__file__), 'templates', 't1.html'))
        assert render.as_string('subdir/index.html', {}) == '<div>subdir index</div>'

class TestGenshiDirectoryView(TestCase):

    app = genshi_app_factory(
        None,
        document_root=path.join(testdir, 'templates')
    )

    def _test_genshi_app(self, path_info):
        return Response.from_wsgi(
            self.app,
            MockRequest(PATH_INFO=path_info).environ,
            lambda status, headers: None
        )

    def test_genshi_app_serves_file(self):
        assert list(self._test_genshi_app('/t1.html').content) == ["<div>t1</div>"]

    def test_genshi_app_redirects_dir(self):
        assert self._test_genshi_app('/subdir').status_code == 302
        redirect = self._test_genshi_app('/subdir').get_header('location')
        assert redirect == 'http://localhost/subdir/', redirect

    def test_genshi_app_renders_default_doc(self):
        assert list(self._test_genshi_app('/subdir/').content) == ['<div>subdir index</div>']

    def test_genshi_app_returns_404_on_missing_default_doc(self):
        assert self._test_genshi_app('/subdir2/').status_code == 404

