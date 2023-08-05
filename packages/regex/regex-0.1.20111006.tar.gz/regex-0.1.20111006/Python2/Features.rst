Introduction
------------

This new regex implementation is intended eventually to replace Python's current re module implementation.

For testing and comparison with the current 're' module the new implementation is in the form of a module called 'regex'.

Also included are the compiled binary .pyd files for Python 2.5-2.7 and Python 3.1-3.2 on 32-bit Windows.


Change of behaviour
-------------------

**Old vs new behaviour**

This module has 2 behaviours:

Version 0 behaviour (old behaviour, compatible with the current 're' module):

    Indicated by the ``VERSION0`` or ``V0`` flag, or ``(?V0)`` in the pattern.

    ``.split`` won't split a string at a zero-width match.

    Inline flags apply to the entire pattern, and they can't be turned off.

    Only simple sets are supported.

    Case-insensitive matches in Unicode use simple case-folding by default.

Version 1 behaviour (new behaviour, different from the current 're' module):

    Indicated by the ``VERSION1`` or ``V1`` flag, or ``(?V1)`` in the pattern.

    ``.split`` will split a string at a zero-width match.

    Inline flags apply to the end of the group or pattern, and they can be turned off.

    Nested sets and set operations are supported.

    Case-insensitive matches in Unicode use full case-folding by default.

If no version is specified, the regex module will default to ``regex.DEFAULT_VERSION``. In the short term this will be ``VERSION0``, but in the longer term it will be ``VERSION1``.

**Note**: the ``VERSION1`` flag replaces the ``NEW`` flag in previous versions of this module. The ``NEW`` flag is still supported in this release, but will be removed. The decision about versions and making the change was made after discussion in the python-dev list.

**Case-insensitive matches in Unicode**

The regex module supports both simple and full case-folding for case-insensitive matches in Unicode. Use of full case-folding can be turned on using the ``FULLCASE`` or ``F`` flag, or ``(?f)`` in the pattern. Please note that this flag affects how the ``IGNORECASE`` flag works; the ``FULLCASE`` flag itself does not turn on case-insensitive matching.

In the version 0 behaviour, the flag is off by default.

In the version 1 behaviour, the flag is on by default.

**Nested sets and set operations**

Previous releases supported both simple and nested sets at the same time. This occasionally lead to problems in practice when an unescaped "[" in a simple set was interpreted as being the start of a nested set. Therefore nested sets and set operations are now supported only in the version 1 behaviour.

Version 0 behaviour: only simple sets are supported.

Version 1 behaviour: nested sets and set operations are supported.

**Fuzzy matching**

When performing fuzzy matching, the previous release of this module searched for the best match. This proved to be confusing in practice when used with ``.findall``, for example.

Therefore, the default behaviour has been changed to search for the first match which meets the constraints, and a new ``BESTMATCH`` flag has been added to force it to search for the best match instead (the previous behaviour).


Flags
-----

There are 2 kinds of flag: scoped and global. Scoped flags can apply to only part of a pattern and can be turned on or off; global flags apply to the entire pattern and can only be turned on.

The scoped flags are: ``FULLCASE``, ``IGNORECASE``, ``MULTILINE``, ``DOTALL``, ``VERBOSE``, ``WORD``.

The global flags are: ``ASCII``, ``BESTMATCH``, ``LOCALE``, ``REVERSE``, ``UNICODE``, ``VERSION0``, ``VERSION1``.

If neither the ``ASCII``, ``LOCALE`` nor ``UNICODE`` flag is specified, it will default to ``UNICODE`` if the regex pattern is a Unicode string and ``ASCII`` if it's a bytestring.

The ``BESTMATCH`` flag makes fuzzy matching search for the best match instead of the next match which meets the given constraints.


Notes on named capture groups
-----------------------------

All capture groups have a group number, starting from 1.

Groups with the same group name will have the same group number, and groups with a different group name will have a different group number.

