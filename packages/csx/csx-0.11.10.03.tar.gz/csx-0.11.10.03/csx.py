#!/usr/bin/env python3

# csx.py - Extended Cascading Stylesheets.
# Copyright (C) 2009 Zero Piraeus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""csx - Create, manipulate and convert CSX stylesheets.

CSX is a style language based on `CSS 2.1`_, with two improvements:

1. Rules may be nested inside other rules.
2. There are no at-rules (like @media or @import).

CSX is also somewhat stricter than CSS (for example, you can't split a
quoted string over more than one line, and comments must be terminated).

See the file `README.txt` provided with this module for a complete description
of the differences between CSS and CSX.

.. _CSS 2.1: http://www.w3.org/TR/CSS21

"""

import collections
import copy
import re

__author__ = "Zero Piraeus <z@etiol.net>"
__version__ = "0.11.10.03"

DEFAULT_STYLE = "pretty"

STYLES = ("bare", "compact", "pretty")

TAB = "    "

WIDTH = 80


class Error(Exception):

    """An error which may usefully be displayed by the csx utility."""

    # Allows incorporation of filename and line no. for output to end-users
    # by the csx utility - see doc/lib/error.txt for details.

    def __init__(self, msg:str="", line:int=0, source:str=""):
        self.msg = msg
        self.line = line
        self.source = source

    def __str__(self):
        if self.source == "-":
            source = "<stdin>"
        elif self.source:
            source = repr(self.source)
        else:
            source = ""
        if self.line:
            line = "line {0}".format(self.line)
        else:
            line = ""
        location = ", ".join(x for x in (source, line) if x)
        return ": ".join(x for x in (location, self.msg) if x)


class _Comparable(object):

    """Base class for objects with sane comparison behaviour."""

    # The following methods define comparisons other than `__lt__` in terms of
    # `__lt__`, which is not otherwise the case for subclasses of e.g. `set`.

    def __ge__(self, other):
        less_than = (self < other)
        return NotImplemented if less_than is NotImplemented else not less_than

    def __gt__(self, other):
        return other < self

    def __le__(self, other):
        more_than = (other < self)
        return NotImplemented if more_than is NotImplemented else not more_than


class _Renderable(object):

    """Base class for renderable objects.

    Example::

        >>> class Chars(_Renderable, list): pass
        >>> Chars("squee")
        Chars('s,q,u,e,e')

    """

    SEP = {s: "," for s in STYLES}

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, str(self))

    def __str__(self):
        return self.render("compact", level=1) # `level=1` to prevent newlines.

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> selector = Selector("ol li a")

            >>> print(selector.render())
            ol li a

        """
        return self.SEP[style].join(self)


class _Renderable_Recursive(_Renderable):

    """Base class for recursively renderable objects."""

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> ds = Declarations("color: red; font-family: serif")

            >>> print(ds.render())
            color: red;
            font-family: serif;

        """
        # `SEP` is defined by the subclass.
        return self.SEP[style].join(x.render(style, level) for x in self)


class Declaration(_Renderable, tuple):

    """A CSX declaration; e.g. "color: red".

    Examples::

        >>> d1 = Declaration("color: red")

        >>> d2 = Declaration(["color", "red"])

        >>> assert d1 == d2

    """

    SEP = {
        "bare": ":",
        "compact": ": ",
        "pretty": ": ",
    }

    def __new__(cls, arg:collections.Sequence):
        if isinstance(arg, str):
            try:
                key, value = Text(arg).iterate_as(cls)
            except ValueError as cause:
                raise Error("invalid declaration {0!r}".format(arg)) from cause
            else:
                return tuple.__new__(cls, (key.lower(), value))
        else:
            return tuple.__new__(cls, arg)

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> declaration = Declaration("color: red")

            >>> print(declaration.render())
            color: red;

        """
        if style == "pretty":
            return (TAB * level) + super().render(style, level) + ";"
        else:
            return super().render(style, level)


