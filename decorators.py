from time import perf_counter
from functools import wraps


def timer(function):
    @wraps(function)
    def wrapper_timer(*args, **kwargs):
        start = perf_counter()
        value = function(*args, **kwargs)
        elapsed = float(f"{(perf_counter() - start):.2f}")
        print(f'{function.__name__!r} finished in: {elapsed}')
        return value
    return wrapper_timer


class Timer:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        start = perf_counter()
        self.value = self.function(*args, **kwargs)
        self.elapsed = float(f"{(perf_counter() - start):.2f}")
        self.string = f"{self.function.__name__!r} finished in: {self.elapsed}"
        self.printer()
        return self.value

    def printer(self):
        print(self.string)


class ResponseTimer(Timer):
    def printer(self):
        print(f"{self.value.status_code} {self.string}")


def sleeper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f'sleeping for {args[0]} secs')
        function(args[0])
    return wrapper


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