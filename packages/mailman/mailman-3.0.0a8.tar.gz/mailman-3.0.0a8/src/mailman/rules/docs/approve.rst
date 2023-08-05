=====================
Pre-approved postings
=====================

Messages can contain a pre-approval, which is used to bypass the message
approval queue.  This has several use cases:

- A list administrator can send an emergency message to the mailing list from
  an unregistered address, say if they are away from their normal email.

- An automated script can be programmed to send a message to an otherwise
  moderated list.

In order to support this, a mailing list can be given a *moderator password*
which is shared among all the administrators.

    >>> mlist = create_list('_xtest@example.com')
    >>> mlist.moderator_password = 'abcxyz'

The ``approved`` rule determines whether the message contains the proper
approval or not.

    >>> rule = config.rules['approved']
    >>> print rule.name
    approved


No approval
===========

If the message has no ``Approve:`` or ``Approved:`` header (or their ``X-``
equivalents), then the rule does not match.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... An important message.
    ... """)
    >>> rule.check(mlist, msg, {})
    False

If the message has an ``Approve:``, ``Approved:``, ``X-Approve:``, or
``X-Approved:`` header with a value that does not match the moderator
password, then the rule does not match.  However, the header is still removed.
::

    >>> msg['Approve'] = '12345'
    >>> rule.check(mlist, msg, {})
    False
    >>> print msg['approve']
    None

    >>> del msg['approve']
    >>> msg['Approved'] = '12345'
    >>> rule.check(mlist, msg, {})
    False
    >>> print msg['approved']
    None

    >>> del msg['approved']
    >>> msg['X-Approve'] = '12345'
    >>> rule.check(mlist, msg, {})
    False
    >>> print msg['x-approve']
    None

    >>> del msg['x-approve']
    >>> msg['X-Approved'] = '12345'
    >>> rule.check(mlist, msg, {})
    False
    >>> print msg['x-approved']
    None

    >>> del msg['x-approved']


Using an approval header
========================

If the moderator password is given in an ``Approve:`` header, then the rule
matches, and the ``Approve:`` header is stripped.

    >>> msg['Approve'] = 'abcxyz'
    >>> rule.check(mlist, msg, {})
    True
    >>> print msg['approve']
    None

Similarly, for the ``Approved:`` header.

    >>> del msg['approve']
    >>> msg['Approved'] = 'abcxyz'
    >>> rule.check(mlist, msg, {})
    True
    >>> print msg['approved']
    None

The headers ``X-Approve:`` and ``X-Approved:`` are treated the same way.
::

    >>> del msg['approved']
    >>> msg['X-Approve'] = 'abcxyz'
    >>> rule.check(mlist, msg, {})
    True
    >>> print msg['x-approve']
    None

    >>> del msg['x-approve']
    >>> msg['X-Approved'] = 'abcxyz'
    >>> rule.check(mlist, msg, {})
    True
    >>> print msg['x-approved']
    None

    >>> del msg['x-approved']


Using a pseudo-header
=====================

Different mail user agents have varying degrees to which they support custom
headers like ``Approve:`` and ``Approved:``.  For this reason, Mailman also
supports using a *pseudo-header*, which is really just the first
non-whitespace line in the payload of the message.  If this pseudo-header
looks like a matching ``Approve:`` or ``Approved:`` header, the message is
similarly allowed to pass.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... Approve: abcxyz
    ... An important message.
    ... """)
    >>> rule.check(mlist, msg, {})
    True

The pseudo-header is removed.

    >>> print msg.as_string()
    From: aperson@example.com
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    <BLANKLINE>

Similarly for the ``Approved:`` header.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... Approved: abcxyz
    ... An important message.
    ... """)
    >>> rule.check(mlist, msg, {})
    True

    >>> print msg.as_string()
    From: aperson@example.com
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    <BLANKLINE>

As before, a mismatch in the pseudo-header does not approve the message, but
the pseudo-header line is still removed.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... Approve: 123456
    ... An important message.
    ... """)
    >>> rule.check(mlist, msg, {})
    False

    >>> print msg.as_string()
    From: aperson@example.com
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    <BLANKLINE>

