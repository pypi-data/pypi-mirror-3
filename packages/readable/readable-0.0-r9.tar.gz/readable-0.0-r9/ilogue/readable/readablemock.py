#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

# wrapper for pymock

from ilogue.readable.assertableobject import AssertableObject
from ilogue.readable.assertablemethod import AssertableMethod
from ilogue.readable.configurablemethod import ConfigurableMethod
from ilogue.readable.assertableresponse import AssertableResponse
from ilogue.readable.assertableassertion import AssertableAssertion
from ilogue.readable.AssertableContext import AssertableContext
from ilogue.readable.AssertableFileDownload import AssertableFileDownload


def assertObject(val):
    return AssertableObject(val)


def assertMethod(methodMock):
    return AssertableMethod(methodMock)


def assertContext(contextProviderMock):
    return AssertableContext(contextProviderMock)


def setupMethod(methodMock):
    return ConfigurableMethod(methodMock)


def assertResponse(response=None, content = None):
    return AssertableResponse(response,content)


def assertionMethod(method):
    return AssertableAssertion(method)


if __name__ == '__main__':
    print(__doc__)
