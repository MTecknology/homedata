#!/usr/bin/env python
'''
Custom module to look up node config in pillar, if not found,
fall back to defaults values, if not found then return None.
'''


##
# TODO:
# - This should return None when nothing is found
# - missing_ok should be removed; replace with default=None
# ^^ requires first updating states
##
def get(key, default=KeyError, default_lookup=True, missing_ok=False):
    result = __salt__['pillar.get']('nodes:{}:{}'.format(__grains__['id'], key), 'not-found')
    if result == 'not-found' and default_lookup:
        result = __salt__['pillar.get']('nodes:defaults:{}'.format(key), default)
    elif result == 'not-found':
        result = default

    if result is KeyError and not missing_ok:
        # legacy logic: assume at this point that the lookup key is probably wrong
        raise KeyError("Node pillar keys not found: {0}".format(key))

    return result
