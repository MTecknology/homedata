#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Library for working with git repositories.

.. note:: This library does not implement access controls. ACLs are handled by
          the ``auth`` module.
'''
# Python / Flask Imports
import flask
import pygit2


#def list_contents(repository, commit='HEAD'):
#    '''
#    Return a file listing for a repository.
#
#    :param repository:
#        Repository Name
#
#    :param commit:
#        Repository commit ID
#    '''
#    pass


def read_file(repository, commit, path):
    '''
    Return the contents of a single file.

    :param repository:
        Repository Name

    :param commit:
        Repository commit ID

    :param path:
        Path to file.
    '''
    g3_root = flask.current_app.config['G3_ROOT']
    g3_root = g3_root[:-1] if g3_root[-1:] == '/' else g3_root

    try:
        repo = pygit2.Repository('{}/repositories/{}'.format(g3_root, repository))
        blob = repo.revparse_single('{}:{}'.format(commit, path))
    except:
        return False
    return blob.data


#def read_files(filelist):
#    '''
#    Return the contents of multiple files.
#
#    :param filelist:
#        List of tuples, see ``read_file()`` for tuple format.
#
#    .. code:: python
#
#        read_files([
#            ('repo', 'commit', 'path'),
#            ('repo', 'commit', 'path'),
#            ])
#    '''
#    pass
