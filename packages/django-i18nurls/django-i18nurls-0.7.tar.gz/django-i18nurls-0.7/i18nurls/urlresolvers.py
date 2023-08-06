import re

from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import force_unicode
from django.utils.regex_helper import normalize
from django.utils.translation import get_language

from i18nurls.monkeypatch import monkeypatch_class


class I18NRegexURLPattern(RegexURLPattern):
    # Monkeypatch for the origiginal RegexURLPattern class.

    __metaclass__ = monkeypatch_class

    def __init__(self, regex, callback, default_args=None, name=None):
        # This is almost the same as django.core.urlresolvers.RegexURLPattern
        # except that we are not going to set self.regex.
        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback
        self.default_args = default_args or {}
        self.name = name

        # Some new variables.
        self._i18n_regex = regex
        self._i18n_regex_dict = {}

    @property
    def regex(self):
        language_code = get_language()

        if language_code not in self._i18n_regex_dict:
            if isinstance(self._i18n_regex, basestring):
                compiled_regex = re.compile(self._i18n_regex, re.UNICODE)
            else:
                regex = force_unicode(self._i18n_regex)
                compiled_regex = re.compile(regex, re.UNICODE)
            self._i18n_regex_dict[language_code] = compiled_regex
        return self._i18n_regex_dict[language_code]


class I18NRegexURLResolver(RegexURLResolver):
    # Monkeypatch for the origiginal RegexURLResolver class.

    __metaclass__ = monkeypatch_class

    def __init__(self, regex, urlconf_name, default_kwargs=None, app_name=None, namespace=None):
        # This is almost the same as django.core.urlresolvers.RegexURLResolver
        # except that we are not going to set self.regex and we are going to
        # set some more variables for caching.
        self.urlconf_name = urlconf_name
        if not isinstance(urlconf_name, basestring):
            self._urlconf_module = self.urlconf_name
        self.callback = None
        self.default_kwargs = default_kwargs or {}
        self.namespace = namespace
        self.app_name = app_name

        # Some new variables
        self._i18n_regex = regex
        self._i18n_regex_dict = {}
        self._i18n_reverse_dict = {}
        self._i18n_namespace_dict = {}
        self._i18n_app_dict = {}

    @property
    def regex(self):
        language_code = get_language()

        if language_code not in self._i18n_regex_dict:
            if isinstance(self._i18n_regex, basestring):
                compiled_regex = re.compile(self._i18n_regex, re.UNICODE)
            else:
                regex = force_unicode(self._i18n_regex)
                compiled_regex = re.compile(regex, re.UNICODE)
            self._i18n_regex_dict[language_code] = compiled_regex
        return self._i18n_regex_dict[language_code]

    def _populate(self):
        # Almost the same as the original `_populate` function, except the last
        # 4 lines of code.
        lookups = MultiValueDict()
        namespaces = {}
        apps = {}
        language_code = get_language()
        for pattern in reversed(self.url_patterns):
            p_pattern = pattern.regex.pattern
            if p_pattern.startswith('^'):
                p_pattern = p_pattern[1:]
            if isinstance(pattern, RegexURLResolver):
                if pattern.namespace:
                    namespaces[pattern.namespace] = (p_pattern, pattern)
                    if pattern.app_name:
                        apps.setdefault(pattern.app_name, []).append(pattern.namespace)
                else:
                    parent = normalize(pattern.regex.pattern)
                    for name in pattern.reverse_dict:
                        for matches, pat in pattern.reverse_dict.getlist(name):
                            new_matches = []
                            for piece, p_args in parent:
                                new_matches.extend([(piece + suffix, p_args + args) for (suffix, args) in matches])
                            lookups.appendlist(name, (new_matches, p_pattern + pat))
                    for namespace, (prefix, sub_pattern) in pattern.namespace_dict.items():
                        namespaces[namespace] = (p_pattern + prefix, sub_pattern)
                    for app_name, namespace_list in pattern.app_dict.items():
                        apps.setdefault(app_name, []).extend(namespace_list)
            else:
                bits = normalize(p_pattern)
                lookups.appendlist(pattern.callback, (bits, p_pattern))
                if pattern.name is not None:
                    lookups.appendlist(pattern.name, (bits, p_pattern))

        self._i18n_reverse_dict[language_code] = lookups
        self._i18n_namespace_dict[language_code] = namespaces
        self._i18n_app_dict[language_code] = apps

    def _get_reverse_dict(self):
        language_code = get_language()
        if language_code not in self._i18n_reverse_dict:
            self._populate()
        return self._i18n_reverse_dict[language_code]
    reverse_dict = property(_get_reverse_dict)

    def _get_namespace_dict(self):
        language_code = get_language()
        if language_code not in self._i18n_namespace_dict:
            self._populate()
        return self._i18n_namespace_dict[language_code]
    namespace_dict = property(_get_namespace_dict)

    def _get_app_dict(self):
        language_code = get_language()
        if language_code not in self._i18n_app_dict:
            self._populate()
        return self._i18n_app_dict[language_code]
    app_dict = property(_get_app_dict)


class LocaleRegexURLResolver(RegexURLResolver):
    def __init__(self, urlconf_name, default_kwargs=None, app_name=None, namespace=None):
        super(LocaleRegexURLResolver, self).__init__(
            None, urlconf_name, default_kwargs, app_name, namespace)

    @property
    def regex(self):
        language_code = get_language()
        if language_code not in self._i18n_regex_dict:
            regex_compiled = re.compile('^%s/' % language_code, re.UNICODE)
            self._i18n_regex_dict[language_code] = regex_compiled
        return self._i18n_regex_dict[language_code]
