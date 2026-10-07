"""Tokenization helpers."""
import re

_WORD_RE = re.compile(r"[A-Za-z']+")


def words(text: str) -> list[str]:
    """Return the lowercase words in `text`, ignoring punctuation and digits."""
    return [w.lower() for w in _WORD_RE.findall(text)]
