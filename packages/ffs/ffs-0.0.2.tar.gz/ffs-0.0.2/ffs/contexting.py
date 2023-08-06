"""
ffs.contexting

Helpers for writing contextmanagers
"""
import contextlib
import functools

class _GeneratorInitContextManager(contextlib.GeneratorContextManager):
    """
    Helper for @contextmaybe decorator.

    Override the initialisation of the contextlib._GeneratorContextManager
    """

    def __init__(self, func, *args, **kwds):
        self.gen = func(*args, **kwds)
        self.func, self.args, self.kwds = func, args, kwds
        self.nexted = next(self.gen)

    def _recreate_cm(self):
        # _GCM instances are one-shot context managers, so the
        # CM must be recreated each time a decorated function is
        # called
        return self.__class__(self.func, *self.args, **self.kwds)

    def __enter__(self):
        try:
            return self.nexted
        except StopIteration:
            raise RuntimeError("generator didn't yield")

def contextmaybe(func):
    """
    @contextmaybe decorator.

    Similar to contextlib.contextmanager except the __enter__ step
    happens at __init__ time.

    This means that we can optionally call it without the cleanup.

    Typical usage:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:
        some_generator(<arguments>)

    equivalent to:
        <setup>

    while this:

        with some_generator(<arguments>) as <variable>:
            <body>
        <setup>

   remains to this:

        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>

    """
    @functools.wraps(func)
    def helper(*args, **kwds):
        return _GeneratorInitContextManager(func, *args, **kwds)
    return helper
