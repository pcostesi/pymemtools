#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       redis.py
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
#       * Neither the name of the  nor the names of its
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

from redis import Redis as RedisClient
import logging
from memtools.protocols import Memory, MemoryPool
from memtools.storages import NotSet, OutOfBounds

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads


class RedisMemory(Memory):
    """
        Memory gateway to a Redis server
    """

    def __init__(self, expire=None, debug=False,
                *args, **kwargs):
        """
            :param servers: List of servers to use. Please, read
            redis.Redis help.

        """
        self._client = RedisClient(*args, **kwargs)
        self._expire = expire
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Redis-Gateway")
        if debug:
            self.log.setLevel(logging.DEBUG)

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        value = self._client.get(key)
        if value is None:
            raise KeyError
        else:
            value = loads(str(value))
        self.log.debug("Key %s returned %s", key, value)
        return value

    def __setitem__(self, key, value):
        self.log.debug("Setting key %s to %s", key, value)
        self._client.set(key, dumps(value))
        if self._expire:
            self._client.expire(key, self._expire)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        if self._client.delete(key) == 0:
            raise KeyError

    def expire(self, key, time):
        self.log.debug("Setting expire time to %s seconds for key %s",
                time, key)
        self._client.expire(key, time)

    def __getattr__(self, attr):
        redis_attr = getattr(self._client, attr)
        return redis_attr

