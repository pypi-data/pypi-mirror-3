from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(
        _(r'register/$'),
        TemplateView.as_view(template_name='i18nurls/dummy.html'),
        name='register'
    ),
)
