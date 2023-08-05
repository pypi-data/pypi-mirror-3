===============
The news runner
===============

The news runner gateways mailing list messages to an NNTP newsgroup.  One of
the most important things this runner does is prepare the message for Usenet
(yes, I know that NNTP is not Usenet, but this runner was originally written
to gate to Usenet, which has its own rules).

    >>> mlist = create_list('_xtest@example.com')
    >>> mlist.linked_newsgroup = 'comp.lang.python'

Some NNTP servers such as INN reject messages containing a set of prohibited
headers, so one of the things that the news runner does is remove these
prohibited headers.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... NNTP-Posting-Host: news.example.com
    ... NNTP-Posting-Date: today
    ... X-Trace: blah blah
    ... X-Complaints-To: abuse@dom.ain
    ... Xref: blah blah
    ... Xref: blah blah
    ... Date-Received: yesterday
    ... Posted: tomorrow
    ... Posting-Version: 99.99
    ... Relay-Version: 88.88
    ... Received: blah blah
    ...
    ... A message
    ... """)
    >>> msgdata = {}

    >>> from mailman.runners.news import prepare_message
    >>> prepare_message(mlist, msg, msgdata)
    >>> msgdata['prepped']
    True
    >>> print msg.as_string()
    From: aperson@example.com
    To: _xtest@example.com
    Newsgroups: comp.lang.python
    Message-ID: ...
    Lines: 1
    <BLANKLINE>
    A message
    <BLANKLINE>

Some NNTP servers will reject messages where certain headers are duplicated,
so the news runner must collapse or move these duplicate headers to an
``X-Original-*`` header that the news server doesn't care about.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... To: two@example.com
    ... Cc: three@example.com
    ... Cc: four@example.com
    ... Cc: five@example.com
    ... Content-Transfer-Encoding: yes
    ... Content-Transfer-Encoding: no
    ... Content-Transfer-Encoding: maybe
    ...
    ... A message
    ... """)
    >>> msgdata = {}
    >>> prepare_message(mlist, msg, msgdata)
    >>> msgdata['prepped']
    True
    >>> print msg.as_string()
    From: aperson@example.com
    Newsgroups: comp.lang.python
    Message-ID: ...
    Lines: 1
    To: _xtest@example.com
    X-Original-To: two@example.com
    CC: three@example.com
    X-Original-CC: four@example.com
    X-Original-CC: five@example.com
    Content-Transfer-Encoding: yes
    X-Original-Content-Transfer-Encoding: no
    X-Original-Content-Transfer-Encoding: maybe
    <BLANKLINE>
    A message
    <BLANKLINE>

But if no headers are duplicated, then the news runner doesn't need to modify
the message.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... Cc: someother@example.com
    ... Content-Transfer-Encoding: yes
    ...
    ... A message
    ... """)
    >>> msgdata = {}
    >>> prepare_message(mlist, msg, msgdata)
    >>> msgdata['prepped']
    True
    >>> print msg.as_string()
    From: aperson@example.com
    To: _xtest@example.com
    Cc: someother@example.com
    Content-Transfer-Encoding: yes
    Newsgroups: comp.lang.python
    Message-ID: ...
    Lines: 1
    <BLANKLINE>
    A message
    <BLANKLINE>


Newsgroup moderation
====================

When the newsgroup is moderated, an ``Approved:`` header with the list's
posting address is added for the benefit of the Usenet system.
::

    >>> from mailman.interfaces.nntp import NewsModeration
    >>> mlist.news_moderation = NewsModeration.open_moderated
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... Approved: this gets deleted
    ...
    ... """)
    >>> prepare_message(mlist, msg, {})
    >>> print msg['approved']
    _xtest@example.com

    >>> mlist.news_moderation = NewsModeration.moderated
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... Approved: this gets deleted
    ...
    ... """)
    >>> prepare_message(mlist, msg, {})
    >>> print msg['approved']
    _xtest@example.com

But if the newsgroup is not moderated, the ``Approved:`` header is not changed.

    >>> mlist.news_moderation = NewsModeration.none
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... To: _xtest@example.com
    ... Approved: this doesn't get deleted
    ...
    ... """)
    >>> prepare_message(mlist, msg, {})
    >>> msg['approved']
    u"this doesn't get deleted"


XXX More of the NewsRunner should be tested.
