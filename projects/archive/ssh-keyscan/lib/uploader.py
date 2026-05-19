#!/usr/bin/env python
'''
Provides functions for compiling results into flat files and uploading
those files to sharepoint.

See README.rst for information about required configuration data.

Author: Michael Lustfield
Copyright: Juniper Networks
License: GPLv3+
'''
import os
import json

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_request import ClientRequest
from office365.runtime.utilities.request_options import RequestOptions
from office365.runtime.utilities.http_method import HttpMethod

from timeout import timeout


def sp_upload(file_path, conf={}):
    '''Upload a source document to a sharepoint destination'''
    # Check for required configuration settings
    for key in ['username', 'password', 'sp_url',
                'sp_team', 'sp_site', 'sp_folder']:
        if key not in conf:
            raise Exception('Missing required config field: {}'.format(key))

    # Read file to be uploaded
    with open(file_path, 'rb') as fh:
        file_data = fh.read()
    file_name = os.path.basename(file_path)

    # Authenticate to sharepoint endpoint
    ctx_auth = AuthenticationContext(format(conf['sp_url'] + conf['sp_team']))
    if not ctx_auth.acquire_token_for_user(conf['username'], conf['password']):
        raise Exception('Failed to authenticate to sharepoint serevrs')
    request = ClientRequest(ctx_auth)

    # Build options for digest request
    digest_url = '{}{}/_api/contextinfo'.format(
        conf['sp_url'], conf['sp_team'])
    digest_options = RequestOptions(digest_url)
    digest_options.method = HttpMethod.Post
    digest_options.set_header('Accept', 'application/json;odata=verbose')
    digest_options.data = ''

    # Request digest token from sharepoint
    resp = sp_request(request, digest_options)
    digest_obj = json.loads(resp.content)
    digest = digest_obj['d']['GetContextWebInformation']['FormDigestValue']

    # Build options for upload request
    upload_tpl = "{}{}{}/_api/web/GetFolderByServerRelativeUrl('{}')/Files/add(url='{}',overwrite=true)"  # noqa: E501
    upload_url = upload_tpl.format(
        conf['sp_url'], conf['sp_team'], conf['sp_site'],
        '{}{}{}'.format(conf['sp_team'], conf['sp_site'], conf['sp_folder']),
        file_name)
    upload = RequestOptions(upload_url)
    upload.set_header('Accept', 'application/json')
    upload.set_header('X-RequestDigest', digest)
    upload.method = HttpMethod.Post
    upload.data = file_data

    # Upload file to sharepoint
    resp = sp_request(request, upload)


@timeout(10)
def sp_request(request, options):
    '''
    Returns the response to a request
    request = ClientRequest(ctx_auth)
    options = RequestOptions(url)
    '''
    return request.execute_request_direct(options)


def compile_results(source, results_file, skipped_file=None):
    '''
    Compile a list of concerning data from results directory (source)
    into a comprehensive list of actionable data (destination).
    This is the list that should be uploaded into sharepoint.
    '''
    _keylog = open(results_file, 'w') if results_file else None
    _skipped = open(skipped_file, 'w') if skipped_file else None

    for user in os.listdir(source):
        with open('{}/{}'.format(source, user), 'r') as _in:
            for line in _in.readlines():
                if _keylog and 'Non-compliant' in line:
                    _keylog.write('{} :: {}'.format(user, line))
                elif _skipped and 'directory not found' in line:
                    _skipped.write('{} :: {}'.format(user, line))
