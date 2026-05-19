#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
User data for running tests.
'''
# Python / Flask Imports
import textwrap


TEST_USERS = {

    # Normal/valid user
    'tester': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: 'Test User'
                gecos_location: 'GitRepo'
                passwords:
                  - 'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'
                  - 'd82c4eb5261cb9c8aa9855edd67d1bd10482f41529858d925094d173fa662aa91ff39bc5b188615273484021dfb16fd8284cf684ccf0fc795be3aa2fc1e6c181'
                '''),
        'dict': {
                'username': 'tester',
                'gecos_fields': {
                    'name': 'Test User',
                    'location': 'GitRepo',
                    },
                'passwords': [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
                    'd82c4eb5261cb9c8aa9855edd67d1bd10482f41529858d925094d173fa662aa91ff39bc5b188615273484021dfb16fd8284cf684ccf0fc795be3aa2fc1e6c181',
                    ],
                },
        },

    # User with no valid hash
    'rex': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: 'T. Rex'
                passwords: ['hashes_confuse_me']
                '''),
        'dict': {
                'username': 'rex',
                'gecos_fields': {'name': 'T. Rex'},
                'passwords': ['hashes_confuse_me']
                },
        },

    # User with unparseable file (not-yaml)
    'polaris': {
        'issue_expected': True,
        'issue_read-result': 'error parsing data',
        'blob': textwrap.dedent('''\
                gecos_name = 'I thought this was python.'
                passwords = [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7']
                '''),
        'dict': False,
        },

    # User with 'passwords' as string instead of list
    'jimbob': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: 'I thought lists and strings were the same'
                passwords: 'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'
                '''),
        'dict': {
                'username': 'jimbob',
                'gecos_fields': {'name': 'I thought lists and strings were the same'},
                'passwords': [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
                    ],
                },
        },

    # User with 'password' and 'passwords' and incorrect 'passwords' (str)
    'orion': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: "Why I can't haz both ??"
                passwords: 'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'
                password: [ 'invalid_hash' ]
                '''),
        'dict': {
                'username': 'orion',
                'gecos_fields': {'name': "Why I can't haz both ??"},
                'passwords': [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
                    ],
                },
        },

    # User with 'password' as string
    'centauri': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: I dislike plurals and lists
                password: f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7
                '''),
        'dict': {
                'username': 'centauri',
                'gecos_fields': {'name': 'I dislike plurals and lists'},
                'passwords': [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
                    ],
                },
        },

    # User with 'password' as list
    'wyona': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: I dislike logic
                password:
                  - f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7
                '''),
        'dict': {
                'username': 'wyona',
                'gecos_fields': {'name': 'I dislike logic'},
                'passwords': [
                    'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7',
                    ],
                },
        },
    # User with 'password' as INVALID boolean
    'sienna': {
        'issue_expected': False,
        'blob': textwrap.dedent('''\
                gecos_name: I dislike logic
                password: true
                '''),
        'dict': {
                'username': 'sienna',
                'gecos_fields': {'name': 'I dislike logic'},
                'passwords': [],
                },
        },

    # User with literal tab in file (LITERAL TAB)
    'andromeda': {
        'issue_expected': True,
        'issue_read-result': 'error parsing data',
        'blob': textwrap.dedent('''\
                gecos_name: I dislike plurals and lists
		passwords: ['TAB PRESENT ON THIS LINE']
                '''),
        'dict': False,
        },

    # User attempting to read a configuration variable (w/ py)
    'l33t_hax0r': {
        'issue_expected': True,
        'issue_read-result': 'error parsing data',
        'blob': textwrap.dedent('''\
                from gitlight import app
                gecos_name = app.current_app.config.get('SECRET_KEY', 'Fuzzy Wuzzy')
                passwords = 'f7fbba6e0636f890e56fbbf3283e524c6fa3204ae298382d624741d0dc6638326e282c41be5e4254d8820772c5518a2c5a8c0c7f7eda19594a7eb539453e1ed7'
                '''),
        'dict': False,
        },

    # User does not exist
    'terminator': {
        'issue_expected': True,
        'issue_read-result': 'error loading data',
        'blob': False,
        'dict': False,
        },
    }