class Declarations(_Renderable_Recursive, _Comparable, dict):

    """A CSX declaration block; e.g. "color: red; font-family: serif".

    Examples::

        >>> ds1 = Declarations("color: red; font-family: serif")

        >>> ds2 = Declarations({
        ...     "color": "red",
        ...     "font-family": "serif",
        ... })

        >>> ds3 = Declarations([
        ...     Declaration("color: red"),
        ...     Declaration("font-family: serif"),
        ... ])

    Underscores are replaced by hyphens in keyword arguments::

        >>> ds4 = Declarations(color="red", font_family="serif")

        >>> assert ds1 == ds2 == ds3 == ds4

    Iterating over a `Declarations` instance returns `Declaration`
    instances, in order::

        >>> [d for d in ds1]
        [Declaration('color: red'), Declaration('font-family: serif')]

    Unlike `dict`, `Declarations` is orderable::

        >>> ds5 = Declarations("color: blue; font-family: serif")

        >>> assert ds1 > ds5

    """

    SEP = {
        "bare": ";",
        "compact": "; ",
        "pretty": "\n",
    }

    def __init__(self, arg:collections.Iterable=(), **kwargs):
        if isinstance(arg, str):
            arg = (Declaration(s) for s in Text(arg).iterate_as(Declarations))
        elif isinstance(arg, collections.Mapping):
            arg = arg.items()
        kwargs = {k.replace("_", "-"): v for k, v in kwargs.items()}
        self.update(dict(arg, **kwargs))

    def __iter__(self):
        return iter(sorted(self.items()))

    def __lt__(self, other):
        return sorted(self.items()) < sorted(other.items())

    def items(self) -> set:
        """Extend `dict.items` to return a set of `Declaration` instances.

        Example::

            >>> from pprint import pprint

            >>> ds = Declarations("color: red; font-family: serif")

            >>> pprint(ds.items())
            {Declaration('color: red'), Declaration('font-family: serif')}

        """
        return {Declaration(x) for x in super().items()}


