#!/usr/bin/env python
#
# rpclib - Copyright (C) Spyne contributors.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#

import unittest

from rpclib.client.http import HttpClient
from rpclib.test.interop._test_soap_client_base import SpyneClientTestBase
from rpclib.test.interop.server.soap_http_basic import soap_application
from rpclib.util.etreeconv import root_dict_to_etree

class TestSpyneHttpClient(SpyneClientTestBase, unittest.TestCase):
    def setUp(self):
        SpyneClientTestBase.setUp(self, 'http')

        self.client = HttpClient('http://localhost:9754/', soap_application)
        self.ns = "rpclib.test.interop.server"


if __name__ == '__main__':
    unittest.main()
