'''
Abstract API based search implementation.
'''


class SearchException(Exception):
    '''
    Base exception. Implementations should raise an exception that inherits
    from this if something went wrong when fetching the search results.
    '''
    pass


class SearchProvider(object):
    '''
    Base search provider. Needs to be extended to provide an
    actual implementation.
    '''

    def search(self, query):
        '''
        Do a search for the given keyword.

        Kwargs:
            query (str): The term to search for.

        Returns:
            A :class:`djangobosssearch.providers.base.ResultSet` instance.

        Raises:
            `NotImplementedError`: Search is not implemented in the base class.
        '''
        raise NotImplementedError  # pragma: no cover


class ResultSet(object):
    '''
    A result set is usually initialized and returned by a
    :class:`djangobosssearch.providers.base.SearchProvider` implementation.
    '''

    def __init__(self, provider, query):
        '''
        Initialize the resultset.

        Kwargs:
            provider (SearchProvider): The provider for this resultset.
            query (str): The term to search for.
        '''
        self.provider = provider
        self.query = query.strip()

    def count(self):
        '''
        Returns:
            The (estimated) total number of results.
        '''
        raise NotImplementedError  # pragma: no cover

    def get_query(self):
        '''
        Returns:
            The search term.
        '''
        return self.query

    def page(self, number, per_page):
        '''
        Fetch a page of results for this resultset.

        Kwargs:
            number (int): The page number.
            per_page (int): The number of results per page.
        '''
        raise NotImplementedError  # pragma: no cover


class Result(object):
    '''
    A basic result object.
    '''
    _title = ''
    _description = ''
    _url = ''
    _display_url = ''

    @property
    def title(self):
        '''
        Result title.
        '''
        return self._title

    @property
    def description(self):
        '''
        Result description.
        '''
        return self._description

    @property
    def url(self):
        '''
        Result url.
        '''
        return self._url

    @property
    def display_url(self):
        '''
        Result display url (same as url but without the protocol).
        '''
        return self._display_url
