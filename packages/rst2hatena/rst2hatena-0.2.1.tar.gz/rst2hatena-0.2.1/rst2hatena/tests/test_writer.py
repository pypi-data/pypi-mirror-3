#!/usr/bin/env python
# -*- coding:utf-8 -*-
import unittest
from docutils.core import publish_file, publish_string

from rst2hatena.hatena_writer import Writer


class WriterTest(unittest.TestCase):
    """
    """
    def setUp(self):
        self.writer = Writer()

    def test_all(self):
        #output = publish_file(source_path='./sample.txt', writer=self.writer)
        #print '===================='
        #print output
        #print '===================='
        self.assert_(True)

    def test_emphasis(self):
        str = """\
emphasis
--------

*emphasis*
  Normally rendered as italics.
"""
        exp_str = """\
*emphasis

:<span style="font-style:italic;">emphasis</span>:Normally rendered as italics.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)

    def test_strong_emphasis(self):
        str = """\
strong emphasis
---------------

**strong emphasis**
  Normally rendered as boldface.
"""
        exp_str = """\
*strong emphasis

:<span style="font-weight:bold;">strong emphasis</span>:Normally rendered as boldface.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)

    def test_interpreted_text(self):
        str = """\
interpreted text
----------------

`interpreted text`
  The rendering and meaning of interpreted text is domain- or application-dependent. It can be used for things like index entries or explicit descriptive markup (like program identifiers).
"""
        exp_str = """\
*interpreted text

:<span style="font-style:italic;">interpreted text</span>:The rendering and meaning of interpreted text is domain- or application-dependent. It can be used for things like index entries or explicit descriptive markup (like program identifiers).

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)

    def test_inline_literal(self):
        str = """\
inline literal
--------------

``inline literal``
  Normally rendered as monospaced text. Spaces should be preserved, but line breaks will not be.
"""
        exp_str = """\
*inline literal

:<span style="font-style:italic;">inline literal</span>:Normally rendered as monospaced text. Spaces should be preserved, but line breaks will not be.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)

    def test_no_reference(self):
        str = """\
reference
---------

reference_
  A simple, one-word hyperlink reference. See Hyperlink Targets.
"""
        exp_str = """\
*reference

:<a href="#reference">reference</a>:A simple, one-word hyperlink reference. See Hyperlink Targets.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_no_phrase_reference(self):
        str = """\
phrase reference
----------------

`phrase reference`_
  A hyperlink reference with spaces or punctuation needs to be quoted with backquotes. See Hyperlink Targets.
"""
        exp_str = """\
*phrase reference

:<a href="#phrase-reference">phrase reference</a>:A hyperlink reference with spaces or punctuation needs to be quoted with backquotes. See Hyperlink Targets.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_no_inline_internal_target(self):
        str = """\
inline internal target
----------------------

_`inline internal target`
  A crossreference target within text. See Hyperlink Targets.
"""
        exp_str = """\
*inline internal target

<!--
Duplicate implicit target name: "inline internal target".
-->

:inline internal target:A crossreference target within text. See Hyperlink Targets.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_standalone_hyperlink(self):
        str = """\
standalone hyperlink
--------------------

http://docutils.sf.net/
  A standalone hyperlink.
"""
        exp_str = """\
*standalone hyperlink

