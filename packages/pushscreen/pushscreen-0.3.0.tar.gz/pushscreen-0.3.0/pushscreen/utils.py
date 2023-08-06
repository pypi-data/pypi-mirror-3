# Copied from Django source
# https://github.com/django/django/blob/master/django/utils/functional.py

def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*(args+moreargs), **dict(kwargs, **morekwargs))
    return _curried
