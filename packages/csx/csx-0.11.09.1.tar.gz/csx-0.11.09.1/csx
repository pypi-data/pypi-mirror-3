#!/usr/bin/python3

# csx - convert between CSX [Extended Cascading Stylesheets] and CSS.
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

"""Usage: csx [OPTION]... [FILE]...

Convert each FILE from CSX to traditional CSS, or optimize each CSS/CSX FILE.
With no FILE, or when FILE is -, read standard input.

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -q, --quiet          don't show warning messages

  Formatting:
    -b, --bare         equivalent to --style=bare
    -c, --compact      equivalent to --style=compact
    -p, --pretty       equivalent to --style=pretty
    --style=STYLE      format output in the specified STYLE
                       (bare, compact or pretty; default: pretty)
    --tab=TAB          width of one level of indentation
                       (requires --style=pretty; default: 4)
    --width=WIDTH      try to keep output within WIDTH columns
                       (requires --style=pretty; default: 80; 0=unlimited)

  Optimization:
    WARNING: --optimize changes the order of rules in the source document,
    so may alter the meaning of output according to cascade rules.
    --aggressive alters source order further still.

    -a, --aggressive   eliminate redundant declarations (implies --optimize)
    -n, --no-collapse  don't collapse redundant nesting (implies --optimize)
    -o, --optimize     convert to optimally nested CSX

  CGI:
    -x, --cache        Output the most recently modified of FILE.STYLE.css or
                       FILE.csx (converting to CSS if necessary), and save the
                       result of any conversion to FILE.STYLE.css
                       (not compatible with optimization options)

"""

import optparse
import os
import platform
import sys
import warnings

import csx


class Alert(UserWarning): pass


class Parser(optparse.OptionParser):

    """CSX option parser."""

    DELIMITERS = {
        "bare": "",
        "compact": "\n",
        "pretty": "\n\n",
    }

    OPTIONS = (
        (None, [
            ("-$ --debug", {
                "action": "store_true",
                "default": False,
                "help": optparse.SUPPRESS_HELP
            }),
            ("-q --quiet", {
                "action": "store_true",
                "default": False,
                "help": "don't show warning messages",
            }),
        ]),
        ("Formatting", [
            ("--style", {
                "choices": csx.STYLES,
                "default": csx.DEFAULT_STYLE,
                "help": (
                    "format output in the specified STYLE              "
                    "({0} or {1}; default: %default)"
                ).format(", ".join(csx.STYLES[:-1]), csx.STYLES[-1]),
            }),
            ("--tab", {
                "default": len(csx.TAB) if (set(csx.TAB) == {" "}) else 4,
                "type": "int",
                "help": (
                    "width of one level of indentation              "
                    "(requires --style=pretty; default: %default)"
                ),
            }),
            ("--width", {
                "default": csx.WIDTH,
                "type": "int",
                "help": (
                    "try to keep output within WIDTH columns        "
                    "(requires --style=pretty; default: %default; 0=unlimited)"
                ),
            }),
        ]),
        ("Optimization", [
            (
                "WARNING: --optimize changes the order of rules in the source "
                "document, so may alter the meaning of output according to "
                "cascade rules. --aggressive alters source order further "
                "still."
            ),
            ("-a --aggressive", {
                "action": "store_true",
                "default": False,
                "help": "eliminate redundant declarations "
                "(implies --optimize)",
            }),
            ("-n --no-collapse", {
                "action": "store_false",
                "default": True,
                "dest": "collapse",
                "help": "don't collapse redundant nesting "
                "(implies --optimize)",
            }),
            ("-o --optimize", {
                "action": "store_true",
                "default": False,
                "help": "convert to optimally nested CSX",
            }),
        ]),
        ("CGI", [
            ("-x --cache", {
                "action": "store_true",
                "default": False,
                "help": (
                    "Output the most recently modified of FILE.STYLE.css or "
                    "FILE.csx (converting to CSS if necessary), and save the "
                    "result of any conversion to FILE.STYLE.css          "
                    "(not compatible with optimization options)"
                ),
            }),
        ]),
    )

    # Add shortcut options.
    OPTIONS[1][1][0:0] = [
        ("-{0[0]} --{0}".format(style), {
            "action": "store_const",
            "const": style,
            "dest": "style",
            "help": "equivalent to --style={0}".format(style),
        }) for style in csx.STYLES
    ]

    def __init__(self):
        optparse.OptionParser.__init__(self, version=csx.__version__)
        self.description = (
            "Convert each FILE from CSX to traditional CSS, or optimize each "
            "CSS/CSX FILE. With no FILE, or when FILE is -, read standard "
            "input."
        )
        self.usage = "%prog [OPTION]... [FILE]..."
        for title, args in self.OPTIONS:
            self.__add_group(title, *args)
        self.parse_args()
        csx.TAB = " " * self.values.tab
        csx.WIDTH = self.values.width
        if not self.largs:
            self.largs = ["-"]
        if self.values.quiet:
            warnings.simplefilter("ignore")
        else:
            warnings.simplefilter("once", Alert)

    def __add_group(self, title:{str, None}, *args):
        """Add an option group to `self`."""
        if isinstance(args[0], str):
            description, *args = args
        else:
            description = None
        if title is None:
            target = self
        else:
            target = optparse.OptionGroup(self, title, description)
        for option, attrs in args:
            target.add_option(*option.split(), **attrs)
        if isinstance(target, optparse.OptionGroup):
            self.add_option_group(target)

    def __check_options(self):
        """Check for conflicting option values, and enforce implied options."""
        if self.values.optimize:
            opt = "--optimize"
        elif self.values.aggressive:
            self.values.optimize = True
            opt = "--aggressive"
        elif not self.values.collapse:
            self.values.optimize = True
            opt = "--no-collapse"
        if self.values.optimize:
            if self.values.cache:
                raise csx.Error("--cache and {0} are incompatible".format(opt))
            else:
                warnings.warn(Alert("{0} alters rule order".format(opt)))
        if self.values.style != "pretty":
            if self.values.tab != self.defaults["tab"]:
                warnings.warn(Alert("--tab requires --style=pretty"))
            if self.values.width != self.defaults["width"]:
                warnings.warn(Alert("--width requires --style=pretty"))

    def __process_cached(self) -> str:
        """Process the files in `self.largs`, or their caches."""
        output = []
        for source in (Source(a, self.values.style) for a in self.largs):
            try:
                if source.cached:
                    output.append(source.read(cache=True))
                else:
                    rules = csx.Rules(source.read())
                    text = rules.render(self.values.style)
                    with open(source.cache_name, "w") as cache:
                        cache.write(text)
                    output.append(text)
            except csx.Error as exc:
                exc.source = source.name
                raise
        return self.DELIMITERS[self.values.style].join(output)

    def __process_uncached(self) -> str:
        """Process the files in `self.largs`."""
        rules = csx.Rules()
        for source in (Source(a) for a in self.largs):
            try:
                rules.extend(csx.Rules(source.read()))
            except csx.Error as exc:
                exc.source = source.name
                raise
        if self.values.optimize:
            rules.optimize(self.values.collapse, self.values.aggressive)
        else:
            rules.flatten()
        return rules.render(self.values.style)

    def process(self) -> str:
        """Process the command line."""
        self.__check_options()
        if self.values.cache:
            return self.__process_cached()
        else:
            return self.__process_uncached()


