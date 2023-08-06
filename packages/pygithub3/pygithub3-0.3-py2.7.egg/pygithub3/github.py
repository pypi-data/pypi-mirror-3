#!/usr/bin/env python
# -*- encoding: utf-8 -*-


#TODO: Move the imports out. setup related
class Github(object):
    """
    You can preconfigure all services globally with a ``config`` dict. See
    :attr:`~pygithub3.services.base.Service`

    Example::

        gh = Github(user='kennethreitz', token='ABC...', repo='requests')
    """

    def __init__(self, **config):
        from pygithub3.services.users import User
        from pygithub3.services.repos import Repo
        from pygithub3.services.gists import Gist
        self._users = User(**config)
        self._repos = Repo(**config)
        self._gists = Gist(**config)

    @property
    def remaining_requests(self):
        """ Limit of Github API v3 """
        from pygithub3.core.client import Client
        return Client.remaining_requests

    @property
    def users(self):
        """
        :ref:`Users service <Users service>`
        """
        return self._users

    @property
    def repos(self):
        """
        :ref:`Repos service <Repos service>`
        """
        return self._repos

    @property
    def gists(self):
        """
        :ref:`Gists service <Gists service>`
        """
        return self._gists
