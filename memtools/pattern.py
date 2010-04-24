#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pattern.py
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



from functools import wraps
from hashlib import md5
import logging

class Memoized(object):
    """ This class wraps a normal callable and returns a memoized callable
        with a "memo" storage. End users are not intended to know what happens
        inside this class, neither they should know about it.

    """

    def __init__(self, f, memo, hashing_function=md5, debug=False):
        self.__f = f
        self.__memo = memo
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memorzed Callable %s" % f.__name__)
        if debug:
            self.log.setLevel(logging.DEBUG)
        self.hashing_function = hashing_function

    def __create_key(self, f, *args, **kwargs):
#       TODO: Is there another way to create a key?
        the_hash = self.hashing_function(f.__name__)
        for arg in args:
            the_hash.update(str(arg))
        the_hash.update("|")
        for key, val in kwargs.iteritems():
            the_hash.update("%s:%s;".__mod__(key, val))
        return the_hash.hexdigest()

    def __call__(self, *args, **kwargs):
        key = self.__create_key(self.__f, args, kwargs)
        self.log.debug("Calling memoized value %s", key)
        try:
            return self.__memo[key]
        except KeyError:
            self.log.debug("No key %s found. Calculating value...", key)
            val = self.__f(*args, **kwargs)
            self.__memo[key] = val
            return val


class memoize(object):
    """
        The memoize decorator takes a Memory (or Memory-compatible) object
        and masks the Memoized decorator to keep the original signature
        clean.

        Use of this decorator is deprecated since Memory objects implement
        the same functionality in their __call__ methods.
    """

    def __init__(self, memory, debug=False):
        self._memory = memory
        self.debug = debug

    def __call__(self, f):
        memo = Memoized(f, self._memory, self.debug)
        wraps(f)(memo)
        return memo
