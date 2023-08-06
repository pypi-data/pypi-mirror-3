#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock
from ilogue.readable import assertionMethod

class AssertableRequestTestCase(unittest.TestCase):

    def test_returnsDocument_Fails_on_nonexisting_page(self):
        from ilogue.readable import assertRequest
        reqForNonExistPage = assertRequest('http://httpbin.org/status/404')
        (assertionMethod(reqForNonExistPage.returnsDocument)
            .fails())

    def test_returnsDocument_Succeeds_on_existing_page(self):
        from ilogue.readable import assertRequest
        reqForNonExistPage = assertRequest('http://httpbin.org/get')
        (assertionMethod(reqForNonExistPage.returnsDocument)
            .doesNotFail())


if __name__ == '__main__':
    unittest.main()