Similarly for the ``Approved:`` header.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... Approved: 123456
    ... An important message.
    ... """)
    >>> rule.check(mlist, msg, {})
    False

    >>> print msg.as_string()
    From: aperson@example.com
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    <BLANKLINE>


MIME multipart support
======================

Mailman searches for the pseudo-header as the first non-whitespace line in the
first ``text/plain`` message part of the message.  This allows the feature to
be used with MIME documents.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: application/x-ignore
    ...
    ... Approve: 123456
    ... The above line will be ignored.
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approve: abcxyz
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    True

Like before, the pseudo-header is removed, but only from the text parts.

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Type: application/x-ignore
    <BLANKLINE>
    Approve: 123456
    The above line will be ignored.
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--
    <BLANKLINE>

The same goes for the ``Approved:`` message.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: application/x-ignore
    ...
    ... Approved: 123456
    ... The above line will be ignored.
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approved: abcxyz
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    True

And the header is removed.

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Type: application/x-ignore
    <BLANKLINE>
    Approved: 123456
    The above line will be ignored.
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--
    <BLANKLINE>

Here, the correct password is in the non-``text/plain`` part, so it is ignored.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: application/x-ignore
    ...
    ... Approve: abcxyz
    ... The above line will be ignored.
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approve: 123456
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    False

And yet the pseudo-header is still stripped.

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Type: application/x-ignore
    <BLANKLINE>
    Approve: abcxyz
    The above line will be ignored.
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--

As before, the same goes for the ``Approved:`` header.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: application/x-ignore
    ...
    ... Approved: abcxyz
    ... The above line will be ignored.
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approved: 123456
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    False

And the pseudo-header is removed.

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Type: application/x-ignore
    <BLANKLINE>
    Approved: abcxyz
    The above line will be ignored.
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--


Stripping text/html parts
=========================

Because some mail readers will include both a ``text/plain`` part and a
``text/html`` alternative, the ``approved`` rule has to search the
alternatives and strip anything that looks like an ``Approve:`` or
``Approved:`` headers.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: text/html
    ...
    ... <html>
    ... <head></head>
    ... <body>
    ... <b>Approved: abcxyz</b>
    ... <p>The above line will be ignored.
    ... </body>
    ... </html>
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approved: abcxyz
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    True

And the header-like text in the ``text/html`` part was stripped.

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/html; charset="us-ascii"
    <BLANKLINE>
    <html>
    <head></head>
    <body>
    <b></b>
    <p>The above line will be ignored.
    </body>
    </html>
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--
    <BLANKLINE>

This is true even if the rule does not match.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... MIME-Version: 1.0
    ... Content-Type: multipart/mixed; boundary="AAA"
    ...
    ... --AAA
    ... Content-Type: text/html
    ...
    ... <html>
    ... <head></head>
    ... <body>
    ... <b>Approve: 123456</b>
    ... <p>The above line will be ignored.
    ... </body>
    ... </html>
    ...
    ... --AAA
    ... Content-Type: text/plain
    ...
    ... Approve: 123456
    ... An important message.
    ... --AAA--
    ... """)
    >>> rule.check(mlist, msg, {})
    False

    >>> print msg.as_string()
    From: aperson@example.com
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="AAA"
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/html; charset="us-ascii"
    <BLANKLINE>
    <html>
    <head></head>
    <body>
    <b></b>
    <p>The above line will be ignored.
    </body>
    </html>
    <BLANKLINE>
    --AAA
    Content-Transfer-Encoding: 7bit
    MIME-Version: 1.0
    Content-Type: text/plain; charset="us-ascii"
    <BLANKLINE>
    An important message.
    --AAA--
    <BLANKLINE>
