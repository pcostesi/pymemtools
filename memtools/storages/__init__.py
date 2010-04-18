#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       __init__.py
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
Memory decorator and utilites to speed up access to computationally expensive
functions.
"""

import random, time
from memtools.protocols import Memory


#
#   AUXILIARY CLASSES
#


class NotSet(object):
    """ Empty class used to differenciate None from unsetted values in k-v
        storages that return None in both cases, like python-memcached.
    """
    pass


class OutOfBounds(Exception):
    pass


class Alzheimer(Memory):
    '''This is a mock class. Forget it.'''

    def __init__(self, disease=False, *args, **kwargs):
        self._client = {}
        if disease:
            t = Thread(target=self.__disease)
            t.start()

    def __setitem__(self, key, value):
        self._client.__setitem__(key, value)

    def __getitem__(self, key):
        return self._client.__getitem__(key)

    def __delitem__(self, key):
        self._client.__delitem__(key)

    def keys(self, string):
        a = []
        for i in self._client.keys():
            if i.startswith(string[:-1]):
                a.append(i)
        return a

    def __disease(self):
        while True:
            rand = random.uniform(1, 3600)
            time.sleep(rand)
            try:
                del self._client[self._client.keys()[int(random.uniform(0,
                            len(self._client)))]]
            except:
                pass
