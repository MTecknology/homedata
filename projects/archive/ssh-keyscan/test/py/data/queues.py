#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Sample queue data
'''
# Python Imports
import textwrap

FILES = {
    'automount': textwrap.dedent('''\
            #$Header: /cvs/juniper/admin/admin-systems/rotor/etc/local/dist-auto/base_auto_homes,v 1.1 2009/03/25 22:02:41 rsn Exp $
            # automount map per user (e.g. /homes/<user> )
            #
            # This file was auto-generated on rotor.juniper.net.
            # DO NOT EDIT IT! or your changes will be overwritten.
            # You probably want to edit rotor.juniper.net:/etc/local/system_database instead.
            #
            www                  sdc-homeflr-a-9:/vol/homes9/home9/www
            xmljobs              sdc-homeflr-a-9:/vol/homes9/home9/xmljobs
            schedule             svl-engdata1vs1-schedule:/vol/schedule
            junos                svl-engdatahome5-002cf1:/vol/home5_002cf1/homes5/junos
            '''),
    'userlist': textwrap.dedent('''\
            www
            xmljobs
            schedule
            junos
            '''),
    }

FILE_LINES = {
    'automount': [
        '#$Header: /cvs/juniper/admin/admin-systems/rotor/etc/local/dist-auto/base_auto_homes,v 1.1 2009/03/25 22:02:41 rsn Exp $',
        '# automount map per user (e.g. /homes/<user> )',
        '#',
        '# This file was auto-generated on rotor.juniper.net.',
        '# DO NOT EDIT IT! or your changes will be overwritten.',
        '# You probably want to edit rotor.juniper.net:/etc/local/system_database instead.',
        '#',
        'www                  sdc-homeflr-a-9:/vol/homes9/home9/www',
        'xmljobs              sdc-homeflr-a-9:/vol/homes9/home9/xmljobs',
        'schedule             svl-engdata1vs1-schedule:/vol/schedule',
        'junos                svl-engdatahome5-002cf1:/vol/home5_002cf1/homes5/junos',
        ],
    'userlist': [
        'www',
        'xmljobs',
        'schedule',
        'junos',
        ],
    }
