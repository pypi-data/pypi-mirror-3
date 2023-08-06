#-*- coding: utf-8 -*-
u"""Defines the `Door` class.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from __future__ import with_statement
from threading import Lock, Event
from contextlib import contextmanager
from cocktail.modeling import getter


class Door(object):
    """An object that enables or disables concurrent access to a shared state.
    """

    _exclusive_access_interval = 0.1

    def __init__(self, lock = None):

        if lock is None:
            lock = Lock()

        self.__lock = lock
        self.__concurrency = 0
        self.__empty = Event()

    def enter(self):
        """Request clearence to begin accessing the shared state."""
        with self.__lock:
            self.__concurrency += 1
            self.__empty.clear()
    
    def leave(self):
        """Notify the end of access to the shared state."""
        with self.__lock:
            self.__concurrency -= 1
            if not self.__concurrency:
                self.__empty.set()

    def lock(self):
        """Prevent concurrent access to the shared state.
        
        The method waits until no other thread is accessing the shared state
        (ie. no one's inside) and then prevents further access to it until the
        `unlock` method is called.
        """ 
        while True:
            self.__empty.wait()
            self.__lock.acquire()
            if not self.__concurrency:
                break
            self.__lock.release()

    def unlock(self):
        """Re-enable concurrent access to the shared state after a call to
        `lock`.
        """
        self.__lock.release()

    # Implement the context manager protocol:

    def __enter__(self):
        self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.leave()

    @getter
    @contextmanager
    def locking(self):
        """A context manager that locks and unlocks the door."""
        self.lock()
        try:
            yield self
        finally:
            self.unlock()

