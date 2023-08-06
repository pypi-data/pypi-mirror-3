from django.conf import settings
from django.conf.urls.defaults import patterns

from i18nurls.urlresolvers import LocaleRegexURLResolver


def i18n_patterns(prefix, *args):
    pattern_list = patterns(prefix, *args)
    if not settings.USE_I18N:
        return pattern_list
    return [LocaleRegexURLResolver(pattern_list)]
