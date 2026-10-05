# Runtime available to every question (mirrors the Midterm 2 study guide).
from dataclasses import dataclass
from typing import Any


@dataclass
class Link:
    first: Any
    rest: Any = ()  # empty list

    def __str__(self):
        return format_link(self)


def format_link(s):
    """Display a linked list as (3 4 5); nested linked lists nest the parens."""
    items = []
    while isinstance(s, Link):
        items.append(format_link(s.first) if isinstance(s.first, Link) else str(s.first))
        s = s.rest
    return '(' + ' '.join(items) + ')'
