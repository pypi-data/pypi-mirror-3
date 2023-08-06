from django.conf import settings

OKONOMI_JS_PLACEHOLDER = '${JSREQUIRE}'
OKONOMI_STATIC_URL = settings.OKONOMI_STATIC_URL
OKONOMI_HTML_PATH_TEMPLATE = getattr(settings, 'OKONOMI_HTML_PATH_TEMPLATE', '<script type="text/javascript" src="%s"></script>\n')
OKONOMI_HTML_URL_TEMPLATE = getattr(settings, 'OKONOMI_HTML_URL_TEMPLATE', '<script type="text/javascript" src="%s"></script>\n')

class Okonomi(object):
    """
    the okonomi middleware prepares unique combinations of javascript includes
    for rendered django templates. it stores the combined javascript in memcache
    for fast serving by a view used as a single point of javascript inclusion.
    """

    # TODO should this return the request object?
    def process_request(self, request):
        request.okonomi_paths = []
        request.okonomi_urls = []

    def process_response(self, request, response):
        def early_exit(response):
            response.content = response.content.replace(OKONOMI_JS_PLACEHOLDER, '')
            return response

        if not (hasattr(request, 'okonomi_paths') or hasattr(request, 'okonomi_urls')):
            return early_exit(response)
        if len(request.okonomi_urls) == 0 and len(request.okonomi_paths) == 0:
            return early_exit(response)

        # This sucks, but set() doesn't preserve order and we need order for js
        # dependencies. so we're using a list and deduping.
        def dedupe(l):
            seen = set()
            seen_add = seen.add
            return [ x for x in l if x not in seen and not seen_add(x)]

        remote_html = ''
        local_html = ''
        for url in dedupe(request.okonomi_urls):
            remote_html += (OKONOMI_HTML_URL_TEMPLATE % url)

        for path in dedupe(request.okonomi_paths):
            # TODO lack of / works for medley, but...
            # maybe revisit this to avoid adding urls
            url = settings.OKONOMI_STATIC_URL + path
            local_html += (OKONOMI_HTML_PATH_TEMPLATE % url)

        # why str()? we were getting UnicodeDecodeErrors
        combined = str(local_html+remote_html)
        response.content = response.content.replace(OKONOMI_JS_PLACEHOLDER, combined)

        return response

def context_processor(request):
    """ sticks paths and urls arrays into the template context """
    context = {}
    attrs = ['okonomi_paths', 'okonomi_urls']
    for attr in attrs:
        if hasattr(request, attr):
            context[attr] = getattr(request, attr)

    return context
