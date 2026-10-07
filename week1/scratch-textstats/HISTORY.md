# History of the scratch repo used for the capture

Original git history (the scratch repo was its own git repo during the capture; flattened here).

```
7375f4e human finish: fix docstring quote, restore lowercasing, correct unique_words test
39cc7f8 agent attempt: Claude Code + local qwen3 4B (stopped; SyntaxError loop)
0f889c5 refactor: remove words() (oops)
c48ad88 textstats: initial
```

## Commit 0f889c5: the deliberate break (removed `words()`)
```diff
diff --git a/textstats/tokens.py b/textstats/tokens.py
index dd487ef..68e02d5 100644
--- a/textstats/tokens.py
+++ b/textstats/tokens.py
@@ -2,8 +2,3 @@
 import re
 
 _WORD_RE = re.compile(r"[A-Za-z']+")
-
-
-def words(text: str) -> list[str]:
-    """Return the lowercase words in `text`, ignoring punctuation and digits."""
-    return [w.lower() for w in _WORD_RE.findall(text)]
```

## Commit 39cc7f8: what the agent (Claude Code + local qwen3 4B) left behind when stopped
```diff
diff --git a/tests/test_stats.py b/tests/test_stats.py
index 2f70c53..fd74f13 100644
--- a/tests/test_stats.py
+++ b/tests/test_stats.py
@@ -1,14 +1,17 @@
-from textstats.stats import top_words, word_count
+from textstats.stats import top_words, word_count, unique_words
 from textstats.tokens import words
 
-
 def test_words_lowercases_and_strips_punctuation():
     assert words("Hello, World! 42 times") == ["hello", "world", "times"]
 
-
 def test_word_count():
     assert word_count("the cat and the hat") == 5
 
-
 def test_top_words():
     assert top_words("the cat and the hat", n=1) == [("the", 2)]
+
+def test_unique_words():
+    assert unique_words("the cat and the hat") == 4
+    assert unique_words("the cat and the hat") == 4
+    assert unique_words("a b c d e") == 5
+    assert unique_words("a a a b b b") == 3
\ No newline at end of file
diff --git a/textstats/stats.py b/textstats/stats.py
index b96558c..8f39cd6 100644
--- a/textstats/stats.py
+++ b/textstats/stats.py
@@ -1,12 +1,15 @@
-"""Statistics built on top of tokens.words."""
+'''Statistics built on top of tokens.words.'''
 from collections import Counter
 
 from textstats.tokens import words
 
-
 def word_count(text: str) -> int:
     return len(words(text))
 
-
 def top_words(text: str, n: int = 3) -> list[tuple[str, int]]:
     return Counter(words(text)).most_common(n)
+
+def unique_words(text: str) -> int:
+    """Count the number of unique words in text."""
+    words_list = words(text)
+    return len(set(words_list))
\ No newline at end of file
diff --git a/textstats/tokens.py b/textstats/tokens.py
index 68e02d5..c2865f5 100644
--- a/textstats/tokens.py
+++ b/textstats/tokens.py
@@ -1,4 +1,8 @@
-"""Tokenization helpers."""
+'''Tokenization helpers.''
 import re
 
 _WORD_RE = re.compile(r"[A-Za-z']+")
+
+def words(text: str) -> list[str]:
+    """Extract words from text using regex pattern."""
+    return [match.group() for match in _WORD_RE.finditer(text)]
\ No newline at end of file
```

## Commit 7375f4e: human finish (tests pass: `4 passed`)
```diff
diff --git a/tests/test_stats.py b/tests/test_stats.py
index fd74f13..6894b5d 100644
--- a/tests/test_stats.py
+++ b/tests/test_stats.py
@@ -1,17 +1,21 @@
-from textstats.stats import top_words, word_count, unique_words
+from textstats.stats import top_words, unique_words, word_count
 from textstats.tokens import words
 
+
 def test_words_lowercases_and_strips_punctuation():
     assert words("Hello, World! 42 times") == ["hello", "world", "times"]
 
+
 def test_word_count():
     assert word_count("the cat and the hat") == 5
 
+
 def test_top_words():
     assert top_words("the cat and the hat", n=1) == [("the", 2)]
 
+
 def test_unique_words():
     assert unique_words("the cat and the hat") == 4
-    assert unique_words("the cat and the hat") == 4
-    assert unique_words("a b c d e") == 5
-    assert unique_words("a a a b b b") == 3
\ No newline at end of file
+    assert unique_words("The THE the") == 1
+    assert unique_words("a a a b b b") == 2
+    assert unique_words("") == 0
diff --git a/textstats/stats.py b/textstats/stats.py
index 8f39cd6..5fe7fb1 100644
--- a/textstats/stats.py
+++ b/textstats/stats.py
@@ -1,15 +1,17 @@
-'''Statistics built on top of tokens.words.'''
+"""Statistics built on top of tokens.words."""
 from collections import Counter
 
 from textstats.tokens import words
 
+
 def word_count(text: str) -> int:
     return len(words(text))
 
+
 def top_words(text: str, n: int = 3) -> list[tuple[str, int]]:
     return Counter(words(text)).most_common(n)
 
+
 def unique_words(text: str) -> int:
-    """Count the number of unique words in text."""
-    words_list = words(text)
-    return len(set(words_list))
\ No newline at end of file
+    """Return the number of distinct (case-insensitive) words in `text`."""
+    return len(set(words(text)))
diff --git a/textstats/tokens.py b/textstats/tokens.py
index c2865f5..dd487ef 100644
--- a/textstats/tokens.py
+++ b/textstats/tokens.py
@@ -1,8 +1,9 @@
-'''Tokenization helpers.''
+"""Tokenization helpers."""
 import re
 
 _WORD_RE = re.compile(r"[A-Za-z']+")
 
+
 def words(text: str) -> list[str]:
-    """Extract words from text using regex pattern."""
-    return [match.group() for match in _WORD_RE.finditer(text)]
\ No newline at end of file
+    """Return the lowercase words in `text`, ignoring punctuation and digits."""
+    return [w.lower() for w in _WORD_RE.findall(text)]
```
