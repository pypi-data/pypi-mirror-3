Django URL internationalization
===============================

This Django app makes it possible to prefix URL patterns with the active
language and to make URL patterns translatable by using gettext. As well this
package contains a middleware which is able to activate the right language
(based on the language-prefix in the requested URL).

.. note::

    During the DjangoCon EU 2011 sprints, I wrote a patch for including this
    functionality into the Django core. This patch was accepted and will be
    included in Django 1.4 (thanks to Jannis Leidel and Russell Keith-Magee for
    their feedback and reviewing the patch).

    Django documentation: `Internationalization: in URL patterns <https://docs.djangoproject.com/en/dev/topics/i18n/translation/#internationalization-in-url-patterns>`_.


Translating URL patterns
------------------------

After installing this package, URL patterns can also be marked translatable
using the ``ugettext_lazy()`` function. Example::

    from django.conf.urls.defaults import patterns, include, url
    from django.utils.translation import ugettext_lazy as _
    from i18nurls.i18n import i18n_patterns

    urlpatterns = patterns(''
        url(r'^sitemap\.xml$', 'sitemap.view', name='sitemap_xml'),
    )

    news_patterns = patterns(''
        url(r'^$', 'news.views.index', name='index'),
        url(_(r'^category/(?P<slug>[\w-]+)/$'), 'news.views.category', name='category'),
        url(r'^(?P<slug>[\w-]+)/$', 'news.views.details', name='detail'),
    )

    urlpatterns += i18n_patterns('',
        url(_(r'^about/$'), 'about.view', name='about'),
        url(_(r'^news/$'), include(news_patterns, namespace='news')),
    )


After you've created the translations, the ``reverse()`` function will return
the URL in the active language. Example::

    from django.core.urlresolvers import reverse
    from django.utils.translation import activate

    >>> activate('en')
    >>> reverse('news:category', kwargs={'slug': 'recent'})
    '/en/news/category/recent/'

    >>> activate('nl')
    >>> reverse('news:category', kwargs={'slug': 'recent'})
    '/nl/nieuws/categorie/recent/'


Reversing in templates
----------------------

If localized URLs get reversed in templates they always use the current
language. To link to a URL in another language use the ``language`` template
tag. It enables the given language in the enclosed template section::

    {% load i18nurls i18n %}

    {% get_available_languages as languages %}

    {% trans "View this category in:" %}
        {% for lang_code, lang_name in languages %}
            {% language lang_code %}
                <a href="{% url category slug=category.slug %}">{{ lang_name }}</a>
            {% endlanguage %}
    {% endfor %}


See also: `Reversing in templates <https://docs.djangoproject.com/en/dev/topics/i18n/translation/#std:templatetag-language>`_.


Installation
------------

* Install the ``django-i18nurls`` package (eg: ``pip install django-i18nurls``).

* Add ``i18nurls`` to your ``settings.INSTALLED_APPS``.

* Add ``i18nurls.middleware.LocaleMiddleware`` to your
  ``settings.MIDDLEWARE_CLASSES`` (make sure it comes before the
  ``CommonMiddleware``).


Changelog
---------

v0.7
~~~~

* ``{% language %}`` template-tag implemented (thanks to Harro van der Klauw).
* ``LocaleMiddleware`` class is not patched anymore (Issue #3).
* ``i18n_patterns`` is not patched anymore.
* Trailing slash is now optional in ``LocaleMiddleware`` regex.

v0.6.1
~~~~~~

* templates and locale folder added to setup.py script (Issue #1).

v0.6
~~~~

* API changed so it will match with ``i18n_patterns`` in upcoming Django 1.4 release.

v0.5.2
~~~~~~

* Some README errors corrected.

v0.5.1
~~~~~~

* Some code cleanup.

v0.5
~~~~

* Initial release.
