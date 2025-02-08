# prettyfmt

`prettyfmt` is a tiny library to make your outputs, logs, and
`__str__()` representations slightly more beautiful.

It offers simple but general functions for formatting and abbreviating
objects and dataclasses, dicts, words and phrases, filenames, titles, long
strings, timestamps, ages, and sizes.

Simply a more convenient wrapper around `humanize`, `humanfriendly`, and `strif`.

```python
from prettyfmt import *

# Simple abbreviations of objects:
abbrev_obj({"a": "very " * 100 + "long", "b": 23})
🢂 "{a='very very very very very very very very very very very very ver…', b=23}"

# Abbreviate but don't break words. Combine with slugifiers.
abbrev_on_words("very " * 100 + "long", 30)
🢂 'very very very very very very…'

# My favorite, very good for abbreviating a long title to get a shorter one,
# or good filename.
abbrev_phrase_in_middle("very " * 100 + "long", 40)
🢂 'very very very very … very very very long'

# Ages in seconds or deltas.
fmt_age(60 * 60 * 24 * 23)
🢂 '3 weeks and 2 days ago'

fmt_age(60 * 60 *24 * 23, brief=True)
🢂 '3w ago'

# Sizes
fmt_size_human(12000000)
🢂 '11.4M'

fmt_size_dual(12000000)
🢂 '11.4M (12000000 bytes)'

# Helpful making __str__() methods or printing output:
fmt_words("Hello", None, "", "world!")
🢂 'Hello world!'

fmt_paras(fmt_words("Hello", "world!"), "", "Goodbye.")
🢂 'Hello world!\n\nGoodbye.'

# Example of `abbrev_obj` to customize __str__().
# Allows sorting and truncating based on key and value.
@dataclass
class MyThing:
   file_path: Path
   title: str
   url: str
   body: str

   def __str__(self) -> str:
      return abbrev_obj(
            self,
            # Put an abbreviated title first, then the file path, then the url.
            key_filter={
               "title": 64,
               "file_path": 0,
               "url": 128,
            },
      )

```

See pydoc for details.