"""Simple test fixtures."""

from functools import wraps


class Context(dict):

    """Store context information for a fixture."""

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

    def __repr__(self):
        kwarg_str = ", ".join("%s=%r" % kv for kv in sorted(self.items()))
        return "%s(%s)" % (self.__class__.__name__, kwarg_str)


def with_fixture(create_fixture, **kwargs):
    """Decorate a callable with a fixture."""
    context = Context()
    fixture = create_fixture(context, **kwargs)
    if isinstance(fixture, tuple):
        setup, teardown = fixture
    else:
        setup = fixture
        teardown = lambda: None

    def wrap(func):
        """Wrap the callable."""
        @wraps(func)
        def call(*args, **kwargs):
            """Call `setup` and `teardown` before and after `func`."""
            try:
                setup()
                result = func(context, *args, **kwargs)
            finally:
                try:
                    teardown()
                finally:
                    context.clear()
            return result
        return call

    return wrap