class Rule(_Renderable, _Comparable):

    """A CSX rule; e.g. "dt, dd { color: red; a { color: blue } }".

    Attributes:
        :`selectors`:    A `Selectors` instance.
        :`declarations`: A `Declarations` instance.
        :`rules`:        A `Rules` instance.

    Examples::

        >>> r1 = Rule("dt, dd { color: red; a { color: blue } }")

        >>> ss = Selectors("dt, dd")
        >>> ds = Declarations("color: red")
        >>> rs = Rules("a { color: blue }")

        >>> r2 = Rule(selectors=ss, declarations=ds, rules=rs)

        >>> assert r1 == r2

    If declarations specified in string and keyword arguments conflict,
    the string argument takes precedence::

        >>> ds = Declarations("background: yellow; color: red")

        >>> Rule("dl { background: aqua }", declarations=ds)
        Rule('dl { background: aqua; color: red }')

    """

    SEP = {
        "bare": ";",
        "compact": "; ",
        "pretty": "\n",
    }

    FORMAT = {
        "bare": "{selectors}{{{block}}}",
        "compact": "{selectors} {{ {block} }}",
        "pretty": "{selectors} {{\n{block}\n{indent}}}",
    }

    def __init__(self, text:str="", **kwargs):
        self.selectors = kwargs.pop("selectors", Selectors())
        self.declarations = kwargs.pop("declarations", Declarations())
        self.rules = kwargs.pop("rules", Rules())
        if kwargs:
            invalid = kwargs.keys().pop()
            raise TypeError("invalid keyword argument {0!r}".format(invalid))
        text_rules = Text(text).extract()
        if len(text_rules) > 1:
            raise ValueError("string argument describes multiple rules")
        elif text_rules:
            rule = text_rules.pop()
            self.selectors.update(rule.selectors)
            self.declarations.update(rule.declarations)
            self.rules.extend(rule.rules)

    def __eq__(self, other):
        return (
                (self.selectors == other.selectors)
            and (self.declarations == other.declarations)
            and (self.rules == other.rules)
        )

    def __lt__(self, other):
        if self.selectors != other.selectors:
            return self.selectors < other.selectors
        elif self.declarations != other.declarations:
            return self.declarations < other.declarations
        elif self.rules != other.rules:
            return self.rules < other.rules
        else:
            return False

    def collapse(self):
        """Remove redundant nesting from `self`.

        Example::

            >>> rule = Rule("ol { li { a { color: blue } } }")

            >>> rule.collapse()

            >>> print(rule.render())
            ol li a {
                color: blue;
            }

        """
        while (
                (not self.declarations)
            and (len(self.selectors) == 1)
            and (len(self.rules) == 1)
            and (len(self.rules[0].selectors) == 1)
        ):
            child = self.rules.pop()
            self.selectors = child.selectors.prefix(self.selectors)
            self.declarations = child.declarations
            self.rules = child.rules
        for rule in self.rules:
            rule.collapse()

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> rule = Rule("dt, dd { color: red; a { color: blue } }")

            >>> print(rule.render())
            dt, dd {
                color: red;
                a {
                    color: blue;
                }
            }

        """
        selectors = self.selectors.render(style, level)
        if self.declarations and self.rules:
            block = self.SEP[style].join((
                self.declarations.render(style, level + 1),
                self.rules.render(style, level + 1),
            ))
        elif self.declarations:
            block = self.declarations.render(style, level + 1)
        elif self.rules:
            block = self.rules.render(style, level + 1)
        else:
            block = ""
        indent = TAB * level
        return self.FORMAT[style].format(**locals())


class Rules(_Renderable_Recursive, list):

    """A CSX rule block; e.g. "ol { background: aqua }; li { color: red }".

    Examples::

        >>> rs1 = Rules('''
        ...     ol { background: aqua }
        ...     li { color: red }
        ... ''')

        >>> rs2 = Rules([
        ...     Rule("ol { background: aqua }"),
        ...     Rule("li { color: red }"),
        ... ])

        >>> assert rs1 == rs2

    """

    SEP = {
        "bare": "",
        "compact": "\n",
        "pretty": "\n\n",
    }

    # Nested rules are delimited differently to top-level rules - see
    # `Rules.render`.
    ALT_SEP = {
        "bare": ";",
        "compact": "; ",
        "pretty": "\n",
    }

    def __init__(self, arg:collections.Iterable=()):
        if isinstance(arg, str):
            self[:] = Text(arg).extract()
        else:
            self[:] = arg

    def _graft(self, tree:"Rules") -> list:
        """Merge `tree` into `self` and return a list of leaf rules.

        Arguments:
            :`tree`: As returned by `Selectors._sprout`.

        Example::

            >>> rules = Rules('''
            ...     dl, ol, ul { margin: 1em; padding: 1em }
            ...     dl { background: yellow }
            ...     ol, ul { background: aqua }
            ... ''')

            >>> tree = Selectors("dl dt, dl dd, ol li, ul li")._sprout()

            >>> leaves = rules._graft(tree)

            >>> sorted(leaves)
            [Rule('dt, dd {  }'), Rule('li {  }')]

            >>> print(rules.render("compact"))
            dl, ol, ul { margin: 1em; padding: 1em }
            dl { background: yellow; dt, dd {  } }
            ol, ul { background: aqua; li {  } }

        """
        # Used by `_merge_optimized` - somewhat voodoo, but the examples above
        # should make it clear *what* is happening, if not *how*. Essentially
        # we search for nodes in `self` that, in traditional CSS, would
        # have the same selectors as those in `tree`, so we can insert
        # declarations from `tree` at those nodes as appropriate. This is
        # tricky stuff, though, and can only really be properly understood by
        # reading `_merge_optimized` as well. Action by side-effect is not
        # ideal, admittedly, but I can't see an easier way to do it.
        leaves = []
        target_selectors = [r.selectors for r in self]
        for rule in tree:
            if rule.selectors in target_selectors:
                target = self[target_selectors.index(rule.selectors)]
            else:
                self.append(rule)
                target = rule
            if ("$", "leaf") in rule.declarations.items():
                leaves.append(target)
                del rule.declarations["$"]
            if rule.rules:
                leaves += target.rules._graft(rule.rules)
        return leaves

    def _merge_normalized(self, rule:Rule, _prefixes:set=set()):
        """Merge a rule into `self` for each declaration in `rule`.

        Arguments:
            :`rule`:      Rule to be merged into `self`.
            :`_prefixes`: Used internally - ***DO NOT SET***.

        Example::

            >>> normalized = Rules('''
            ...     dl { background: yellow }
            ...     dl { margin: 1em }
            ...     dl { padding: 1em }
            ...     dl dt, dl dd { color: red }
            ... ''')

            >>> rule = Rule('''
            ...     ol, ul {
            ...         background: aqua;
            ...         margin: 1em;
            ...         padding: 1em;
            ...         li { color: red }
            ...     }
            ... ''')

            >>> normalized._merge_normalized(rule)

            >>> print(normalized.render("compact"))
            dl { background: yellow }
            dl, ol, ul { margin: 1em }
            dl, ol, ul { padding: 1em }
            dl dt, dl dd, ol li, ul li { color: red }
            ol, ul { background: aqua }

        """
        # Used by `Rules.optimize`.
        selectors = rule.selectors.prefix(_prefixes)
        for dec in (Declarations({d}) for d in rule.declarations):
            for candidate in self:
                if dec == candidate.declarations:
                    candidate.selectors.update(selectors)
                    break
            else:
                self.append(Rule(selectors=selectors.copy(), declarations=dec))
        for subrule in rule.rules:
            self._merge_normalized(subrule, selectors)

    def _merge_optimized(self, rule:Rule):
        """Merge an optimized rule tree based on `rule` into `self`.

        Arguments:
            :`rule`: Rule to be merged into `self`.

        Example::

            >>> optimized = Rules('''
            ...     dl { background: yellow }
            ...     ol, ul { background: aqua }
            ... ''')

            >>> rule = Rule("dl dt, dl dd, ol li, ul li { color: red }")

            >>> optimized._merge_optimized(rule)

            >>> print(optimized.render("compact"))
            dl { background: yellow; dt, dd { color: red } }
            ol, ul { background: aqua; li { color: red } }

        """
        # Used by `Rules.optimize`.
        for leaf in self._graft(rule.selectors._sprout()):
            leaf.declarations.update(rule.declarations)
            for subrule in rule.rules:
                leaf.rules._merge_optimized(subrule)

    def flatten(self, _prefixes:set=set()):
        """Convert `self` to un-nested rules.

        Arguments:
            :`_prefixes`: Used internally - ***DO NOT SET***.

        Example::

            >>> rules = Rules('''
            ...
            ...     dl, ol, ul {
            ...         margin: 1em;
            ...         padding: 1em;
            ...     }
            ...
            ...     ol, ul {
            ...         background: aqua;
            ...         li { color: red }
            ...     }
            ...
            ...     dl {
            ...         background: yellow;
            ...         dt, dd { color: red }
            ...     }
            ...
            ... ''')

            >>> rules.flatten()

            >>> print(rules.render("compact"))
            dl, ol, ul { margin: 1em; padding: 1em }
            ol, ul { background: aqua }
            ol li, ul li { color: red }
            dl { background: yellow }
            dl dt, dl dd { color: red }

        """
        flattened = []
        for rule in self:
            selectors = rule.selectors.prefix(_prefixes)
            if rule.declarations:
                new = Rule(selectors=selectors, declarations=rule.declarations)
                flattened.append(new)
            rule.rules.flatten(selectors)
            flattened += rule.rules
        self[:] = flattened

    def optimize(self, collapse:bool=True, normalize:bool=False):
        """Optimize `self`.

        Arguments:
            :`collapse`:  If True, collapse redundant nesting.
            :`normalize`: If True, normalize `self` before optimizing
                          (dramatically alters rule order).

        Example::

            >>> rules = Rules('''
            ...     dl { background: yellow }
            ...     dl, ol, ul { margin: 1em }
            ...     dl, ol, ul { padding: 1em }
            ...     dl dt, dl dd, ol li, ul li { color: red }
            ...     ol, ul { background: aqua }
            ... ''')

            >>> rules.optimize()

            >>> print(rules.render("compact"))
            dl, ol, ul { margin: 1em; padding: 1em }
            dl { background: yellow; dt, dd { color: red } }
            ol, ul { background: aqua; li { color: red } }

        """
        if normalize:
            normalized = Rules()
            for rule in self:
                normalized._merge_normalized(rule)
            rules = normalized
        else:
            rules = self
        optimized = Rules()
        for rule in rules:
            optimized._merge_optimized(rule)
        if collapse:
            for rule in optimized:
                rule.collapse()
        optimized.sort()
        self[:] = optimized

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> rules = Rules('''
            ...
            ...     dl, ol, ul {
            ...         margin: 1em;
            ...         padding: 1em;
            ...     }
            ...
            ...     ol, ul {
            ...         background: aqua;
            ...         li { color: red }
            ...     }
            ...
            ...     dl {
            ...         background: yellow;
            ...         dt, dd { color: red }
            ...     }
            ...
            ... ''')

            >>> print(rules.render("compact"))
            dl, ol, ul { margin: 1em; padding: 1em }
            ol, ul { background: aqua; li { color: red } }
            dl { background: yellow; dt, dd { color: red } }

        """
        if (level == 0) or (self.SEP is self.ALT_SEP):
            return super().render(style, level)
        else:
            self.SEP, cache = self.ALT_SEP, self.SEP
            try:
                return super().render(style, level)
            finally:
                self.SEP = cache

    def sort(self, key=None, reverse=False):
        """Extend `list.sort` to recursively sort `self`.

        Example::

            >>> rules = Rules('''
            ...     ol li, ul li { a { color: blue }; b { color: black } }
            ...     dl dt, dl dd { b { color: black }; a { color: blue } }
            ... ''')

            >>> rules.sort()

            >>> print(rules.render("compact"))
            dl dt, dl dd { a { color: blue }; b { color: black } }
            ol li, ul li { a { color: blue }; b { color: black } }

        """
        for rule in self:
            rule.rules.sort(key, reverse)
        super().sort(key=key, reverse=reverse)


