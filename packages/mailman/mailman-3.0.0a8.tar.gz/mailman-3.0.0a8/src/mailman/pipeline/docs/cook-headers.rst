===============
Cooking headers
===============

Messages that flow through the global pipeline get their headers 'cooked',
which basically means that their headers go through several mostly unrelated
transformations.  Some headers get added, others get changed.  Some of these
changes depend on mailing list settings and others depend on how the message
is getting sent through the system.  We'll take things one-by-one.

    >>> mlist = create_list('_xtest@example.com')
    >>> mlist.subject_prefix = ''
    >>> mlist.include_list_post_header = False
    >>> mlist.archive = True


Saving the original sender
==========================

Because the original sender headers may get deleted or changed, this handler
will place the sender in the message metadata for safe keeping.
::

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... A message of great import.
    ... """)
    >>> msgdata = {}

    >>> from mailman.pipeline.cook_headers import process
    >>> process(mlist, msg, msgdata)
    >>> print msgdata['original_sender']
    aperson@example.com

But if there was no original sender, then the empty string will be saved.

    >>> msg = message_from_string("""\
    ... Subject: No original sender
    ...
    ... A message of great import.
    ... """)
    >>> msgdata = {}
    >>> process(mlist, msg, msgdata)
    >>> print msgdata['original_sender']
    <BLANKLINE>


Mailman version header
======================

Mailman will also insert an ``X-Mailman-Version`` header...

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... A message of great import.
    ... """)
    >>> process(mlist, msg, {})
    >>> from mailman.version import VERSION
    >>> msg['x-mailman-version'] == VERSION
    True

...but only if one doesn't already exist.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... X-Mailman-Version: 3000
    ...
    ... A message of great import.
    ... """)
    >>> process(mlist, msg, {})
    >>> print msg['x-mailman-version']
    3000


Precedence header
=================

Mailman will insert a ``Precedence`` header, which is a de-facto standard for
telling automatic reply software (e.g. ``vacation(1)``) not to respond to this
message.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... A message of great import.
    ... """)
    >>> process(mlist, msg, {})
    >>> print msg['precedence']
    list

But Mailman will only add that header if the original message doesn't already
have one of them.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... Precedence: junk
    ...
    ... A message of great import.
    ... """)
    >>> process(mlist, msg, {})
    >>> print msg['precedence']
    junk


RFC 2919 and 2369 headers
=========================

This is a helper function for the following section.

    >>> def list_headers(msg):
    ...     print '---start---'
    ...     # Sort the List-* headers found in the message.  We need to do
    ...     # this because CookHeaders puts them in a dictionary which does
    ...     # not have a guaranteed sort order.
    ...     for header in sorted(msg.keys()):
    ...         parts = header.lower().split('-')
    ...         if 'list' not in parts:
    ...             continue
    ...         for value in msg.get_all(header):
    ...             print '%s: %s' % (header, value)
    ...     print '---end---'

These RFCs define headers for mailing list actions.  A mailing list should
generally add these headers, but not for messages that aren't crafted for a
specific list (e.g. password reminders in Mailman 2.x).

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, dict(_nolist=True))
    >>> list_headers(msg)
    ---start---
    ---end---

Some people don't like these headers because their mail readers aren't good
about hiding them.  A list owner can turn these headers off.

    >>> mlist.include_rfc2369_headers = False
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> list_headers(msg)
    ---start---
    ---end---

But normally, a list will include these headers.

    >>> mlist.include_rfc2369_headers = True
    >>> mlist.include_list_post_header = True
    >>> mlist.preferred_language = 'en'
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... Message-ID: <12345>
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> list_headers(msg)
    ---start---
    List-Archive: <http://lists.example.com/archives/_xtest@example.com>
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Id: <_xtest.example.com>
    List-Post: <mailto:_xtest@example.com>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    ---end---

If the mailing list has a description, then it is included in the ``List-Id``
header.

    >>> mlist.description = 'My test mailing list'
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> list_headers(msg)
    ---start---
    List-Archive: <http://lists.example.com/archives/_xtest@example.com>
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Id: My test mailing list <_xtest.example.com>
    List-Post: <mailto:_xtest@example.com>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    ---end---

There are some circumstances when the list administrator wants to explicitly
set the ``List-ID`` header.  Start by creating a new domain.
::

    >>> from mailman.interfaces.domain import IDomainManager
    >>> from zope.component import getUtility
    >>> domain = getUtility(IDomainManager).add('mail.example.net')
    >>> mlist.mail_host = 'mail.example.net'

    >>> process(mlist, msg, {})
    >>> print msg['list-id']
    My test mailing list <_xtest.example.com>

    >>> mlist.list_id = '_xtest.mail.example.net'
    >>> process(mlist, msg, {})
    >>> print msg['list-id']
    My test mailing list <_xtest.mail.example.net>

    >>> mlist.mail_host = 'example.com'
    >>> mlist.list_id = '_xtest.example.com'

Any existing ``List-ID`` headers are removed from the original message.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ... List-ID: <123.456.789>
    ...
    ... """)

    >>> process(mlist, msg, {})
    >>> sorted(msg.get_all('list-id'))
    [u'My test mailing list <_xtest.example.com>']

Administrative messages crafted by Mailman will have a reduced set of headers.

    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, dict(reduced_list_headers=True))
    >>> list_headers(msg)
    ---start---
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Id: My test mailing list <_xtest.example.com>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    X-List-Administrivia: yes
    ---end---

With the normal set of ``List-*`` headers, it's still possible to suppress the
``List-Post`` header, which is reasonable for an announce only mailing list.

    >>> mlist.include_list_post_header = False
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> list_headers(msg)
    ---start---
    List-Archive: <http://lists.example.com/archives/_xtest@example.com>
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Id: My test mailing list <_xtest.example.com>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    ---end---

And if the list isn't being archived, it makes no sense to add the
``List-Archive`` header either.

    >>> mlist.include_list_post_header = True
    >>> mlist.archive = False
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> list_headers(msg)
    ---start---
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Id: My test mailing list <_xtest.example.com>
    List-Post: <mailto:_xtest@example.com>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    ---end---


Archived-At
===========

RFC 5064 (draft) defines a new ``Archived-At`` header which contains the url to
the individual message in the archives.  The stock Pipermail archiver doesn't
support this because the url can't be calculated until after the message is
archived.  Because this is done by the archive runner, this information isn't
available to us now.

    >>> print msg['archived-at']
    None


Personalization
===============

The ``To`` field normally contains the list posting address.  However when
messages are fully personalized, that header will get overwritten with the
address of the recipient.  The list's posting address will be added to one of
the recipient headers so that users will be able to reply back to the list.

    >>> from mailman.interfaces.mailinglist import (
    ...     Personalization, ReplyToMunging)
    >>> mlist.personalize = Personalization.full
    >>> mlist.reply_goes_to_list = ReplyToMunging.no_munging
    >>> msg = message_from_string("""\
    ... From: aperson@example.com
    ...
    ... """)
    >>> process(mlist, msg, {})
    >>> print msg.as_string()
    From: aperson@example.com
    X-BeenThere: _xtest@example.com
    X-Mailman-Version: ...
    Precedence: list
    Cc: My test mailing list <_xtest@example.com>
    List-Id: My test mailing list <_xtest.example.com>
    List-Unsubscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-leave@example.com>
    List-Post: <mailto:_xtest@example.com>
    List-Help: <mailto:_xtest-request@example.com?subject=help>
    List-Subscribe: <http://lists.example.com/listinfo/_xtest@example.com>,
        <mailto:_xtest-join@example.com>
    <BLANKLINE>
    <BLANKLINE>
