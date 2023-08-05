__doc__ = u"""
    >>> s = Spam()
    >>> s.get_tons()
    17
    >>> s.set_tons(42)
    >>> s.get_tons()
    42
    >>> s = None
    42 tons of spam is history.
"""

cdef class Spam:

    cdef int tons

    def __cinit__(self):
        self.tons = 17

    def __dealloc__(self):
        print self.tons, u"tons of spam is history."

    def get_tons(self):
        return self.tons

    def set_tons(self, x):
        self.tons = x