:[http://docutils.sf.net/:title=http://docutils.sf.net/]:A standalone hyperlink.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_section(self):
        str = """\
Section
=======

Subtitle
--------

Titles are underlined (or over- 
and underlined) with a printing 
nonalphanumeric 7-bit ASCII 
character. Recommended choices 
are "``= - ` : ' " ~ ^ _ * + # < >``". 
The underline/overline must be at 
least as long as the title text. 

A lone top-level (sub)section 
is lifted up to be the document's 
(sub)title.
"""
        exp_str = """\
*Section

**Subtitle

Titles are underlined (or over- and underlined) with a printing nonalphanumeric 7-bit ASCII character. Recommended choices are "<span style="font-style:italic;">= - ` : ' " ~ ^ _ * + # < ></span>". The underline/overline must be at least as long as the title text.

A lone top-level (sub)section is lifted up to be the document's (sub)title.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_paragraphs(self):
        str = """\
Paragraphs
==========

This is a paragraph.

Paragraphs line up at their left 
edges, and are normally separated 
by blank lines.
"""
        exp_str = """\
*Paragraphs

This is a paragraph.

Paragraphs line up at their left edges, and are normally separated by blank lines.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_bullet_lists(self):
        str = """\
Bullet Lists
============

Bullet lists:

- This is item 1 
- This is item 2

- Bullets are "-", "*" or "+". 
  Continuing text must be aligned 
  after the bullet and whitespace.

Note that a blank line is required 
before the first item and after the 
last, but is optional between items.
"""
        exp_str = """\
*Bullet Lists

Bullet lists:

- This is item 1
- This is item 2
- Bullets are "-", "*" or "+". Continuing text must be aligned after the bullet and whitespace.

Note that a blank line is required before the first item and after the last, but is optional between items.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_enumerated_lists(self):
        str = """\
Enumerated Lists
================

Enumerated lists:

3. This is the first item 
4. This is the second item 
5. Enumerators are arabic numbers, 
   single letters, or roman numerals 
6. List items should be sequentially 
   numbered, but need not start at 1 
   (although not all formatters will 
   honour the first index). 
#. This item is auto-enumerated
"""
        exp_str = """\
*Enumerated Lists

Enumerated lists:

+ This is the first item
+ This is the second item
+ Enumerators are arabic numbers, single letters, or roman numerals
+ List items should be sequentially numbered, but need not start at 1 (although not all formatters will honour the first index).
+ This item is auto-enumerated

<!--
Enumerated list start value not ordinal-1: "3" (ordinal 3)
-->

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_definition_lists(self):
        str = """\
Definition Lists
================

Definition lists: 

what 
  Definition lists associate a term with 
  a definition. 

how 
  The term is a one-line phrase, and the 
  definition is one or more paragraphs or 
  body elements, indented relative to the 
  term. Blank lines are not allowed 
  between term and definition.
"""
        exp_str = """\
*Definition Lists

Definition lists:

:what:Definition lists associate a term with a definition.

:how:The term is a one-line phrase, and the definition is one or more paragraphs or body elements, indented relative to the term. Blank lines are not allowed between term and definition.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)

    def test_field_lists(self):
        str = """\
Field Lists
===========

Fields
------

:Author: Yosuke Ikeda
:Authors: 
    Tony J. (Tibs) Ibbs, 
    David Goodger
    (and sundry other good-natured folks)

:Organization: Electro Insanity
:Address: Tokyo, Japan
:Contact: alpha.echo.35@gmail.com
:Status: normal
:Date: 2001/08/08
:Copyright: Yosuke Ikeda
:Version: 1.0 of 2001/08/08
:Revision: 12345
:Dedication: To my father.
"""
        exp_str = """\
*Field Lists

**Fields

:Author:Yosuke Ikeda
:Author:Tony J. (Tibs) Ibbs
:Author:David Goodger (and sundry other good-natured folks)
:Organization:Electro Insanity
:Address:Tokyo, Japan
:Contact:[mailto:alpha.echo.35@gmail.com:title=alpha.echo.35@gmail.com]
:Status:normal
:Date:2001/08/08
:Copyright:Yosuke Ikeda
:Version:1.0 of 2001/08/08
:Revision:12345
:Dedication:To my father.
"""
        output = publish_string(str, writer=self.writer)

        print
        self.assertEqual(exp_str, output)


    def test_option_lists(self):
        str = """\
Option Lists
============

-a            command-line option "a" 
-b file       options can have arguments 
              and long descriptions 
--long        options can be long also 
--input=file  long options can also have 
              arguments 
/V            DOS/VMS-style options too
"""
        exp_str = """\
*Option Lists

:-a:command-line option "a"

:-b file:options can have arguments and long descriptions

:--long:options can be long also

:--input=file:long options can also have arguments

:/V:DOS/VMS-style options too

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_literal_blocks(self):
        str = """\
Literal Blocks
==============

A paragraph containing only two colons 
indicates that the following indented 
or quoted text is a literal block. 

:: 

  The paragraph containing only '::' 
  will be omitted from the result. 

The ``::`` may be tacked onto the very 
end of any paragraph. The ``::`` will be 
omitted if it is preceded by whitespace. 
The ``::`` will be converted to a single 
colon if preceded by text, like this:: 

  It's very convenient to use this form. 

Per-line quoting can also be used on 
unindented literal blocks:: 

> Useful for quotes from email and 
> for Haskell literate programming.
"""
        exp_str = """\
*Literal Blocks

A paragraph containing only two colons indicates that the following indented or quoted text is a literal block.

>||
The paragraph containing only '::'
will be omitted from the result.
||<

The <span style="font-style:italic;">::</span> may be tacked onto the very end of any paragraph. The <span style="font-style:italic;">::</span> will be omitted if it is preceded by whitespace. The <span style="font-style:italic;">::</span> will be converted to a single colon if preceded by text, like this:

>||
It's very convenient to use this form.
||<

Per-line quoting can also be used on unindented literal blocks:

>||
> Useful for quotes from email and
> for Haskell literate programming.
||<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_line_blocks(self):
        str = """\
Line Blocks
===========

| Line blocks are useful for addresses, 
| verse, and adornment-free lists. 
| 
| Each new line begins with a 
| vertical bar ("|"). 
|     Line breaks and initial indents 
|     are preserved. 
| Continuation lines are wrapped 
  portions of long lines; they begin 
  with spaces in place of vertical bars.
"""
        exp_str = """\
*Line Blocks

>|
Line blocks are useful for addresses,
verse, and adornment-free lists.

Each new line begins with a
vertical bar ("|").
    Line breaks and initial indents
    are preserved.
Continuation lines are wrapped portions of long lines; they begin with spaces in place of vertical bars.
|<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_block_quotes(self):
        str = """\
Block Quotes
============

Block quotes are just:

    Indented paragraphs,

        and they may nest.
        and they may nest.
"""
        exp_str = """\
*Block Quotes

Block quotes are just:

>>
Indented paragraphs,

    and they may nest. and they may nest.
<<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_doctest_blocks(self):
        str = """\
Doctest Blocks
==============

Doctest blocks are interactive 
Python sessions. They begin with 
"``>>>``" and end with a blank line.

>>> print "This is a doctest block." 
This is a doctest block.
"""
        exp_str = """\
*Doctest Blocks

Doctest blocks are interactive Python sessions. They begin with "<span style="font-style:italic;">>>></span>" and end with a blank line.

>|python|
>>> print "This is a doctest block."
This is a doctest block.
||<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_grid_tables(self):
        str = """\
Grid table
----------

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
| body row 3 | Cells may  | - Cells   |
+------------+ span rows. | - contain |
| body row 4 |            | - blocks. |
+------------+------------+-----------+
"""
        exp_str = """\
*Grid table

|*Header 1|*Header 2|*Header 3|
|body row 1|column 2|column 3|
|body row 2|Cells may span columns.|
|body row 3|Cells may span rows.|- Cells
- contain
- blocks.
|
|body row 4|

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_simple_table(self):
        str = """\
Simple table
------------

=====  =====  ====== 
   Inputs     Output 
------------  ------ 
  A      B    A or B 
=====  =====  ====== 
False  False  False 
True   False  True 
False  True   True 
True   True   True 
=====  =====  ======
"""
        exp_str = """\
*Simple table

|*Inputs|*Output|
|*A|*B|*A or B|
|False|False|False|
|True|False|True|
|False|True|True|
|True|True|True|

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_transitions(self):
        str = """\
Transitions
===========

A transition marker is a horizontal line 
of 4 or more repeated punctuation 
characters.

------------

A transition should not begin or end a 
section or document, nor should two 
transitions be immediately adjacent.
"""
        exp_str = """\
*Transitions

A transition marker is a horizontal line of 4 or more repeated punctuation characters.

<hr>

A transition should not begin or end a section or document, nor should two transitions be immediately adjacent.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_explicit_footnote_reference(self):
        str = """\
Footnote references
-------------------

Footnote references, like [5]_. 
Note that footnotes may get 
rearranged, e.g., to the bottom of 
the "page". [5]_

.. [5] A numerical footnote. Note 
   there's no colon after the ``]``.
"""
        exp_str = """\
*Footnote references

Footnote references, like ((A numerical footnote. Note there's no colon after the <span style="font-style:italic;">]</span>.)). Note that footnotes may get rearranged, e.g., to the bottom of the "page". ((A numerical footnote. Note there's no colon after the <span style="font-style:italic;">]</span>.))

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_explicit_markup_autonumbered_footnotes(self):
        str = """\
Autonumbered footnotes are 
possible, like using [#]_ and [#]_.

.. [#] This is the first one. 
.. [#] This is the second one.

They may be assigned 'autonumber 
labels' - for instance, 
[#fourth]_ and [#third]_.

.. [#third] a.k.a. third_

.. [#fourth] a.k.a. fourth_
"""
        exp_str = """\
Autonumbered footnotes are possible, like using ((This is the first one.)) and ((This is the second one.)).

They may be assigned 'autonumber labels' - for instance, ((a.k.a. <a href="#fourth">fourth</a>)) and ((a.k.a. <a href="#third">third</a>)).

"""

        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_explicit_markup_auto_symbol_footnotes(self):
        str = """\
Auto-symbol footnotes are also 
possible, like this: [*]_ and [*]_.

.. [*] This is the first one. 

.. [*] This is the second one.
"""
        exp_str = """\
Auto-symbol footnotes are also possible, like this: ((This is the first one.)) and ((This is the second one.)).

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_citations(self):
        str = """\
