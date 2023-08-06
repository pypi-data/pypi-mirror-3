from django.conf.urls.defaults import patterns, include, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from i18nurls.i18n import i18n_patterns


urlpatterns = patterns('',
    url(
        r'^not-prefixed/$',
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='not-prefixed'
    ),
    url(
        r'^news/$',
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='news-no-i18n'
    ),
)

urlpatterns += i18n_patterns('',
    url(
        r'^$',
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='root'
    ),
    url(
        r'^prefixed/$',
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='prefixed'
    ),
    url(
        _(r'^news/$'),
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='news'
    ),
    url(
        _(r'^users/'),
        include('i18nurls.tests.user_urls',
        namespace='users')
    ),
)
