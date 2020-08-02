#!/usr/bin/env python
##
# Quick little script to migrate Encyclopedia to Factoids
#   Requires sqlite old.db .dump | sqlite3 temp.db
#   Thanks twb!
##
import sqlite3

with sqlite3.connect('ng3.db') as old_conn:
    with sqlite3.connect('Factoids.db') as new_conn:
        old = old_conn.cursor()
        new = new_conn.cursor()
        for (oname, oadd, oval, opop) in old.execute('SELECT name,added,value,popularity from facts;'):
            if '<deleted>' in oval:
                continue
            if '<reply>' in oval:
                oval = oval.replace('<reply>', '')
            if '<alias>' in oval:
                oval = oval.replace('<alias>', '').strip()
                if ' ' in oval:
                    continue
                print('@alias #ngx-newbot {} {}'.format(oval.replace('<alias>', '').strip(), oname))
            else:
                new.execute('INSERT INTO keys (key) VALUES (?)', (oname,));
                key_id = new.lastrowid
                new.execute('INSERT INTO factoids (added_by,added_at,fact,locked) VALUES ("MTecknology",?,?,0)', (oadd, oval.strip(),))
                fact_id = new.lastrowid
                new.execute('INSERT INTO relations (key_id,fact_id,usage_count) VALUES (?, ?, ?)', (key_id, fact_id, opop,))
