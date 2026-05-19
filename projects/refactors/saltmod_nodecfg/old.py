# -*- coding: utf-8 -*-
'''
Custom module to lookup node config in pillar, if not found,
fall back to defaults values, if not found KeyError
'''
from __future__ import absolute_import

import logging

# Import salt libs
import salt
import salt.utils
from salt.defaults import DEFAULT_TARGET_DELIM
log = logging.getLogger(__name__)

def get(key, default=KeyError, default_lookup=True, missing_ok=False):
    delimiter = DEFAULT_TARGET_DELIM
    node_id = __grains__['id']
    node_key = ':'.join(("nodes", node_id, key))
    defaults_key = DEFAULT_TARGET_DELIM.join(("nodes{}defaults".format(DEFAULT_TARGET_DELIM), key))

    log.debug("Node CFG Module: {0}/{1}".format(node_key, defaults_key))

    ret = salt.utils.traverse_dict_and_list(__pillar__, node_key, KeyError, delimiter)
    log.debug("Node Lookup key ({0}): {1}".format(node_key, ret))

    if default_lookup is True:
        if ret is KeyError or ret is None:
            ret = salt.utils.traverse_dict_and_list(__pillar__, defaults_key, KeyError, delimiter)
            log.debug("Default Lookup key ({0}): {1}".format(defaults_key, ret))
    else:
        log.debug("skipping default lookup.")

    # assign the default value because we found nothing
    if ret is KeyError and default is not KeyError:
        ret = default

    # if we don't pass a default value, we stop because it's a good guess that the lookup key is wrong
    # and we'll want to know
    if ret is KeyError and not missing_ok:
        raise KeyError("Node pillar keys not found: {0} or {1}".format(node_key, defaults_key))

    return ret
