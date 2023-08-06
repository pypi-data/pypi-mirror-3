#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from urlparse import urlparse, parse_qs

from .third_libs.link_header import parse_link_value


class Method(object):

    def __init__(self, method, request, **method_args):
        self.method = method
        self.request = request
        self.args = method_args
        self.cache = {}

    def cached(func):
        def wrapper(self, page=1):
            if str(page) in self.cache:
                return self.cache[str(page)]
            return func(self, page)
        return wrapper

    def if_needs_lastpage(func):
        def wrapper(self, response):
            has_link = response.headers.get('link')
            has_last_page = hasattr(self, 'last_page')
            if not has_last_page and has_link:
                return func(self, response)
            elif not has_last_page and not has_link:
                self.last_page = 1
        return wrapper

    @if_needs_lastpage
    def __set_last_page_from(self, response):
        link_parsed = parse_link_value(response.headers['link'])

        def get_last(url):
            url_rels = link_parsed[url]
            return (url_rels.get('rel') == 'last')
        url_last = filter(get_last, link_parsed)
        query = urlparse(url_last.pop()).query
        self.last_page = int(parse_qs(query).get('page').pop())

    @cached
    def __call__(self, page=1):
        all_args = self.args.copy()
        all_args.update(page=page)
        response = self.method(self.request, **all_args)
        self.__set_last_page_from(response)
        resource = self.request.resource
        self.cache[str(page)] = resource.loads(response.content)
        return self.cache[str(page)]

    @property
    def last(self):
        if not hasattr(self, 'last_page'):
            self()
        return self.last_page


class Page(object):
    """ """

    def __init__(self, getter, page=1):
        """ """
        self.getter = getter
        self.page = page

    def __iter__(self):
        return self

    def __add__(self, number):
        return self.page + number

    def __radd__(self, number):
        return number + self.page

    def __sub__(self, number):
        return self.page - number

    def __rsub__(self, number):
        return number - self.page

    def __lt__(self, number):
        return self.page < number

    def __le__(self, number):
        return self.page <= number

    def __eq__(self, number):
        return self.page == number

    def __ne__(self, number):
        return self.page != number

    def __gt__(self, number):
        return self.page > number

    def __ge__(self, number):
        return self.page >= number

    @property
    def resources(self):
        return getattr(self, '_count', None) or u"~"

    def get_content(func):
        def wrapper(self):
            if not hasattr(self, '_count'):
                content = self.getter(self.page)
                self._count = len(content)
                self.iterable = iter(content)
            return func(self)
        return wrapper

    @get_content
    def __next__(self):
        try:
            return self.iterable.next()
        except StopIteration:
            self.iterable = iter(self.getter(self.page))
            raise StopIteration

    def next(self):
        return self.__next__()

    def __str__(self):
        return '<{name}{page} resources={resources}>'.format(
                name=self.__class__.__name__,
                page=self.page,
                resources=self.resources)

    def __repr__(self):
        return "%s[%d]" % (self.__str__(), id(self))


class Result(object):
    """
    Result is a very lazy paginator. It only do a real request when is needed

    You have several ways to consume it

    #. Iterating over the result::

        result = some_request()
        for page in result:
            for resource in page:
                print resource

    #. With a generator::

        result = some_request()
        for resource in result.iterator():
            print resource

    #. As a list::

        result = some_request()
        print result.all()

    #. Also you can request some page manually

        .. autoattribute:: pygithub3.core.result.Result.pages
        .. automethod:: pygithub3.core.result.Result.get_page

        Each ``Page`` is an iterator and contains resources::

            result = some_request()
            assert result.pages > 3
            page3 = result.get_page(3)
            page3_resources = list(page3)
    """

    def __init__(self, client, request, **kwargs):
        self.getter = Method(client.get, request, **kwargs)
        self.page = Page(self.getter)

    def __iter__(self):
        return self

    def __next__(self):
        if self.page <= self.pages:
            page_to_return = self.page
            self.page = Page(self.getter, page_to_return + 1)
            return page_to_return
        self.page = Page(self.getter)
        raise StopIteration

    def next(self):
        return self.__next__()

    @property
    def pages(self):
        """ Total number of pages in request """
        return self.getter.last

    def get_page(self, page):
        """ Get ``Page`` of resources

        :param int page: Page number
        """
        if page in xrange(1, self.pages + 1):
            return Page(self.getter, page)
        return None

    def iterator(self):
        for page in self:
            for resource in page:
                yield resource

    def all(self):
        return list(self.iterator())
