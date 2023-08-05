==================
Message decoration
==================

Message decoration is the process of adding headers and footers to the
original message.  A handler module takes care of this based on the settings
of the mailing list and the type of message being processed.

    >>> mlist = create_list('_xtest@example.com')
    >>> msg_text = """\
    ... From: aperson@example.org
    ...
    ... Here is a message.
    ... """
    >>> msg = message_from_string(msg_text)


Short circuiting
================

Digest messages get decorated during the digest creation phase so no extra
decorations are added for digest messages.
::

    >>> from mailman.pipeline.decorate import process
    >>> process(mlist, msg, dict(isdigest=True))
    >>> print msg.as_string()
    From: aperson@example.org
    <BLANKLINE>
    Here is a message.

    >>> process(mlist, msg, dict(nodecorate=True))
    >>> print msg.as_string()
    From: aperson@example.org
    <BLANKLINE>
    Here is a message.


Decorating simple text messages
===============================

Text messages that have no declared content type character set are by default,
encoded in us-ascii.  When the mailing list's preferred language is ``en``
(i.e. English), the character set of the mailing list and of the message will
match.  In this case, and when the header and footer have no interpolation
placeholder variables, the message's payload will be prepended by the verbatim
header, and appended with the verbatim footer.

    >>> msg = message_from_string(msg_text)
    >>> mlist.msg_header = 'header\n'
    >>> mlist.msg_footer = 'footer'
    >>> mlist.preferred_language = 'en'
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    From: aperson@example.org
    ...
    <BLANKLINE>
    header
    Here is a message.
    footer

Mailman supports a number of interpolation variables, placeholders in the
header and footer for information to be filled in with mailing list specific
data.  An example of such information is the mailing list's `real name` (a
short descriptive name for the mailing list).

    >>> msg = message_from_string(msg_text)
    >>> mlist.msg_header = '$real_name header\n'
    >>> mlist.msg_footer = '$real_name footer'
    >>> mlist.real_name = 'XTest'
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    From: aperson@example.org
    ...
    XTest header
    Here is a message.
    XTest footer

You can't just pick any interpolation variable though; if you do, the variable
will remain in the header or footer unchanged.

    >>> msg = message_from_string(msg_text)
    >>> mlist.msg_header = '$dummy header\n'
    >>> mlist.msg_footer = '$dummy footer'
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    From: aperson@example.org
    ...
    $dummy header
    Here is a message.
    $dummy footer


Handling RFC 3676 'format=flowed' parameters
============================================

RFC 3676 describes a standard by which text/plain messages can marked by
generating MUAs for better readability in compatible receiving MUAs.  The
``format`` parameter on the text/plain ``Content-Type`` header gives hints as
to how the receiving MUA may flow and delete trailing whitespace for better
display in a proportional font.

When Mailman sees text/plain messages with such RFC 3676 parameters, it
preserves these parameters when it concatenates headers and footers to the
message payload.

    >>> mlist.msg_header = 'header'
    >>> mlist.msg_footer = 'footer'
    >>> mlist.preferred_language = 'en'
    >>> msg = message_from_string("""\
    ... From: aperson@example.org
    ... Content-Type: text/plain; format=flowed; delsp=no
    ... 
    ... Here is a message\x20
    ... with soft line breaks.
    ... """)
    >>> process(mlist, msg, {})
    >>> # Don't use 'print' here as above because it won't be obvious from the
    >>> # output that the soft-line break space at the end of the 'Here is a
    >>> # message' line will be retained in the output.
    >>> print msg['content-type']
    text/plain; format="flowed"; delsp="no"; charset="us-ascii"
    >>> [line for line in msg.get_payload().splitlines()]
    ['header', 'Here is a message ', 'with soft line breaks.', 'footer']


Decorating mixed-charset messages
=================================

