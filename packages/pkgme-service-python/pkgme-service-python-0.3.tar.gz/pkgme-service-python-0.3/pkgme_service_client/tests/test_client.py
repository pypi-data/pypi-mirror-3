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

"""Tests for pkgme_service_client.client."""

from mock import patch
from piston_mini_client import APIError
from testtools import TestCase

from pkgme_service_client.client import build_package


class TestClient(TestCase):

    @patch('httplib2.Http.request')
    def test_build_package_failure(self, mock_request):
        message = "something went wrong"
        body = "a body"
        api_error = APIError(message, body=body)
        mock_request.side_effect = api_error
        metadata = {}
        # Raises a runtime error without crashing
        e = self.assertRaises(
            RuntimeError, build_package, 'http://example', metadata)
        self.assertTrue(mock_request.called)
        self.assertIn(message, str(e))
        self.assertIn(body, str(e))
