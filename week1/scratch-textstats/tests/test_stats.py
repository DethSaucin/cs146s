from textstats.stats import top_words, unique_words, word_count
from textstats.tokens import words


def test_words_lowercases_and_strips_punctuation():
    assert words("Hello, World! 42 times") == ["hello", "world", "times"]


def test_word_count():
    assert word_count("the cat and the hat") == 5


def test_top_words():
    assert top_words("the cat and the hat", n=1) == [("the", 2)]


def test_unique_words():
    assert unique_words("the cat and the hat") == 4
    assert unique_words("The THE the") == 1
    assert unique_words("a a a b b b") == 2
    assert unique_words("") == 0