class Selector(_Renderable, _Comparable, tuple):

    """A CSX selector; e.g. "ol > li a[lang|='en']".

    Example::

        >>> Selector("ol > li a[lang|='en']")
        Selector("ol > li a[lang|='en']")

    """

    # Match and retain:
    #   > or + (possibly followed by whitespace), followed by any sequence
    #   of characters except whitespace, > or +
    # Match and discard:
    #   whitespace (where not part of a match as detailed above)
    ITER = re.compile("([>+]\s*[^\s>+]+)|\s+")

    SEP = {s: " " for s in STYLES}

    # Both `SORT_ATTRIBUTES` and `SORT_ELEMENTS` are used to create
    # substitutions so that lexicographical sorting produces output in a more
    # useful order; i.e `:link` before `:visited`, `dt` before `dd` etc.

    SORT_ATTRIBUTES = tuple((x, "~{0:02d} ".format(n)) for n, x in enumerate((
        ":link",
        ":visited",
        ":focus",
        ":hover",
        ":active",
        ":", "[", ".", "#",
    )))

    # Not a dict, because order is important.
    SORT_ELEMENTS = (
        ("*", " *"),
        ("html", " * ~"),
        ("body", " * ~~"),
        ("dd", "dt ~"),
        ("input", "label ~"),
        ("td", "th ~"),
        ("tfoot", "thead ~"),
        ("tbody", "thead ~~"),
    )

    __SORT_ELEMENT_KEYS = tuple(e[0] for e in SORT_ELEMENTS) # for speed

    __lt_cache = {}

    def __new__(cls, arg:collections.Iterable):
        if isinstance(arg, str):
            self = tuple.__new__(cls, Text(arg).iterate_as(Selector))
        else:
            self = tuple.__new__(cls, arg)
        return self

    def __lt__(self, other):
        # This comparison is expensive and frequently performed, so we
        # optimize it by caching the result.
        try:
            return self.__lt_cache[(self, other)]
        except KeyError:
            for self_item, other_item in zip(self._sort_key, other._sort_key):
                if self_item != other_item:
                    result = self_item < other_item
                    break
            else:
                result = len(self) < len(other)
            self.__lt_cache[(self, other)] = result
            return result

    @property
    def _sort_key(self) -> collections.Iterator:
        """An ordering key for `self`.

        Example::

            >>> selector = Selector("body dl[lang='en'] dt + dd a:link")
            >>> list(selector._sort_key)
            [' * ~~', "dl~06 lang='en']", 'dt', '   dt ~', 'a~00 ']

        """
        # See `SORT_ATTRIBUTES`, `SORT_ELEMENTS` to better understand what's
        # going on above.
        for item in self:
            # Sibling and child combinators sort before type selectors.
            if item[0] == "+":
                item = "   " + item[1:].lstrip()
            if item[0] == ">":
                item = "  " + item[1:].lstrip()
            # Bare class, id etc. selectors sort after type selectors.
            for target, replacement in self.SORT_ATTRIBUTES:
                item = item.replace(target, replacement)
            # Conceptually related type selectors sort in the "right" order.
            if item.lstrip().startswith(self.__SORT_ELEMENT_KEYS):
                for target, replacement in self.SORT_ELEMENTS:
                    if item.lstrip().startswith(target):
                        item = item.replace(target, replacement, 1)
                        break
            yield item


