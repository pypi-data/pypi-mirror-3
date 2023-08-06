import re

from django.conf import settings
from django.core.urlresolvers import get_resolver
from django.http import HttpResponseRedirect
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.utils import translation
from django.utils.cache import patch_vary_headers

from i18nurls.urlresolvers import LocaleRegexURLResolver


language_code_prefix_re = re.compile(r'^/([\w-]+)(/|$)')


class LocaleMiddleware(DjangoLocaleMiddleware):

    def process_request(self, request):
        language_code = self.get_language_from_path(request.path_info)

        if not language_code:
            language_code = translation.get_language_from_request(request)

        translation.activate(language_code)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language_code = translation.get_language()
        translation.deactivate()

        if (response.status_code == 404 and
            not self.get_language_from_path(request.path_info)
                and self.is_language_prefix_patterns_used()):
            return HttpResponseRedirect(
                '/%s%s' % (language_code, request.get_full_path()))

        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language_code
        return response

    def is_language_prefix_patterns_used(self):
        for url_pattern in get_resolver(None).url_patterns:
            if isinstance(url_pattern, LocaleRegexURLResolver):
                return True
        return False

    def get_language_from_path(self, path):
        regex_match = language_code_prefix_re.match(path)
        if regex_match:
            language_code = regex_match.group(1)
            if language_code in dict(settings.LANGUAGES):
                return language_code
        return None
