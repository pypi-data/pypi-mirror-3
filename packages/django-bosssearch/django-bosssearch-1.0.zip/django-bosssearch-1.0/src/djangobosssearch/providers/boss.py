'''
The actual Yahoo BOSS API search implementation.
'''
import urllib
import oauth.oauth as oauth
from django.conf import settings
from djangobosssearch.providers import base
try:  # pragma: no cover
    import simplejson as json
except ImportError:  # pragma: no cover
    import json


class BossSearchException(base.SearchException):
    '''
    Something went wrong when fetching results. Gets raised when the response
    is invalid, or contains errors.
    '''

    @classmethod
    def from_response(cls, response):
        '''
        Extracts the error messages from the JSON decoded API response.

        Kwargs:
            response (dict): The JSON decoded API response.

        Returns:
            BossSearchException with the error message(s) formatted
            in a readable way.
        '''
        return BossSearchException(cls.format_error(response))

    @staticmethod
    def format_error(response):
        '''
        Helper method to format an API error message.

        Kwargs:
            error (dict): Error taken from the JSON response dict.

        Returns:
            str: The formatted error message.
        '''
        if 'bossresponse' in response:
            error = response['bossresponse']
            return '%s: %s' % (error['responsecode'], error['reason'])
        elif 'error' in response:
            error = response['error']
            return error['description']


class BossWebSearchProvider(base.SearchProvider):
    '''
    A search provider using the Yahoo BOSS API, with 'web',
    'spelling' as the source.
    '''
    endpoint = 'http://yboss.yahooapis.com/ysearch/'
    sources = ['web', 'spelling']

    def __init__(self, key, secret, market='en-us'):
        '''
        Initialize the search provider.

        Kwargs:
            key (str): API key
            secret (str): API secret
            market (str): Which region (country) to search, default 'en-us'.
        '''
        super(BossWebSearchProvider, self).__init__()
        self.key = key
        self.secret = secret
        self.market = market

    def search(self, query):
        '''
        Do a search for the given keyword.

        Kwargs:
            query (str): The term to search for.
            page (int): The page offset (default: 1).

        Returns:
            A :class:`djangobosssearch.providers.boss.BossResultSet`
            instance.
        '''
        return BossResultSet(self, query)

    def get_params(self, query, per_page, offset, market=None):
        '''
        Get all the params for the search.
        '''
        return {
            'q': query,
            'start': offset,
            'count': per_page,
            'market': market or 'en-us',
            'format': 'json'
        }

    def raw_search(self, query, per_page, offset=0):
        '''
        Performs the actual search.

        Kwargs:
            query (str): The term to search for.
            per_page (int): The amount of results to return.
            offset (int): The result offset (default: 0).

        Returns:
            dict of JSON decoded response.

        Raises:
            BossSearchException: API exception
        '''
        endpoint = '%s%s' % (self.endpoint, ','.join(self.sources))
        params = self.get_params(query, per_page, offset, self.market)

        consumer = oauth.OAuthConsumer(self.key, self.secret)
        hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, token=None, http_method='GET',
            http_url=endpoint, parameters=params)
        oauth_request.sign_request(hmac_sha1, consumer, "")
        complete_url = oauth_request.to_url()
        try:
            content = urllib.urlopen(complete_url).read()
        except IOError, e:
            _, code, message, headers = e
            raise BossSearchException('%s: %s %s' %
                    (code, message, headers['www-authenticate']))
        try:
            # XXX: Sometimes the response headers are appended to the
            #      response content. Just get rid of them.
            response = json.loads(content.split('HTTP/1')[0])
            return response
        except ValueError, e:
            raise BossSearchException('JSONDecodeError: %s' % e)