The same group name can be used on different branches of an alternation because they are mutually exclusive, eg. ``(?P<foo>first)|(?P<foo>second)``. They will, of course, have the same group number.

Group numbers will be reused, where possible, across different branches of a branch reset, eg. ``(?|(first)|(second))`` has only group 1. If capture groups have different group names then they will, of course, have different group numbers, eg. ``(?|(?P<foo>first)|(?P<bar>second))`` has group 1 ("foo") and group 2 ("bar").


Multithreading
--------------

The regex module releases the GIL during matching on instances of the built-in (immutable) string classes, enabling other Python threads to run concurrently. It is also possible to force the regex module to release the GIL during matching by calling the matching methods with the keyword argument ``concurrent=True``. The behaviour is undefined if the string changes during matching, so use it *only* when it is guaranteed that that won't happen.


Building for 64-bits
--------------------

If the source files are built for a 64-bit target then the string positions will also be 64-bit. (The 're' module appears to limit string positions to 32 bits, even on a 64-bit build.)


Unicode
-------

This module supports Unicode 6.0.0.

Full Unicode case-folding is supported.


Additional features
-------------------

The issue numbers relate to the Python bug tracker, except where listed as "Hg issue".

* Full Unicode case-folding is supported.

    When performing case-insensitive matches in Unicode, regex uses full case-folding.

    Examples (in Python 3):

        >>> regex.match(r"(?i)strasse", "stra\N{LATIN SMALL LETTER SHARP S}e").span()
        (0, 6)
        >>> regex.match(r"(?i)stra\N{LATIN SMALL LETTER SHARP S}e", "STRASSE").span()
        (0, 7)

* Approximate "fuzzy" matching (Hg issue 12)

    Regex usually attempts an exact match, but sometimes an approximate, or "fuzzy", match is needed, for those cases where the text being searched may contain errors in the form of inserted, deleted or substituted characters.

    A fuzzy regex specifies which types of errors are permitted, and, optionally, the maximum permitted number of each type.

    The 3 types of error are:

    * Insertion, indicated by "i"

    * Deletion, indicated by "d"

    * Substitution, indicated by "s"

    In addition, "e" indicates any type of error.

    The fuzziness of a regex item is specified between "{" and "}" after the item.

    Examples:

    ``foo`` match "foo" exactly

    ``(?:foo){i}`` match "foo", permitting insertions

    ``(?:foo){d}`` match "foo", permitting deletions

    ``(?:foo){s}`` match "foo", permitting substitutions

    ``(?:foo){i,s}`` match "foo", permitting insertions and substitutions

    ``(?:foo){e}`` match "foo", permitting errors

    If a certain type of error is specified, then any type not specified will **not** be permitted.

    In the following examples I'll omit the item and write only the fuzziness.

    ``{i<=3}`` permit at most 3 insertions, but no other types

    ``{d<=3}`` permit at most 3 deletions, but no other types

    ``{s<=3}`` permit at most 3 substitutions, but no other types

    ``{i<=1,s<=2}`` permit at most 1 insertion and at most 2 substitutions, but no deletions

    ``{e<=3}`` permit at most 3 errors

    ``{i<=2,d<=2,e<=3}`` permit at most 2 insertions, at most 2 deletions, at most 3 errors in total, but no substitutions

    It's also possible to state the costs of each type of error and the maximum permitted total cost.

    Examples:

    ``{2i+2d+1s<=4}`` each insertion costs 2, each deletion costs 2, each substitution costs 1, the total cost must not exceed 4

    ``{i<=1,d<=1,s<=1,2i+2d+1s<=4}`` at most 1 insertion, at most 1 deletion, at most 1 substitution; each insertion costs 2, each deletion costs 2, each substitution costs 1, the total cost must not exceed 4

    You can also use "<" instead of "<=" if you want an exclusive maximum:

    ``{e<=3}`` permit up to 3 errors

    ``{e<4}`` permit fewer than 4 errors

    By default, fuzzy matching searches for the first match which meets the given constraints, but turning on the ``BESTMATCH`` flag will make it search for the best match instead.