When a message has no explicit character set, it is assumed to be us-ascii.
However, if the mailing list's preferred language has a different character
set, Mailman will still try to concatenate the header and footer, but it will
convert the text to utf-8 and base-64 encode the message payload.
::

    # 'ja' = Japanese; charset = 'euc-jp'
    >>> mlist.preferred_language = 'ja'
    >>> mlist.msg_header = '$description header'
    >>> mlist.msg_footer = '$description footer'
    >>> mlist.description = '\u65e5\u672c\u8a9e'

    >>> from email.message import Message
    >>> msg = Message()
    >>> msg.set_payload('Fran\xe7aise', 'iso-8859-1')
    >>> print msg.as_string()
    MIME-Version: 1.0
    Content-Type: text/plain; charset="iso-8859-1"
    Content-Transfer-Encoding: quoted-printable
    <BLANKLINE>
    Fran=E7aise
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    MIME-Version: 1.0
    Content-Type: text/plain; charset="utf-8"
    Content-Transfer-Encoding: base64
    <BLANKLINE>
    5pel5pys6KqeIGhlYWRlcgpGcmFuw6dhaXNlCuaXpeacrOiqniBmb290ZXI=

Sometimes the message even has an unknown character set.  In this case,
Mailman has no choice but to decorate the original message with MIME
attachments.

    >>> mlist.preferred_language = 'en'
    >>> mlist.msg_header = 'header'
    >>> mlist.msg_footer = 'footer'
    >>> msg = message_from_string("""\
    ... From: aperson@example.org
    ... Content-Type: text/plain; charset=unknown
    ... Content-Transfer-Encoding: 7bit
    ...
    ... Here is a message.
    ... """)
    >>> process(mlist, msg, {})
    >>> msg.set_boundary('BOUNDARY')
    >>> print msg.as_string()
    From: aperson@example.org
    Content-Type: multipart/mixed; boundary="BOUNDARY"
    <BLANKLINE>
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    header
    --BOUNDARY
    Content-Type: text/plain; charset=unknown
    Content-Transfer-Encoding: 7bit
    <BLANKLINE>
    Here is a message.
    <BLANKLINE>
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    footer
    --BOUNDARY--


Decorating multipart messages
=============================

Multipart messages have to be decorated differently.  The header and footer
cannot be simply concatenated into the payload because that will break the
MIME structure of the message.  Instead, the header and footer are attached as
separate MIME subparts.

When the outer part is ``multipart/mixed``, the header and footer can have a
``Content-Disposition`` of ``inline`` so that MUAs can display these headers
as if they were simply concatenated.

    >>> mlist.preferred_language = 'en'
    >>> mlist.msg_header = 'header'
    >>> mlist.msg_footer = 'footer'
    >>> part_1 = message_from_string("""\
    ... From: aperson@example.org
    ...
    ... Here is the first message.
    ... """)
    >>> part_2 = message_from_string("""\
    ... From: bperson@example.com
    ...
    ... Here is the second message.
    ... """)
    >>> from email.mime.multipart import MIMEMultipart
    >>> msg = MIMEMultipart('mixed', boundary='BOUNDARY',
    ...                     _subparts=(part_1, part_2))
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    Content-Type: multipart/mixed; boundary="BOUNDARY"
    MIME-Version: 1.0
    <BLANKLINE>
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    header
    --BOUNDARY
    From: aperson@example.org
    <BLANKLINE>
    Here is the first message.
    <BLANKLINE>
    --BOUNDARY
    From: bperson@example.com
    <BLANKLINE>
    Here is the second message.
    <BLANKLINE>
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    footer
    --BOUNDARY--


Decorating other content types
==============================

Non-multipart non-text content types will get wrapped in a ``multipart/mixed``
so that the header and footer can be added as attachments.

    >>> msg = message_from_string("""\
    ... From: aperson@example.org
    ... Content-Type: image/x-beautiful
    ...
    ... IMAGEDATAIMAGEDATAIMAGEDATA
    ... """)
    >>> process(mlist, msg, {})
    >>> msg.set_boundary('BOUNDARY')
    >>> print msg.as_string()
    From: aperson@example.org
    ...
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    header
    --BOUNDARY
    Content-Type: image/x-beautiful
    <BLANKLINE>
    IMAGEDATAIMAGEDATAIMAGEDATA
    <BLANKLINE>
    --BOUNDARY
    Content-Type: text/plain; charset="us-ascii"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Content-Disposition: inline
    <BLANKLINE>
    footer
    --BOUNDARY--
