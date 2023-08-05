
====================================
CSX - Extended Cascading Stylesheets
====================================

CSX adds one powerful language feature to CSS: nested scopes.

For example, the traditional CSS::

    dl {
        background: yellow;
        font-family: "Arial Black";
    }

    dl dt {
        color: red;
    }

    dl dd {
        color: blue;
    }

    dl dd a {
        color: green;
    }

can be written in CSX like this::

    dl {
        background: yellow;
        font-family: "Arial Black";
        dt { color: red }
        dd {
            color: blue;
            a { color: green }
        }
    }

You can nest child and sibling combinators::

    ol {
        > li { color: red }
        + p { margin-top: 2em }
    }

... and they'll be handled as you would expect::

    ol > li { color: red }
    ol + p { margin-top: 2em }

Comments are stripped out automatically. Because the conversion process mangles
the order of the source and alters line formatting, attempting to keep them in
what humans would regard as the "right" place would be error-prone.

There's no limit to how far you can nest rules [1]_.

CSS at-rules, such as @media and @import, are *not* allowed in CSX. Pretty much
anything they can do is better accomplished by appropriate use of the <link>
element in (X)HTML, and it's assumed that other document languages have similar
capabilities.

How to install it
-----------------

Unpack the tarball, cd to the csx-x.y.z directory, and type ::

    sudo python setup.py install

How to use it
-------------

This distribution includes a utility `csx`, and a Python module `csx.py`.

Converting from CSX to CSS from the command line is simple::

    z@cracker:~/projects/squee$ csx --compact kapow.csx

... as it is from within Python code::

    >>> from csx import Rules

    >>> rules = Rules("/* ... */")
    >>> rules.flatten()
    >>> css_text = rules.render("pretty")

You can also convert traditional CSS to CSX::

    z@cracker:~/projects/squee$ csx --optimize kapow.css

    >>> rules = Rules("/* ... */")
    >>> rules.optimize()
    >>> csx_text = rules.render("pretty")

For complex stylesheets, this may result in deeply nested CSX. The conversion
from CSS to CSX ignores the order of rules in the source stylesheet in order to
maximize nesting; because of the way the cascade works, this might change the
meaning of the stylesheet. A simple way to check for this is to "round-trip" a
stylesheet::

    z@cracker:~/projects/squee$ csx --optimize kapow.css | csx --pretty

In general, neither the csx.py module nor the csx utility care whether you feed
them CSS or CSX - everything is CSX as far as the underlying code is concerned.
So, you can use csx as a code prettifier ... ::

    z@cracker:~/projects/squee$ csx --pretty kapow.css

... or compressor::

    z@cracker:~/projects/squee$ csx --compact kapow.css

The csx utility has several options, including one intended to make converting
CSX on the fly by a web server straightforward; typing `csx --help` in a
terminal will give you the run-down.

The csx.py module is thoroughly documented - typing `help("csx")` from the
Python interpreter should tell you all you need to know.

Gotchas
-------

Syntax
""""""

Writing CSX is straightforward if you already know CSS, but there are some
differences. Apart from nested rules, changes from CSS2.1_ are:

- Syntax is strictly enforced; all errors are fatal. Illegal syntax that
  would be ignored (or implicitly fixed) in CSS renders the entire
  stylesheet invalid in CSX.

- At-rules (`@import`, `@media`, etc.) are not allowed. Any `@` outside a
  string or comment is a fatal error.

- XML/SGML comment delimiters are not allowed. Any `<!--` or `-->` outside
  a string or comment is a fatal error.

- Strings must be correctly terminated. For example, ::

        font-family: "Arial Black \n

  is a fatal error; it is *not* ignored as in CSS.

- Blocks and comments must be explicitly closed. For example, ::

        blockquote {
        color: green;
        /* EOF */

  is a fatal error; it is *not* implicitly closed as in CSS.

Comments are allowed, although this implementation of CSX removes them
from input.

.. _CSS2.1: http://www.w3.org/TR/CSS21/

Classes, pseudo-classes, IDs and attribute selectors
""""""""""""""""""""""""""""""""""""""""""""""""""""

The rule ::

    ul {
        .nav { background: yellow }
    }

is equivalent to ::

    ul .nav { background: yellow }

(note the space), and *not* ::

    ul.nav { background: yellow }

... similarly for pseudo-classes, IDs and attribute selectors.

Invalid CSX / CSS
"""""""""""""""""

This implementation does some checking for illegal syntax, but not much. If you
get weird results, there's probably an error in your stylesheet - and this
implementation isn't especially helpful in tracking it down for you.

Hacks
"""""

Because CSX strips out comments, hacks that rely on legacy browsers' incorrect
handling of them won't work ... but you shouldn't be using them anyway.

Tricks like the one employed by some CSS resets::

    blockquote:before, blockquote:after,
    q:before, q:after {
        content: '';
        content: none;
    }

... won't work as intended either, because (in this implementation at least),
all but the last declaration for a particular property in each rule is simply
discarded. This might be considered a bug.

Credits / Copyright
-------------------

CSX was created by Zero Piraeus <z@etiol.net>, but inspired by an article on
Eric Meyer's blog about nested scopes in CSS. It's released under the GNU
General Public License (version 3 or later), a copy of which is included with
this distribution in the file "COPYING".


.. [1]  In this implementation, Python's internal recursion limits apply, but
        you're unlikely to hit those in any sane stylesheet.