class BossSiteSearchProvider(BossWebSearchProvider):
    '''
    A search provider that's limited to a specific domain.
    '''

    def __init__(self, key, secret, domain, market='en-us'):
        '''
        Initialize the search provider.

        Kwargs:
            key (str): API key
            secret (str): API secret
            domain (str): A domain name (e.g. example.com) to search within.
        '''
        super(BossSiteSearchProvider, self).__init__(key, secret, market)
        self.domain = domain

    def get_params(self, query, per_page, offset, market=None):
        '''
        Get all the params for the search and add the given search domain.
        '''
        params = super(BossSiteSearchProvider, self).get_params(
                    query, per_page, offset)
        params.update({
            'sites': self.domain,
        })
        return params


class BossResultSet(base.ResultSet):
    '''
    This object describes the result set of a web search.
    '''
    def __init__(self, provider, query):
        super(BossResultSet, self).__init__(provider, query)
        self._raw_results = {}

    def count(self):
        '''
        Returns:
            The (estimated) total number of results.
        '''
        rpp = getattr(settings, 'BOSS_RESULTS_PER_PAGE', 50)
        return int(self.fetch(1, rpp)['web'].get('totalresults', 0))

    def page(self, number, per_page):
        '''
        Fetch a page of results for this resultset.

        Kwargs:
            number (int): The page number.
            per_page (int): The number of results per page.

        Returns:
            A iterable set of
            :class:`djangobosssearch.providers.boss.BossResult` instances.

        Raises:
            BossSearchException: API exception
        '''
        results = []
        if 'results' in self.fetch(number, per_page)['web']:
            results = [result for result in BossResultGenerator(
                        self.fetch(number, per_page)['web']['results'])]
        return results

    def fetch(self, number, per_page):
        '''
        Fetch a page of raw results for this resultset.

        Kwargs:
            number (int): The page number.
            per_page (int): The number of results per page.

        Returns:
            A dict created from decoding the JSON response.

        Raises:
            BossSearchException: API exception
        '''
        key = '%s_%s' % (number, per_page)
        if not key in self._raw_results:
            offset = self.get_offset(number, per_page)
            response = self.provider.raw_search(self.query, per_page, offset)
            if not 'bossresponse' in response and not 'error' in response:
                raise BossSearchException(
                    'No bossresponse in response object.')
            if ('error' in response
                    or response['bossresponse']['responsecode'] != '200'):
                raise BossSearchException.from_response(response)
            self._raw_results[key] = response['bossresponse']
        return self._raw_results[key]

    @staticmethod
    def get_offset(number, per_page):
        '''
        Calculate the offset number for the API call.

        Kwargs:
            number (int): The page number.
            per_page (int): The number of results per page.

        Returns:
            The result offset (zero based).
        '''
        offset = per_page * (number - 1)
        if offset > 0:
            return offset + 1
        return offset

    def spelling(self):
        '''
        Get spelling suggestions for the entered query.

        Returns:
            A spelling suggestion.
        '''
        rpp = getattr(settings, 'BOSS_RESULTS_PER_PAGE', 50)
        response = self.fetch(1, rpp)
        if 'spelling' in response and response['spelling']['count'] == '1':
            return response['spelling']['results'][0]['suggestion']


class BossResultGenerator(object):
    '''
    Generator that transforms a raw SearchResponse into a set of
    :class:`djangobosssearch.providers.boss.BossResult` instances.
    '''

    def __init__(self, raw_resultset):
        super(BossResultGenerator, self).__init__()
        self.i = 0
        self._raw_resultset = raw_resultset

    def __iter__(self):
        return self

    def next(self):
        '''
        Get the next result or StopIteration.

        Returns:
            The next :class:`djangobosssearch.providers.boss.BossResult`
            instance.

        Raises:
            StopIteration when the last result has been reached.
        '''
        if self.i < len(self._raw_resultset):
            result = self._raw_resultset[self.i]
            self.i += 1
            return BossResult(result)
        raise StopIteration


class BossResult(base.Result):
    '''
    A result object.
    '''

    def __init__(self, raw_result):
        super(BossResult, self).__init__()
        self._title = raw_result['title']
        self._description = raw_result.get('abstract', '')
        self._url = raw_result['clickurl']
        self._display_url = raw_result['dispurl']
