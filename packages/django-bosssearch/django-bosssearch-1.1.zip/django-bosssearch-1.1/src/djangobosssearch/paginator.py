'''
A Django Paginator compatible search paginator.
'''

from django.core.paginator import Paginator, Page


class ResultsetPaginator(Paginator):
    '''
    A paginator that can paginate over
    :class:`djangobosssearch.providers.base.resultset` implementations.
    '''

    def page(self, number):
        '''
        Returns a Page object for the given 1-based page number.
        '''
        number = self.validate_number(number)
        return Page(self.object_list.page(number, self.per_page), number, self)