class Selectors(_Renderable_Recursive, _Comparable, set):

    """A CSX selector block; e.g. "dl dd, dl dt, ol li, ul li".

    Example::

        >>> Selectors("dl dd, dl dt, ol li, ul li")
        Selectors('dl dt, dl dd, ol li, ul li')

    """

    SEP = {
        "bare": ",",
        "compact": ", ",
        "pretty": ", ",
    }

    def __init__(self, arg:collections.Iterable=()):
        if isinstance(arg, str):
            arg = Text(arg).iterate_as(Selectors)
        set.__init__(self, (Selector(x) for x in arg))

    def __iter__(self):
        return iter(sorted(set(self)))

    def __lt__(self, other):
        # This comparison is expensive and frequently performed, so we
        # optimize it by caching the result.
        for self_item, other_item in zip(self, other):
            if self_item != other_item:
                return self_item < other_item
        else: # indentation is correct! This is the else of the for loop.
            return len(self) > len(other)

    def _sprout(self, _prefix:collections.Iterable=()) -> {Rule, Rules}:
        """Return a graftable tree of optimized rules for `self`.

        Arguments:
            :`_prefix`: Used internally - ***DO NOT SET***.

        Example::

            >>> example = Selectors("ul, ol, ul ul, ol ol, ol ul, ul ol")
            >>> print(example._sprout().render())
            ol, ul {
                $: leaf;
                ol, ul {
                    $: leaf;
                }
            }

        """
        # Used by `Rules._graft` - turns a selector block into an
        # optimally-nested `Rules` object with place-markers for where any
        # declarations for those selectors should go. This was murder to write,
        # but I *think* it now works in all cases. No line-by-line comments
        # because they just padded out the code and made it even harder to
        # understand - you just have to read it very very carefully.
        tree = Rule(selectors=Selectors({_prefix}))
        for node in {s[:1] for s in self}:
            if node:
                branches = {s[1:] for s in self if s[:1] == node}
                rule = Selectors(branches)._sprout(node)
                rule_spec = (rule.rules, rule.declarations)
                tree_specs = [(r.rules, r.declarations) for r in tree.rules]
                if rule_spec in tree_specs:
                    target = tree.rules[tree_specs.index(rule_spec)]
                    target.selectors.add(Selector(node))
                else:
                    tree.rules.append(rule)
            else:
                tree.declarations["$"] = "leaf"
        if _prefix:
            return tree
        else:
            tree.rules.sort()
            return tree.rules

    def copy(self) -> "Selectors":
        """Extend `set.copy` to return a `Selectors` instance."""
        # set.copy() returns a set, which isn't what we want.
        return copy.copy(self)

    def prefix(self, prefixes:set) -> "Selectors":
        """Prefix `self` with `prefixes`.

        Arguments:
            :`prefixes`: Selectors with which to prefix `self`.

        Example::

            >>> prefixed = Selectors("b, i").prefix(Selectors("p, a"))
            >>> Selectors(prefixed)
            Selectors('a b, a i, p b, p i')

        """
        if prefixes:
            return Selectors({Selector(p + s) for p in prefixes for s in self})
        else:
            return self.copy()

    def render(self, style:str=DEFAULT_STYLE, level:int=0) -> str:
        """Return a textual representation of `self`.

        Arguments:
            :`style`: One of `STYLES`.
            :`level`: Indentation level of "pretty" output.

        Example::

            >>> selectors = Selectors("ol li, ul li, dl dd, dl dt")
            >>> print(selectors.render("compact"))
            dl dt, dl dd, ol li, ul li

            >>> table = Selectors('''
            ...
            ...     table tbody tr td, table tbody tr th,
            ...     table tfoot tr td, table tfoot tr th,
            ...     table thead tr td, table thead tr th,
            ...
            ... ''')
            >>> print(table.render(level=1))
                table thead tr th,
                table thead tr td,
                table tfoot tr th,
                table tfoot tr td,
                table tbody tr th,
                table tbody tr td

        """
        if style == "pretty":
            indent = TAB * level
            result = indent + super().render(style, level)
            if len(result) <= WIDTH:
                return result
            else:
                cache = self.SEP["pretty"]
                try:
                    self.SEP["pretty"] = ",\n" + indent
                    return indent + super().render(style, level)
                finally:
                    self.SEP["pretty"] = cache
        else:
            return super().render(style, level)


