#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Baan']
__version__ = '0.1.5'

import sys
import logging
from numbers import Number

logger = logging.getLogger('baanlib')

# this is a hack to be able to run the test cases on non-windows systems.
# otherwise, using this library on a non-windows system makes hardly any sense.
if sys.platform != 'win32':
    from mock import Mock
    Dispatch = Mock()
    assert Dispatch  # silence pyflakes
else:
    from win32com.client.dynamic import Dispatch


# Please note:
# To avoid collision with baan dll function names, inside the classes even
# "public" properties like dll_name are prefixed with '_'

class UnknownDllException(Exception):
    pass


class UnknownMethodException(Exception):
    pass


class Baan(object):
    """Wrapper class for win32com Dispatch

    It chains each attribute access until it is finally called.
    The first attribute name will be taken as the dll name,
    everything afterwards will be interpreted as part of the function name.

    >>> from baanlib import Baan
    >>> b = Baan('Baan.Application.erpln')
    >>> retval = b.dll_name.some.method.name()

    Calling the "chained attribute names" will invoke
    ParseExecFunction and return the ReturnValue of the baan object created from
    the dispatcher
    """

    def __init__(self, name, dispatcher=Dispatch):
        """Instantiate a baan object

        :param name: ole automation class name taken from the bw configuration
        :param dispatcher: Shouldn't be specified, only to be used for testing.
        """
        self._baan = dispatcher(name)
        self._baan.Timeout = 3600

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __getattr__(self, name):
        return BaanWrapper(self._baan, name)

    def close(self):
        if self._baan:
            self._baan.Quit()
            self._baan = None

    @property
    def Timeout(self):
        return self._baan.Timeout

    @Timeout.setter
    def Timeout(self, value):
        self._baan.Timeout = value

    @property
    def ReturnValue(self):
        return self._baan.ReturnValue

    @property
    def FunctionCall(self):
        return self._baan.FunctionCall

    @property
    def ReturnCall(self):
        return self._baan.ReturnCall

    @property
    def Binary(self):
        return self._baan.Binary

    @Binary.setter
    def Binary(self, value):
        self._baan.Binary = value


class BaanWrapper(object):
    def __init__(self, baanobj, name):
        self._baanobj = baanobj
        self._name = name

    @property
    def _dll_name(self):
        return self._name.split('.')[0]

    @property
    def _method_name(self):
        return '.'.join(self._name.split('.')[1:])

    def _get_calling_method(self, *args):
        method = self._method_name + '('
        for i, arg in enumerate(args):
            if isinstance(arg, Number):
                method += str(arg)
            else:
                method += '"{0}"'.format(arg)

            if not i + 1 == len(args):
                method += ", "
        method += ")"

        return method

    def __getattr__(self, name):
        return BaanWrapper(self._baanobj, self._name + "." + name)

    def __call__(self, *args):
        method = self._get_calling_method(*args)
        self._baanobj.ParseExecFunction(self._dll_name, method)
        if self._baanobj.Error == -1:
            raise UnknownDllException
        elif self._baanobj.Error == -2:
            raise UnknownMethodException
        return self._baanobj.ReturnValue
