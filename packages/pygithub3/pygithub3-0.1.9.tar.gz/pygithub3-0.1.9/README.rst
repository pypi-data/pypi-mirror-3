Pygithub3
==========

Pygithub3 is a wrapper to the **Github API v3**,
written in Python.

It has been developed with extensibility in mind, because the ``API`` is in a
beta state, trying to achieve a very loosly coupled software.

It should be very easy to extend to support new ``requests`` and ``resources``,
because each of them are managed by itself.

`Pygithub3 docs <http://pygithub3.rtfd.org>`_

`Github API v3 docs <http://developer.github.com/v3/>`_

Fast install
-------------
::

    pip install pygithub3

Fast example
-------------
::

    from pygithub3 import Github

    gh = Github(login='copitux', password='password')

    copitux = gh.users.get()
    kennethreitz = gh.users.get('kennethreitz')

    copitux_repos = gh.repos.list().all()
    kennethreitz_repos = gh.repos.list('kennethreitz').all()

Achievements
-------------

- The core
- `User service <http://developer.github.com/v3/users/>`_

TODO
-----

- `Repo service <http://developer.github.com/v3/repos/>`_

Contribute
-----------

1. Fork the `repository <https://github.com/copitux/python-github3>`_
2. Write a test to cover new feature or to reproduce bug
3. Code with `pep8 <http://www.python.org/dev/peps/pep-0008/>`_ rules
4. Add you to ``AUTHORS``
5. Pull request it

**Note**: I use `nose <http://readthedocs.org/docs/nose/en/latest/>`_ test environment,
with `mock <http://www.voidspace.org.uk/python/mock/>`_ ``pip install nose mock``
