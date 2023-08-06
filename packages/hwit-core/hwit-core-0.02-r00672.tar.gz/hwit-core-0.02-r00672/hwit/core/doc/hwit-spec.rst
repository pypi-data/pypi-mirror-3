:Author:    D Haynes
:Date:      June 2009

..  sectnum::
    :start: 2

HWIT File Format
================

This document describes how to make a HWIT_ file. Such files are
containers for human-readable text, and can be used to implement
forms and questionnaires, or carry business data between automated
processes.

The reference implementation of this specification is the `hwit.core`
library, available from the HWIT_ project site.

In this specification, the terms, `file`, `document` and `container`
are used interchangeably to refer to the serialised form of a `HWIT`
Container object.

References
~~~~~~~~~~

..  target-notes::

Licence
~~~~~~~

::

    This file is part of the HWIT distribution.

    HWIT is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    HWIT is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with HWIT.  If not, see <http://www.gnu.org/licenses/>.


Trademark declaration
~~~~~~~~~~~~~~~~~~~~~

The initials `hwit` and `HWIT` are trademarks of Thuswise Limited, a
UK registered company.

File structure
~~~~~~~~~~~~~~

A HWIT_ container is a valid XHTML_ file (see also DOCTYPE_ below).
`W3C validator`_ should return no error on a `HWIT` file.

..  sidebar:: Regression

    As of mid-November 2009, the `W3C validator`_ no longer approves
    a standard HWIT container. I intend to resolve this issue,
    but there remains work to do to achieve compliance.

The `HWIT` document may contain metadata_ in the `head`. The `body`
may contain any amount of XHTML content, subject to the restrictions
set out in `Forbidden tags`_ and `Forbidden content`_ below.

In among the `body` content may appear one or more `HWIT` Group_ s.
A `group` is a semi-structured section of the document which defines one
or more Field_ s. A `field` may be read-only, or it may be configured to
accept data. A `group` may define the number of `fields` required to
be correctly completed.  

The data in `fields` can be checked against a recognised type.  `hwit.checks`
defines several checker classes for this purpose (see Validation_). 

DOCTYPE
"""""""

The doctype declaration shall be as follows::

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

Metadata
""""""""

Metadata may be placed in the `head` of the file in the manner
established by XHTML_. `HWIT` defines some custom metadata as follows:

Authorship
''''''''''

The author (or creating program) of a HWIT file can store his name
as the `hwit_originator` like this::

    <meta name="hwit_originator" content="hwit project" />

Keywords
''''''''

Uncompressed HWIT files are easy to search because they contain only
plain text. You can also tag the whole document with topic keywords,
or business-specific terms. Multiple entries are separated by commas::

    <meta name="hwit_keywords" content="test, small" />

Identity
''''''''

A Container has no concept of `name`, so you can rename the file without
breaking any internal reference.

However, there is a `hwit_namebase` keyword, which allows you to define
a string as a short description of the file.

An important property of HWIT files is that completed returns may be
stored alongside each other in a directory. Therefore, the `hwit.core`
library uses the `hwit_namebase` string as a prefix when saving the file.
It adds a serial number to provide name diversity.

To make use of this feature, define a `hwit_namebase` as follows::

    <meta name="hwit_namebase" content="hwit-poll" />

Versioning
''''''''''

It is useful for administration purposes to add an identifier to the HWIT
file so you can distinguish between different revisions of the same form.
The `hwit_serial` keyword is for this purpose::

    <meta name="hwit_serial" content="0123456789" />

The interpretation of this value is entirely up to the author; it doesn't
even need to be a number.

Time to live
''''''''''''

Sometimes users don't fill out forms straight away, and while they are
hesitating, the rest of the world moves on. The `hwit_validto` keyword
is available to help the user understand the urgency of your request for
data. The given value must conform to `ISO 8601`_ for the representation
of dates and times::

    <meta name="hwit_validto" content="2009-10-31" />

HWIT-aware programs may use this value to prioritise forms for the user
to fill out. Note that this value is not to be used as any kind of
security feature; the user is just as able to change it as the author
of the form!

Forbidden tags
""""""""""""""

The following tags are not permitted in HWIT files:

    *   area
    *   button
    *   fieldset
    *   form
    *   img
    *   input
    *   legend
    *   map
    *   noscript
    *   object
    *   optgroup
    *   option
    *   param
    *   script
    *   select
    *   textarea
    *   applet
    *   b
    *   big
    *   blink
    *   center
    *   embed
    *   font
    *   frame
    *   frameset
    *   iframe
    *   hr
    *   i
    *   layer
    *   marquee
    *   small
    *   sub
    *   sup
    *   tt
    *   u

