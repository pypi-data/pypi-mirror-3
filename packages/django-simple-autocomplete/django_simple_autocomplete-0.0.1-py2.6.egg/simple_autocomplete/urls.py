from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'simple_autocomplete.views',
    url(r'^(?P<token>[\w-]+)/$', 'get_json', name='simple-autocomplete'),
)
