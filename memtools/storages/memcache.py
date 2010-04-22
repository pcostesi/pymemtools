#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       memcache.py
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


from threading import Lock, Thread
from memcache import Client as MemcacheClient
import logging
from memtools.protocols import Memory, MemoryPool
from memtools.storages import NotSet, OutOfBounds


class MemcacheMemory(Memory):
    """
        Memory gateway to a Memcache server
    """

    def __init__(self, servers=["127.0.0.1:11211"], expire=0, debug=False):
        """
            :param servers: List of servers to use. Please, read
            memcache.Client help.
        """
        self._client = MemcacheClient(servers)
        self._expire = expire
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memcache-Gateway")
        if debug:
            self.log.setLevel(logging.DEBUG)

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        value = self._client.get(key)
        if isinstance(value, NotSet):
            return None
        elif value is None:
            raise KeyError
        else:
            return value

    def __setitem__(self, key, value):
        self.log.debug("Setting key")
        if value is None:
            value = NotSet()
        self._client.set(key, value, self._expire)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        if self._client.delete(key) == 0:
            raise KeyError


class MemcacheMemoryPool(MemoryPool):

    def __init__(self, servers=["127.0.0.1:11211"], expire=0, upper_limit=100,
            lower_limit=1, debug=False):
        super(MemcacheMemoryPool, self).__init__()
        self._clients = [MemcacheMemory(servers=servers, expire=expire) for o
                in xrange(0, abs(upper_limit + lower_limit) / 2)]
        self.__expire = expire
        self._servers = servers
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        logging.basicConfig(level=logging.WARNING)
        self.log = logging.getLogger("Memcache Pool")
        self.__debug = debug
        self.__clients_lock = Lock()
        if debug:
            self.log.setLevel(logging.DEBUG)

    def __expire_get(self):
        return self.__expire

    def __expire_set(self, value):
        if self.__expire != value:
            self.__expire = value
            for i in self._clients:
                i._expire = value

    _expire = property(__expire_get, __expire_set)

    def count(self):
        try:
            self.__clients_lock.acquire()
            return len(self._clients)
        finally:
            self.__clients_lock.release()

    def grow(self, number=1):
        self.log.debug("Adding %s new servers to the pool", number)
        self.__clients_lock.acquire()
        for i in range(number):
            self._clients.append(MemcacheMemory(self._servers, self._expire,
                    self.__debug))
        self.__clients_lock.release()

    def shrink(self, number=1):
        self.log.debug("Deleting %s servers from the pool", number)
        self.__clients_lock.acquire()
        for i in range(number):
            self._clients.pop()
        self.__clients_lock.release()

    def _claim_client(self):
        if self.count() < self.lower_limit:
            self.grow()
        try:
            self.__clients_lock.acquire()
            return self._clients.pop()
        finally:
            self.__clients_lock.release()

    def _return_client(self, client):
        if self.count() < self.upper_limit:
            self.__clients_lock.acquire()
            self._clients.append(client)
            self.__clients_lock.release()

    def __getitem__(self, key):
        self.log.debug("Accessing key %s", key)
        try:
            client = self._claim_client()
            return client[key]
        finally:
            self.__return_client(client)

    def __setitem__(self, key, value):
        self.log.debug("Setting key %s to %s", key, value)
        try:
            client = self._claim_client()
            client[key] = value
        finally:
            self._return_client(client)

    def __delitem__(self, key):
        self.log.debug("Deleting key %s", key)
        try:
            client = self._claim_client()
            client.__delitem__(key)
        finally:
            self._return_client(client)
