import re
import logging

from django import template

logger = logging.getLogger(__name__)
register = template.Library()

@register.tag(name="jsrequire")
def jsrequire(parse, token):
    """
        Syntax::
            {% jsrequire path_relative_to_STATIC_URL|url %}

        Examples::
            {% jsrequire /formcheckin.js %}
            {% jsrequire /jqueryui/accordian.js %}
            {% jsinclde https://maps.google.com/api/?key=123 %}

    """
    tokens = token.split_contents()
    if len(tokens) < 2:
        raise template.TemplateSyntaxError('Need a path relative to STATIC_URL or a fully qualified url.')

    path_or_url = tokens.pop()
    path = None
    url = None
    if path_or_url.startswith('http'):
        url = path_or_url
    else:
        path = path_or_url

    return JSRequireNode(path, url)

class JSRequireNode(template.Node):
    def __init__(self, path=None, url=None):
        if not (path or url):
            raise template.TemplateSyntaxError('Expected either a relative path or a fully qualified url. Got nothing')
        if path and url:
            raise template.TemplateSyntaxError('Expected either a relative path or a fully qualified url. Got both')
        if path:
            self.path = path
            self.url = None
        if url:
            self.path = None
            self.url = url

    def render(self, context):
        if self.path and 'okonomi_paths' in context:
            context['okonomi_paths'].append(self.resolve_template_variables(self.path, context))
        if self.url and 'okonomi_urls' in context:
            context['okonomi_urls'].append(self.resolve_template_variables(self.url, context))

        return '<!-- requires %s -->' % (self.path or self.url)

    def resolve_template_variables(self, path, context):
        """ Resolve any template variables in the path, it must be within double quotes.
            e.g. path `http://maps.google.com/maps?&key="{{ googlemaps_api_key }}"`
            becomes `http://maps.google.com/maps?&key=123`
        """
        template_vars = re.findall('"{{[a-zA-Z0-9\ _]+}}"', path)

        for v in template_vars:
            val = ''
            try:
                val = template.Variable(v.strip(' "{}')).resolve(context)
            except template.VariableDoesNotExist:
                logger.debug("Could not find template variable '%s' in context." % v)
            path = path.replace(v, val)

        return path
