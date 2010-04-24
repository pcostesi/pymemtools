#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       protocols.py
#
#       Copyright 2010 Pablo Alejandro Costesich <pcostesi@alu.itba.edu.ar>
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are
#       met:
#
#       * Redistributions of source code must retain the above copyright
#         notice, this list of conditions and the following disclaimer.
#       * Redistributions in binary form must reproduce the above
#         copyright notice, this list of conditions and the following disclaimer
#         in the documentation and/or other materials provided with the
#         distribution.
#       * Neither the name of the Dev Team nor the names of its
#         contributors may be used to endorse or promote products derived from
#         this software without specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#       "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#       LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#       A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#       OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#       SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#       LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#       DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#       THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#       OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

"""
    This file defines the required protocols for most memory tools used
    in this package.

"""


from functools import wraps
from memtools.pattern import Memoized, memoize


class Memory(object):
    """
        Memory objects are key-value gateways to a database or any other kind
        of memory storage. They behave the same way dictionaries do, which
        makes it easier to mock them.

        Required methods are __getitem__, __setitem__ and __delitem__. get(),
        set() are mapped to __getitem__ and __setitem__.

        A convenience method __call__ is defined to use objects of this class
        as decorators. Doing so will apply the memoize pattern to the
        function. You can find more information in the corresponding docstring
        in __call__.

    """

    def __getitem__(self, key):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def __call__(self, f):
        """
            This is a convenience function that provides the Memory Pattern as
            a decorator and wraps it in a way transparent to the end user
            (i.e.: they will not know whether the function has been decorated
            or not). This is acomplished by using the "wrap" decorator in
            functools.

        """
        memo = Memoized(f, self)
        wraps(f)(memo)
        return memo

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value):
        self.__setitem__(key, value)


class MemoryPool(Memory):
    """
        A MemoryPool object provides an extended way of using Memory gateways.
        It holds more than one connection open, so it should be theoretically
        faster than ad-hoc connections. However, it does not necessarily imply
        that the objects in the pool are connected to different servers.

        It *must* behave like a Memory gateway too, masking the
        lock/hold/return operations inside the MemoryPool, providing a complete
        replacement for normal Memory objects.
    """

    def count(self):
        raise NotImplementedError

    def grow(self, number=1):
        raise NotImplementedError

    def shrink(self, number=1):
        raise NotImplementedError
