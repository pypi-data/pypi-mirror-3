# Copyright (C) 2012  Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Synchronous client for pkgme-service."""

import json
from pprint import pformat

from httplib2 import Http

from piston_mini_client import (
    APIError,
    ExceptionFailHandler,
    PistonAPI,
    SocketError,
    returns_json,
    )

from .utils import parse_json


class PkgmeAPI(PistonAPI):
    default_service_root = 'http://localhost:8001/pkgme/api/1.0'

    @returns_json
    def build_package(self, metadata, overrides):
        data = {'metadata': metadata, 'overrides': overrides}
        return self._post('/build_package/', data=data)

    @returns_json
    def get_version(self):
        """Get the version information for the service we're talking to."""
        return self._get('/version/')


def _do_json_api_request(url, method, data):
    # What does this buy us over piston-mini-client?  parse_json gets us a
    # better error message.
    body = json.dumps(data)
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
        }
    response, content = Http().request(
        url, method=method, headers=headers, body=body)
    ExceptionFailHandler(url, method, body, headers).handle(response, content)
    return parse_json(content)


def _build_package(pkgme_service_root, metadata):
    data = {'metadata': metadata, 'overrides': {}}
    url = '%s/build_package/' % (pkgme_service_root,)
    return _do_json_api_request(url, 'POST', data)


def build_package(pkgme_service_root, metadata):
    """Send the API request to package something.

    All URLs in the metadata have to be real URLs that can be
    accessed.

    This method merely triggers the API call, it finishes well before the
    actual package is made.

    :param pkgme_service_root: The base URL of a pkgme service
    :param metadata: A metadata dictionary.  Should contain at least
        'callback_url', 'errback_url' and 'package_url' keys.
    """
    try:
        # XXX: This creates a celery task. If there's any way to hook up
        # an event for if that task fails we should do it.
        return _build_package(pkgme_service_root, metadata)
    except SocketError, e:
        raise
    except APIError, e:
        body = e.body
        data = getattr(e, 'data', "(unavailable)")
        if body is not None:
            try:
                body = parse_json(body)
            except ValueError:
                # not json
                pass
        raise RuntimeError(
            "API request failed: %s\n"
            "Data:\n"
            "%s\n"
            "Body:\n%s" % (e.msg, pformat(data), pformat(body)))
