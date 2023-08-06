from django.conf.urls.defaults import url, patterns, include, handler404, handler500


urlpatterns = patterns('',
    url(r'^$', include('djangobosssearch.bosssearch_urls')),
)
