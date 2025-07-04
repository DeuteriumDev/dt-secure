from typing import Iterable


def flatten(xss: Iterable[Iterable]):
    return [x for xs in xss for x in xs]
