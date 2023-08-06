#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pygithub3.services.users import User


class Github(object):
    """ Main entrance """

    def __init__(self, **config):
        self._users = User(**config)

    @property
    def users(self):
        return self._users