* Named lists (Hg issue 11)

    ``\L<name>``

    There are occasions where you may want to include a list (actually, a set) of options in a regex.

    One way is to build the pattern like this::

        p = regex.compile(r"first|second|third|fourth|fifth")

    but if the list is large, parsing the resulting regex can take considerable time, and care must also be taken that the strings are properly escaped if they contain any character which has a special meaning in a regex, and that if there is a shorter string which occurs initially in a longer string that the longer string is listed before the shorter one, for example, "cats" before "cat".

    The new alternative is to use a named list::

        option_set = ["first", "second", "third", "fourth", "fifth"]
        p = regex.compile(r"\L<options>", options=option_set)

    The order of the items is irrelevant, they are treated as a set. The named lists are available as the ``.named_lists`` attribute of the pattern object ::

        >>> print(p.named_lists)
        {'options': frozenset({'second', 'fifth', 'fourth', 'third', 'first'})}

* Start and end of word

    ``\m`` matches at the start of a word.

    ``\M`` matches at the end of a word.

    Compare with ``\b``, which matches at the start or end of a word.

* Unicode line separators

    Normally the only line separator is ``\n`` (``\x0A``), but if the ``WORD`` flag is turned on then the line separators are the pair ``\x0D\x0A``, and ``\x0A``, ``\x0B``, ``\x0C`` and ``\x0D``, plus ``\x85``, ``\u2028`` and ``\u2029`` when working with Unicode.

    This affects the regex dot ``"."``, which, with the ``DOTALL`` flag turned off, matches any character except a line separator. It also affects the line anchors ``^`` and ``$`` (in multiline mode).

* Set operators

    **Version 1 behaviour only**

    Set operators have been added, and a set ``[...]`` can include nested sets.

    The operators, in order of increasing precedence, are:

        ``||`` for union ("x||y" means "x or y")

        ``~~`` (double tilde) for symmetric difference ("x~~y" means "x or y, but not both")

        ``&&`` for intersection ("x&&y" means "x and y")

        ``--`` (double dash) for difference ("x--y" means "x but not y")

    Implicit union, ie, simple juxtaposition like in ``[ab]``, has the highest precedence. Thus, ``[ab&&cd]`` is the same as ``[[a||b]&&[c||d]]``.

    Examples:

        ``[ab]`` # Set containing 'a' and 'b'

        ``[a-z]`` # Set containing 'a' .. 'z'

        ``[[a-z]--[qw]]`` # Set containing 'a' .. 'z', but not 'q' or 'w'

        ``[a-z--qw]`` # Same as above

        ``[\p{L}--QW]`` # Set containing all letters except 'Q' and 'W'

        ``[\p{N}--[0-9]]`` # Set containing all numbers except '0' .. '9'

        ``[\p{ASCII}&&\p{Letter}]`` # Set containing all characters which are ASCII and letter

