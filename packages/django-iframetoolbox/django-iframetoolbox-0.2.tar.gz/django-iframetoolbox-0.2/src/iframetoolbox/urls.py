from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    'iframetoolbox.views',
    url(r'iframefix/$', 'iframe_fix'),
)
