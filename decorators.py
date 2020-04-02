from time import perf_counter
from functools import wraps
from urllib.parse import urlparse


class Timer:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        start = perf_counter()
        self.value = self.function(*args, **kwargs)
        self.elapsed = float(f"{(perf_counter() - start):.2f}")
        self.string_elapsed = f"finished in: {self.elapsed}"
        self.string = f"{self.function.__name__!r} {self.string_elapsed}"
        self.printer()
        return self.value

    def printer(self):
        print(self.string)


class ResponseTimer(Timer):
    def printer(self):
        parsed = urlparse(self.value.url)
        endpoint = parsed.path
        if parsed.params:
            endpoint += parsed.params
        if parsed.query:
            endpoint += parsed.query
        print(f"{self.value.status_code}@{endpoint!r} {self.string_elapsed}")


def conditional_decorator(decoration, member):
    def decorator(method):
        predecorated = decoration(method)
        @wraps(method)
        def wrapper(*args, **kwargs):
            self = args[0]
            condition = getattr(self, member)
            if not condition:
                return method(*args, **kwargs)
            return predecorated(*args, **kwargs)
        return wrapper
    return decorator
