
import functools

class Cofunction(object):

    def __init__(self, iterator):
        self.__iterator = iterator
        self.__iterator.send(None)

    def __iter__(self):
        return self.__iterator

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            try:
                self.__iterator.send(None)
            except StopIteration:
                pass
            else:
                raise RuntimeError('generator did not finish like expected')

    def __call__(self, value):
        return self.__iterator.send(value)

    def map(self, iterable):
        return map(self.__iterator.send, iterable)


def cofunction(func):

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return Cofunction(func(*args, **kwargs))

    return wrapped