* regex.escape (issue #2650)

    regex.escape has an additional keyword parameter ``special_only``. When True, only 'special' regex characters, such as '?', are escaped.

    Examples:

        >>> regex.escape("foo!?")
        'foo\\!\\?'
        >>> regex.escape("foo!?", special_only=True)
        'foo!\\?'

* Repeated captures (issue #7132)

    A match object has additional methods which return information on all the successful matches of a repeated capture group. These methods are:

    ``matchobject.captures([group1, ...])``

        Returns a list of the strings matched in a group or groups. Compare with ``matchobject.group([group1, ...])``.

    ``matchobject.starts([group])``

        Returns a list of the start positions. Compare with ``matchobject.start([group])``.

    ``matchobject.ends([group])``

        Returns a list of the end positions. Compare with ``matchobject.end([group])``.

    ``matchobject.spans([group])``

        Returns a list of the spans. Compare with ``matchobject.span([group])``.

    Examples:

        >>> m = regex.search(r"(\w{3})+", "123456789")
        >>> m.group(1)
        '789'
        >>> m.captures(1)
        ['123', '456', '789']
        >>> m.start(1)
        6
        >>> m.starts(1)
        [0, 3, 6]
        >>> m.end(1)
        9
        >>> m.ends(1)
        [3, 6, 9]
        >>> m.span(1)
        (6, 9)
        >>> m.spans(1)
        [(0, 3), (3, 6), (6, 9)]

* Atomic grouping (issue #433030)

    ``(?>...)``

    If the following pattern subsequently fails, then the subpattern as a whole will fail.

* Possessive quantifiers.

    ``(?:...)?+`` ; ``(?:...)*+`` ; ``(?:...)++`` ; ``(?:...){min,max}+``

    The subpattern is matched up to 'max' times. If the following pattern subsequently fails, then all of the repeated subpatterns will fail as a whole. For example, ``(?:...)++`` is equivalent to ``(?>(?:...)+)``.

* Scoped flags (issue #433028)

    ``(?flags-flags:...)``

    The flags will apply only to the subpattern. Flags can be turned on or off.

* Inline flags (issue #433024, issue #433027)

    ``(?flags-flags)``

    Version 0 behaviour: the flags apply to the entire pattern, and they can't be turned off.

    Version 1 behaviour: the flags apply to the end of the group or pattern, and they can be turned on or off.

* Repeated repeats (issue #2537)

    A regex like ``((x|y+)*)*`` will be accepted and will work correctly, but should complete more quickly.

* Definition of 'word' character (issue #1693050)

    The definition of a 'word' character has been expanded for Unicode. It now conforms to the Unicode specification at ``http://www.unicode.org/reports/tr29/``. This applies to ``\w``, ``\W``, ``\b`` and ``\B``.

* Groups in lookahead and lookbehind (issue #814253)

    Groups and group references are permitted in both lookahead and lookbehind.

* Variable-length lookbehind

    A lookbehind can match a variable-length string.

* Correct handling of charset with ignore case flag (issue #3511)

    Ranges within charsets are handled correctly when the ignore-case flag is turned on.

* Unmatched group in replacement (issue #1519638)

    An unmatched group is treated as an empty string in a replacement template.

* 'Pathological' patterns (issue #1566086, issue #1662581, issue #1448325, issue #1721518, issue #1297193)

    'Pathological' patterns should complete more quickly.

* Flags argument for regex.split, regex.sub and regex.subn (issue #3482)

    ``regex.split``, ``regex.sub`` and ``regex.subn`` support a 'flags' argument.

* Pos and endpos arguments for regex.sub and regex.subn

    ``regex.sub`` and ``regex.subn`` support 'pos' and 'endpos' arguments.

* 'Overlapped' argument for regex.findall and regex.finditer

    ``regex.findall`` and ``regex.finditer`` support an 'overlapped' flag which permits overlapped matches.

* Unicode escapes (issue #3665)

    The Unicode escapes ``\uxxxx`` and ``\Uxxxxxxxx`` are supported.

* Large patterns (issue #1160)

    Patterns can be much larger.

* Zero-width match with regex.finditer (issue #1647489)

    ``regex.finditer`` behaves correctly when it splits at a zero-width match.

* Zero-width split with regex.split (issue #3262)

    Version 0 behaviour: a string won't be split at a zero-width match.

    Version 1 behaviour: a string will be split at a zero-width match.

* Splititer

    ``regex.splititer`` has been added. It's a generator equivalent of ``regex.split``.

* Subscripting for groups

    A match object accepts access to the captured groups via subscripting and slicing:

    >>> m = regex.search(r"(?P<before>.*?)(?P<num>\d+)(?P<after>.*)", "pqr123stu")
    >>> print m["before"]
    pqr
    >>> print m["num"]
    123
    >>> print m["after"]
    stu
    >>> print len(m)
    4
    >>> print m[:]
    ('pqr123stu', 'pqr', '123', 'stu')

* Named groups

    Groups can be named with ``(?<name>...)`` as well as the current ``(?P<name>...)``.

* Group references

    Groups can be referenced within a pattern with ``\g<name>``. This also allows there to be more than 99 groups.

* Named characters

    ``\N{name}``

    Named characters are supported. (Note: only those known by Python's Unicode database are supported.)

* Unicode codepoint properties, including scripts and blocks

    ``\p{property=value}``; ``\P{property=value}``; ``\p{value}`` ; ``\P{value}``

    Many Unicode properties are supported, including blocks and scripts. ``\p{property=value}`` or ``\p{property:value}`` matches a character whose property ``property`` has value ``value``. The inverse of ``\p{property=value}`` is ``\P{property=value}`` or ``\p{^property=value}``.

    If the short form ``\p{value}`` is used, the properties are checked in the order: ``General_Category``, ``Script``, ``Block``, binary property:

    1. ``Latin``, the 'Latin' script (``Script=Latin``).

    2. ``Cyrillic``, the 'Cyrillic' script (``Script=Cyrillic``).

    3. ``BasicLatin``, the 'BasicLatin' block (``Block=BasicLatin``).

    4. ``Alphabetic``, the 'Alphabetic' binary property (``Alphabetic=Yes``).

    A short form starting with ``Is`` indicates a script or binary property:

    1. ``IsLatin``, the 'Latin' script (``Script=Latin``).

    2. ``IsCyrillic``, the 'Cyrillic' script (``Script=Cyrillic``).

    3. ``IsAlphabetic``, the 'Alphabetic' binary property (``Alphabetic=Yes``).

    A short form starting with ``In`` indicates a block property:

    1. ``InBasicLatin``, the 'BasicLatin' block (``Block=BasicLatin``).

    2. ``InCyrillic``, the 'Cyrillic' block (``Block=Cyrillic``).

* POSIX character classes

    ``[[:alpha:]]``; ``[[:^alpha:]]``

    POSIX character classes are supported. This is actually treated as an alternative form of ``\p{...}``.

* Search anchor

    ``\G``

    A search anchor has been added. It matches at the position where each search started/continued and can be used for contiguous matches or in negative variable-length lookbehinds to limit how far back the lookbehind goes:

    >>> regex.findall(r"\w{2}", "abcd ef")
    ['ab', 'cd', 'ef']
    >>> regex.findall(r"\G\w{2}", "abcd ef")
    ['ab', 'cd']

    1. The search starts at position 0 and matches 2 letters 'ab'.

    2. The search continues at position 2 and matches 2 letters 'cd'.

    3. The search continues at position 4 and fails to match any letters.

    4. The anchor stops the search start position from being advanced, so there are no more results.

* Reverse searching

    Searches can now work backwards:

    >>> regex.findall(r".", "abc")
    ['a', 'b', 'c']
    >>> regex.findall(r"(?r).", "abc")
    ['c', 'b', 'a']

    Note: the result of a reverse search is not necessarily the reverse of a forward search:

    >>> regex.findall(r"..", "abcde")
    ['ab', 'cd']
    >>> regex.findall(r"(?r)..", "abcde")
    ['de', 'bc']

* Matching a single grapheme

    ``\X``

    The grapheme matcher is supported. It now conforms to the Unicode specification at ``http://www.unicode.org/reports/tr29/``.

* Branch reset

    (?|...|...)

    Capture group numbers will be reused across the alternatives.

* Default Unicode word boundary

    The ``WORD`` flag changes the definition of a 'word boundary' to that of a default Unicode word boundary. This applies to ``\b`` and ``\B``.

* SRE engine do not release the GIL (issue #1366311)

    The regex module can release the GIL during matching (see the above section on multithreading).

    Iterators can be safely shared across threads.