The `link` tag is also currently not permitted, although this
restriction is under review.

Forbidden content
"""""""""""""""""

Various methods exist for embedding non-text content in XHTML documents.
None of them is permitted in a `HWIT` file. Specifically, this forbids:

    *   `Data URLs`_
    *   CDATA
    *   MIME Encoded-word
    *   base64 encoding

Modelled objects
~~~~~~~~~~~~~~~~

Container
"""""""""

Role
''''

The purpose of `HWIT` is to place readable, typed data within the context
of a web document. The entirety of a `HWIT` file is modelled as the
`Container`. Parsing a `HWIT` file shall result in a single in-memory
`Container` object.

Written form
''''''''''''

Writing a `Container` object shall produce a normative version of the
`HWIT` file.

Group
"""""

Role
''''

Wherever typed data is placed in the `Container`, it is enclosed
in a `Group`. Data items within a group may be related in some way;

    *   they may be classified under the same business topic
    *   they may aggregate to construct a defined business object
    *   they may be possible (perhaps mutually exclusive) values for a
        defined variable

Any text documenting the business purpose of the group also attaches
to that group.

The group may define a positive integer, whose significance is the
number of data items which must be populated for that group to be
considered complete.

A group has an `id` which is unique among all groups in the container.
 
Written form
''''''''''''

    1.  A group is a XHTML `<div></div>` element, to which a class of
        *hwit_group* has been applied.
    2.  The *div* must have an XHTML-compliant `id` attribute.
    3.  The *div* must contain a single XHTML *definition list*, further
        explained below.

The *div* may have an attribute of *hwit_fillany*, as described below
(specify).

Any text considered applicable to the entire group (forming an
explanatory note, for example), must appear within `<p></p>` tags,
either above or below the *definition list*. Such text is optional.

