"""Statistics built on top of tokens.words."""
from collections import Counter

from textstats.tokens import words


def word_count(text: str) -> int:
    return len(words(text))


def top_words(text: str, n: int = 3) -> list[tuple[str, int]]:
    return Counter(words(text)).most_common(n)


def unique_words(text: str) -> int:
    """Return the number of distinct (case-insensitive) words in `text`."""
    return len(set(words(text)))
