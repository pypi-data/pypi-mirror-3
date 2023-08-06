'''
The BOSS search / results view.
'''

from django.conf import settings
try:
    from django.shortcuts import render
except ImportError:
    from django.views.generic.simple import direct_to_template as render

from djangobosssearch.paginator import ResultsetPaginator
from djangobosssearch.providers.boss import BossWebSearchProvider, \
    BossSiteSearchProvider


def bosssearch(request):
    '''
    Perform a search using the BossWebSearchProvider.
    '''
    if 'q' in request.GET and request.GET['q'].strip():
        market = getattr(settings, 'BOSS_SEARCH_MARKET', 'en-us')
        rpp = getattr(settings, 'BOSS_RESULTS_PER_PAGE', 50)
        if hasattr(settings, 'BOSS_SITE_SEARCH_DOMAIN'):
            provider = BossSiteSearchProvider(settings.BOSS_API_KEY,
                                              settings.BOSS_API_SECRET,
                                              settings.BOSS_SITE_SEARCH_DOMAIN,
                                              market)
        else:
            provider = BossWebSearchProvider(settings.BOSS_API_KEY,
                                             settings.BOSS_API_SECRET,
                                             market)
        resultset = provider.search(request.GET['q'])
        paginator = ResultsetPaginator(resultset, rpp)
        page_obj = paginator.page(request.GET.get('page', 1))
        return render(request, 'bosssearch/results.html', {
            'resultset': resultset,
            'paginator': paginator,
            'page_obj': page_obj,
        })
    return render(request, 'bosssearch/form.html')