Field
"""""

Role
''''

A `field` holds the name and optionally, the value of a single data
item. A field is contained within a group. It has a `name` which is
unique within the parent group.

A `field` may be `editable`, or not. A `field` may be `mandatory`, or
not.  A `field` may define a `validator` for its data.

A `field` may define additional information to aid in its correct
completion.

Written form
''''''''''''

    1.  The field items of the group are stored within the *definition list*.
    2.  Each field in the list is represented by a `<dt></dt>` element.
    3.  The *dt* element contains the name of the field. It must
        be case insensitively unique within the group.
    4.  Each *dt* element is followed by one or more related `<dd></dd>`
        elements.
    5.  The first `<dd></dd>` element which follows is the placeholder
        for text, either predefined or for user entry.

Further `<dd></dd>` elements may follow it, decorating the field with
other features, such as:

    *   A textual description of the data required
    *   A cross-reference hypertext link referring to another item
        in the container
    *   A tooltip prompting certain action related to an external URL
 
Editable fields
'''''''''''''''

Every *dd* field is assumed to be non-editable, unless specified
otherwise. To specify a field which is editable, set the `hwit_edit`
attribute to `true`:

..  code-block:: html

    <dd hwit_edit="true"></dd>

Mandatory fields
''''''''''''''''

Every *dd* field is assumed to be optional, unless specified
otherwise. To specify a field which is mandatory, set the `hwit_fill`
attribute to `true`:

..  code-block:: html

    <dd hwit_fill="true"></dd>

Validation
''''''''''

`hwit.checks` wraps common functions, eg: `email.utils.parseaddr` to provide
`typer` objects which can validate the contents of a field.

Typer objects are callables. When used as such, they provide a permissive
mode of validation. If you want an explicitly formatted field, you may
name one of the typer's methods as a more specific check.

For example, to check that a field contains a time value, accepting as
many formats as possible, specify a `hwit_check` attribute on the field
with the name of the typer class:

..  code-block:: html

    <dd hwit_check="hwit.checks.common.timetyper"></dd>

To insist that the time is expressed in `ISO 8601`_ format, use the
appropriate `timetyper` method instead:

..  code-block:: html

    <dd hwit_check="hwit.checks.common.timetyper.isotime"></dd>

Form filler applications may choose to use the *hwit_check* attribute to
decide which GUI widget to provide to the user. **TODO: typer
docstrings**

At the time of writing, the only reference for available typers is the
code itself. See the module `hwit.checks.common`.

Tooltips
''''''''

A field may take an additional piece of data, to act as a `tooltip` to
clarify the specific intention of the field. In order to be properly
covered by the HWIT styling rules, the tooltip should be formulated as
shown here:

..  code-block:: html
    
    <dd><a href="http://www.python.org/docs" class="hwit_tip">
    format<span>checked by email.utils.parseaddr</span>
    </a></dd>

Cross references
''''''''''''''''

A field may include a `cross reference` to provide further exposition
of the subject matter addressed by the field. A cross reference
requires a `reference callout`_ in the field, and a matching
`reference target`_ in a special group at the end.

Reference callout
-----------------

..  code-block:: html

    <dd><a href="#item_049">more info...</a></dd>

Reference target
----------------

A single reference target group may appear at the end of the container.
Reference groups are formed as per field groups, but their class is set
to *hwit_refs*.

..  code-block:: html

    <h2>References</h2>
    <div id="bag_003" class="hwit_refs">
    <dl>
    <dt><a id="item_049">Email</a></dt>
    <dd>This is some more info on how to get your own email address.</dd>
    </dl>
    </div>

Example
~~~~~~~

..  code-block:: html
    :linenos:
    
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="hwit_keywords" content="test, small" />
    <meta name="hwit_namebase" content="hwit-poll" />
    <meta name="hwit_originator" content="hwit project" />
    <meta name="hwit_validto" content="2009-10-31" />
    <title>HWIT project poll</title>
    <style type="text/css">
    </style>
    </head>
    <body>
    <h1>HWIT User poll</h1>
    <p>This is a quick poll to gauge early interest in the HWIT project</p>
    <h2>About You</h2>
    <div id="bag_001" class="hwit_group" hwit_fillany="1" >
    <p>Please describe your interest in HWIT.</p>
    <dl>
    <dt>I want to help develop HWIT</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>I already use HWIT and I can help you test it</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>I'd like to use HWIT for a project of mine</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>Other</dt>
    <dd hwit_edit="true"></dd>
    </dl>
    </div>
    <h2>Technology</h2>
    <div id="bag_002" class="hwit_group" >
    <p>On which platforms will you use HWIT?</p>
    <dl>
    <dt>Windows</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>Linux</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>Mac</dt>
    <dd hwit_check="hwit.checks.common.booltyper" hwit_edit="true"></dd>
    <dt>Other</dt>
    <dd hwit_edit="true"></dd>
    </dl>
    </div>
    <h2>Features</h2>
    <div id="bag_003" class="hwit_group" >
    <p>Please number in order of importance (1 down to 5).</p>
    <dl>
    <dt>Multiplatform support</dt>
    <dd hwit_check="hwit.checks.common.numbertyper.isPositiveInteger" hwit_edit="true" hwit_fill="true"></dd>
    <dt>Language support</dt>
    <dd hwit_check="hwit.checks.common.numbertyper.isPositiveInteger" hwit_edit="true" hwit_fill="true"></dd>
    <dt>Client useability</dt>
    <dd hwit_check="hwit.checks.common.numbertyper.isPositiveInteger" hwit_edit="true" hwit_fill="true"></dd>
    <dt>Data analysis</dt>
    <dd hwit_check="hwit.checks.common.numbertyper.isPositiveInteger" hwit_edit="true" hwit_fill="true"></dd>
    <dt>Defined workflows</dt>
    <dd hwit_check="hwit.checks.common.numbertyper.isPositiveInteger" hwit_edit="true" hwit_fill="true"></dd>
    </dl>
    </div>
    <h2>So we can get in touch</h2>
    <div id="bag_004" class="hwit_group">
    <p></p>
    <dl>
    <dt>Name</dt>
    <dd hwit_edit="true" hwit_fill="true" ></dd>
    <dt>Email</dt>
    <dd hwit_check="hwit.checks.common.emailtyper" hwit_edit="true" hwit_fill="true" ></dd>
    <dd><a href="http://hwit.berlios.de" class="hwit_tip"><span>Click here
    to register an account with the project</span></a></dd>
    <dd><a href="http://hwit.berlios.de">more info...</a></dd>
    </dl>
    </div>
    <p>Thank you for taking part.</p>
    </body>
    </html>

..  footnotes
..  _HWIT:  http://hwit.org
..  _XHTML: http://www.w3.org/TR/xhtml11
..  _W3C Validator: http://validator.w3.org
..  _Data URLs: http://www.ietf.org/rfc/rfc2397.txt
..  _ISO 8601: http://wikipedia.org/wiki/ISO_8601