class Text(str):

    r"""An escaped string.

    Attributes:
        :`subs`: A list of quoted substrings extracted from input.

    Instantiated by passing a string to the constructor.

    Quoted substrings are replaced by `str.format` replacement fields, and
    appended to the `subs` attribute. They must not contain newlines,
    unless escaped with a backslash. CSS comments are removed.

    `str(instance_of_Text)` reconstructs the original string,
    removing extraneous whitespace.

    Examples::

        >>> aymara_quechua = Text('''
        ...
        ... /* indigenous Altiplano languages */
        ...
        ...     p[lang|='ay'],
        ...     p[lang|='qu'] {
        ...
        ... ''')
        >>> str(aymara_quechua)
        "p[lang|='ay'], p[lang|='qu'] {"
        >>> aymara_quechua[:]
        '\n\n\n\n    p[lang|={0}],\n    p[lang|={1}] {{\n\n'
        >>> aymara_quechua.subs
        ["'ay'", "'qu'"]

    Instantiated by:

    - `Declaration.__new__`
    - `Declarations.__init__`
    - `Rule.__init__`
    - `Rules.__init__`
    - `Selector.__new__`
    - `Selectors.__init__`

    """

    # Match any of ...
    #
    # - any seqence of characters except semicolons, or braces that aren't part
    #   of "{int}"-style str.format replacement fields, followed by "{{"
    #
    # - a semicolon
    #
    # - "}}", unless followed by an odd number of closing braces (to avoid
    #   catching the ends of replacement fields)
    #
    # - the start of the string
    #
    # ... followed by any all-whitespace sequence.
    ITER = re.compile("((?:(?:{[0-9]+}|[^;{}])*{{|;|}}(?!}(?:}})*[^}])|^)\s*)")

    # Match:
    # - a single or double quotation mark, unless escaped with a backslash
    # - any of "/*", "*/", "{", "}", "@", "<!--" or "-->"
    STRIP = re.compile(r"""((?<!\\)['"]|/\*|\*/|[{}@]|<!--|-->)""")

    def __new__(cls, text:str):
        # Lots of work to make sure that comment markers are only treated as
        # such outside strings, quotes are only treated as string delimiters
        # outside comments, etc. It would probably have made more sense to use
        # a parser and a grammar, but hell, it's written now and it works.
        escaped = ""
        subs = []
        delimiter = None
        for position, line in enumerate(text.split("\n"), start=1):
            for item in re.split(cls.STRIP, line):
                if delimiter:
                    if delimiter in {'"', "'"}:
                        subs[-1] += item
                    if item == delimiter:
                        delimiter = None
                elif item in {'{', "}"}:
                    escaped += item * 2
                elif item == "/*":
                    delimiter = "*/"
                elif item in {'"', "'"}:
                    delimiter = item
                    escaped += "{{{0}}}".format(len(subs))
                    subs.append(item)
                elif item in {"@", "<!--", "-->"}:
                    raise Error("syntax error: {0!r}".format(item), position)
                else:
                    escaped += item
            if delimiter in {"'", '"'}:
                raise Error("unfinished string", position)
            escaped += "\n"
        if delimiter:
            raise Error("unfinished comment", position)
        self = str.__new__(cls, escaped[:-1])
        self.subs = subs
        return self

    def __iter__(self):
        position = 1
        for raw_token in re.split(self.ITER, self):
            if raw_token.strip() not in {"", ";"}:
                token = " ".join(raw_token.split()).format(*self.subs)
                try:
                    yield token
                except Exception:
                    # Spit out the line no. if caller throws something at us.
                    yield position
                    return
            position += raw_token.count("\n")

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, str(self))

    def __str__(self):
        return " ".join(self.split()).format(*self.subs)

    def extract(self, _stream:collections.Iterable=()) -> {Rules, tuple}:
        rules = Rules()
        if _stream:
            # Recursive call, then.
            stream = _stream
            declarations = Declarations()
        else:
            stream = iter(self)
        for token in stream:
            try:
                if token == "}":
                    break
                elif token.endswith("{"):
                    rule = Rule(selectors=Selectors(token.rstrip(" {")))
                    rule.declarations, rule.rules = self.extract(stream)
                    rules.append(rule)
                elif _stream:
                    declarations.update({Declaration(token)})
                else:
                    try:
                        Declaration(token)
                    except Exception:
                        raise Error("syntax error: {0!r}".format(token))
                    else:
                        raise Error("declaration outside rule")
            except Error as exc:
                exc.line = stream.throw(exc) # get the line no.
                raise
        else:
            if _stream:
                raise Error("unfinished rule")
            else:
                return rules
        if _stream:
            return declarations, rules
        else:
            raise Error("unmatched '}", stream.throw(Error)) # get the line no.

    def iterate_as(self, cls) -> collections.Iterator:
        """Iterate over tokens in `self` as defined by `cls`.

        Arguments:
            :`cls`: A subclass of `csx._Renderable`.

        Examples::

            >>> for cls, text in [
            ...     (Declaration, "color: red"),
            ...     (Declarations, "color: red; font-family: serif"),
            ...     (Selector, "ol li a"),
            ...     (Selectors, "dl dd a, dl dt a, ol li a, ul li a"),
            ... ]:
            ...     list(Text(text).iterate_as(cls))
            ['color', 'red']
            ['color: red', 'font-family: serif']
            ['ol', 'li', 'a']
            ['dl dd a', 'dl dt a', 'ol li a', 'ul li a']

        """
        if cls == Selector:
            # Special-case Selector to deal with child/sibling combinators, and
            # take the opportunity to normalize case while we're at it.
            tokens = (x.lower() for x in re.split(cls.ITER, self) if x)
        else:
            tokens = (x for x in self.split(cls.SEP["bare"]) if x.strip())
        for raw_token in tokens:
            yield " ".join(raw_token.split()).format(*self.subs)


if __name__ == "__main__":
    # Exit with an error message if we're run as a script.
    import os, sys
    if "csx" in os.listdir(os.curdir):
        SCRIPT = "./csx"
    else:
        SCRIPT = "csx"
    sys.exit("Try:\n{0} --help".format(SCRIPT))

