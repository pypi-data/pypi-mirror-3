from django import template
from pytest import raises
from okonomi.templatetags import okonomi as tags
from okonomi.tests import helpers


class TestJSRequire(object):
    # FIXME How the hell do you test this?

    def fixme_test_less_thank_two_tokens_raises(self):
        exc = raises(template.TemplateSyntaxError,tags.jsrequire,helpers.FakeRequest(), "")
        assert exc.value.args == ''


class TestJSRequireNode(object):

    def test_raise_when_nothing_is_passed(self):
        exc = raises(template.TemplateSyntaxError, tags.JSRequireNode)
        assert exc.value.args[0] == 'Expected either a relative path or a fully qualified url. Got nothing'

    def test_raise_when_both_are_passed(self):
        exc = raises(template.TemplateSyntaxError, tags.JSRequireNode, path='/', url='/')
        assert exc.value.args[0] == 'Expected either a relative path or a fully qualified url. Got both'

    def test_render_correctly(self):
        js_require = tags.JSRequireNode(path='/')
        result = js_require.render([])
        assert result == '<!-- requires / -->'

    def test_resolve_template_variables(self):
        template_var = 'http://maps.google.com/maps?&key="{{ googlemaps_api_key }}"'
        context = {'googlemaps_api_key' : 'the_awesome'}
        js_require = tags.JSRequireNode(path='/')
        result = js_require.resolve_template_variables(template_var, context)
        assert result == 'http://maps.google.com/maps?&key=the_awesome'

    def test_dont_resolve_template_variables(self):
        template_var = 'http://maps.google.com/maps?&key="{{ googlemaps_api_key }}"'
        context = {'yahoo_api_key' : 'the_awesome'}
        js_require = tags.JSRequireNode(path='/')
        result = js_require.resolve_template_variables(template_var, context)
        assert result == 'http://maps.google.com/maps?&key='