Citation references, like [CIT2002]_. 
Note that citations may get 
rearranged, e.g., to the bottom of 
the "page".

.. [CIT2002] A citation 
   (as often used in journals).

Citation labels contain alphanumerics, 
underlines, hyphens and fullstops. 
Case is not significant.

Given a citation like [this]_, one 
can also refer to it like this_.

.. [this] here.
"""
        exp_str = """\
Citation references, like CIT2002((A citation (as often used in journals).)). Note that citations may get rearranged, e.g., to the bottom of the "page".

Citation labels contain alphanumerics, underlines, hyphens and fullstops. Case is not significant.

Given a citation like this((here.)), one can also refer to it like <a href="#this">this</a>.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_external_hyperlink_targets(self):
        str = """\
External hyperlinks, like Python_.

.. _Python: http://www.python.org/
"""
        exp_str = """\
External hyperlinks, like [http://www.python.org/:title=Python].

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_embedded_uris(self):
        str = """\
External hyperlinks, like `Python <http://www.python.org/>`_.
"""
        exp_str = """\
External hyperlinks, like [http://www.python.org/:title=Python].

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_internal_hyperlink_targets(self):
        str = """\
Internal crossreferences, like example_.

.. _example:

This is an example crossreference target.
"""
        exp_str = """\
Internal crossreferences, like <a href="#example">example</a>.

<a name="example"></a>
This is an example crossreference target.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_indirect_hyperlink_targets(self):
        str = """\
Python_ is `my favourite 
programming language`__.

.. _Python: http://www.python.org/

__ Python_
"""
        exp_str = """\
[http://www.python.org/:title=Python] is [http://www.python.org/:title=my favourite programming language].

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_implicit_hyperlink_targets(self):
        str = """\
Titles are targets, too 
======================= 

Implict references, like `Titles are 
targets, too`_.
"""
        exp_str = """\
*Titles are targets, too

Implict references, like <a href="#titles-are-targets-too">Titles are targets, too</a>.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_directives(self):
        str = """\
For instance:

.. image:: images/ball1.gif
"""
        exp_str = """\
For instance:

<img src="images/ball1.gif">
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_substitution_references_and_definitions(self):
        str = """\
The |biohazard| symbol must be used on containers used to dispose of medical waste.

.. |biohazard| image:: biohazard.png
"""
        exp_str = """\
The <img src="biohazard.png" alt="biohazard"> symbol must be used on containers used to dispose of medical waste.

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_comments(self):
        str = """\
Comment
=======

.. This text will not be shown 
   (but, for instance, in HTML might be 
   rendered as an HTML comment)
"""
        exp_str = """\
*Comment

<!--
This text will not be shown (but, for instance, in HTML might be rendered as an HTML comment)
-->

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_comment_block(self):
        str = """\
Comment block
-------------

An "empty comment" does not 
consume following blocks. 
(An empty comment is ".." with 
blank lines before and after.)

..

        So this block is not "lost", 
        despite its indentation.
"""
        exp_str = """\
*Comment block

An "empty comment" does not consume following blocks. (An empty comment is ".." with blank lines before and after.)

<!--

-->

>>
So this block is not "lost", despite its indentation.
<<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_niconico_directive(self):
        str = """\
Hatena "niconico" notation.

.. niconico:: sm9
"""
        exp_str = """\
Hatena "niconico" notation.

[niconico:sm9]
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_google_directive(self):
        str = """\
Hatena "google" notation.

.. google:: rst2hatena

.. google:: Guid van Rossum
    :target: image

.. google:: Python
    :target: news
"""
        exp_str = """\
Hatena "google" notation.

[google:rst2hatena]
[google:image:Guid van Rossum]
[google:news:Python]
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_amazon_directive(self):
        str = """\
Hatena "amazon" notation.

.. amazon:: Python
"""
        exp_str = """\
Hatena "amazon" notation.

[amazon:Python]
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_wikipedia_directive(self):
        str = """\
Hatena "wikipedia" notation.

.. wikipedia:: Python

.. wikipedia:: Python
    :lang: en
"""
        exp_str = """\
Hatena "wikipedia" notation.

[wikipedia:Python]
[wikipedia:en:Python]
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_twitter_directive(self):
        str = """\
Hatena "twitter" notation.

.. twitter:: 88453766201880576
    :type: title

.. twitter:: 88453766201880576
    :type: tweet

.. twitter:: 88453766201880576
    :type: detail

.. twitter:: 88453766201880576
    :type: tree

.. twitter:: @naoina
"""
        exp_str = """\
Hatena "twitter" notation.

[twitter:88453766201880576:title]
[twitter:88453766201880576:tweet]
[twitter:88453766201880576:detail]
[twitter:88453766201880576:tree]
[twitter:@naoina]
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_twitter_roles(self):
        str = """\
roles for Hatena "twitter" notation.

:twitter:`naoina`
:twitter:`@naoina`

before text :twitter:`@naoina` after text
"""
        exp_str = """\
roles for Hatena "twitter" notation.

[twitter:@naoina] [twitter:@naoina]

before text [twitter:@naoina] after text

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_map_directive(self):
        str = """\
Hatena "map" notation.

.. map::
    :x: 139.6983
    :y: 35.6514

.. map::
    :x: 139.6983
    :y: 35.6514
    :type: map

.. map::
    :x: 139.6983
    :y: 35.6514
    :type: satellite
    :height: 300

.. map::
    :x: 139.6983
    :y: 35.6514
    :type: hybrid
    :width: 300
"""
        exp_str = """\
Hatena "map" notation.

map:x139.6983y35.6514
map:x139.6983y35.6514:map
map:x139.6983y35.6514:satellite:h300
map:x139.6983y35.6514:hybrid:w300
"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


    def test_code_blocks(self):
        str = """\
.. code-block:: python

   def main():
       for i in range(1, 101):
           if i % 15 == 0:
              print "FizzBuzz"
           elif i % 5 == 0:
              print "Buzz"
           elif i % 3 == 0:
              print "Fizz"
           else:
              print i

   if __name__ == '__main__':
       main()
"""
        exp_str = """\
>|python|
def main():
    for i in range(1, 101):
        if i % 15 == 0:
           print "FizzBuzz"
        elif i % 5 == 0:
           print "Buzz"
        elif i % 3 == 0:
           print "Fizz"
        else:
           print i

if __name__ == '__main__':
    main()
||<

"""
        output = publish_string(str, writer=self.writer)
        self.assertEqual(exp_str, output)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WriterTest)
    try:
        from growltestrunner import GrowlTestRunner
        GrowlTestRunner().run(suite)
    except:
        unittest.main()