class Source(object):

    """A CSX source."""

    def __init__(self, name:str, style:str=""):
        self.name = name
        self.style = style

    def read(self, cache:bool=False) -> str:
        """Return the contents of a file, or its cache, or standard input."""
        if cache and self.name == "-":
            raise csx.Error("can't cache standard input")
        elif self.name == "-":
            f = sys.stdin
        elif cache and self.cached:
            f = open(self.cache_name)
        else:
            f = open(self.name)
        if os.isatty(f.fileno()):
            sys.stderr.write(self.quit_msg)
        return f.read()

    @property
    def cache_name(self) -> str:
        """Filename of a possible cache of the file `self` refers to.

        Example::

            >>> {Source(filename, "pretty").cache_name for filename in [
            ...     "squee",
            ...     "squee.csx",
            ...     "squee.CSS",
            ...     "squee.bare.css",
            ...     "squee.COMPACT",
            ...     "squee.pretty.css",
            ...     "squee.pretty.CSX",
            ... ]}
            {'squee.pretty.css'}

        """
        filename = self.name
        basename, ext = os.path.splitext(filename)
        if ext.lower() in {".css", ".csx"}:
            filename = basename
            basename, ext = os.path.splitext(filename)
        if ext.lower() in {".{0}".format(x) for x in csx.STYLES}:
            filename = basename
        return "{0}.{1}.css".format(filename, self.style)

    @property
    def cached(self) -> bool:
        """True if a current cache exists of the file `self` refers to.

        Example::

            >>> import tempfile
            >>> import time
            >>> temp_dir = tempfile.mkdtemp()
            >>> squee = os.path.join(temp_dir, "squee.csx")
            >>> pretty = os.path.join(temp_dir, "squee.pretty.css")
            >>> for filename in [squee, pretty]:
            ...     with open(filename, "w") as f:
            ...         _ = f.write("/* blah */")
            >>> one_week_ago = time.time() - 7 * 24 * 60 * 60
            >>> os.utime(squee, (one_week_ago, one_week_ago))
            >>> Source(squee, "pretty").cached
            True
            >>> Source(squee, "compact").cached
            False
            >>> # cleanup ...
            >>> os.remove(squee)
            >>> os.remove(pretty)
            >>> os.rmdir(temp_dir)

        """
        cache_name = self.cache_name
        cache_exists = os.path.exists(cache_name)
        if cache_exists and os.path.exists(self.name):
            return os.path.getmtime(cache_name) > os.path.getmtime(self.name)
        elif cache_exists:
            return True
        else:
            return False

    @property
    def quit_msg(self) -> str:
        """Platform-appropriate quit message."""
        if platform.system() == "Linux":
            eof = "Ctrl-D"
        elif platform.system() == "MacOS":
            eof = "Cmd-Q"
        elif platform.system() == "Windows":
            eof = "Ctrl-Z then Return"
        else:
            eof = "EOF"
        return "[reading from terminal; terminate with {0}]\n".format(eof)


def _main():
    warning_text = os.path.basename(sys.argv[0]) + ": warning: {0}\n"
    warnings.formatwarning = lambda msg, *a, **k: warning_text.format(msg)
    parser = Parser()
    try:
        print(parser.process())
    except Exception as exc:
        if parser.values.debug:
            raise
        elif isinstance(exc, EnvironmentError):
            details = exc.strerror.lower()
            if exc.filename:
                parser.error("{0!r}: {1}".format(exc.filename, details))
            else:
                parser.error(details)
        elif isinstance(exc, csx.Error):
            parser.error(exc)
        else:
            parser.error("internal error; run with --debug for details.")
    except KeyboardInterrupt:
        return "[interrupted]"


if __name__ == "__main__":
    sys.exit(_main())

