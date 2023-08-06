'''
URL patterns for the search and search results page.
'''

from django.conf.urls.defaults import url, patterns


urlpatterns = patterns('djangobosssearch.views',
    url(r'^$', 'bosssearch', name='bosssearch')
)
