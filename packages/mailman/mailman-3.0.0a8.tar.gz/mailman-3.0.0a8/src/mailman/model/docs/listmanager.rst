========================
The mailing list manager
========================

The ``IListManager`` is how you create, delete, and retrieve mailing list
objects.

    >>> from mailman.interfaces.listmanager import IListManager
    >>> from zope.component import getUtility
    >>> list_manager = getUtility(IListManager)


Creating a mailing list
=======================

Creating the list returns the newly created IMailList object.

    >>> from mailman.interfaces.mailinglist import IMailingList
    >>> mlist = list_manager.create('_xtest@example.com')
    >>> IMailingList.providedBy(mlist)
    True

All lists with identities have a short name, a host name, and a fully
qualified listname.  This latter is what uniquely distinguishes the mailing
list to the system.

    >>> print mlist.list_name
    _xtest
    >>> print mlist.mail_host
    example.com
    >>> print mlist.fqdn_listname
    _xtest@example.com

If you try to create a mailing list with the same name as an existing list,
you will get an exception.

    >>> list_manager.create('_xtest@example.com')
    Traceback (most recent call last):
    ...
    ListAlreadyExistsError: _xtest@example.com

It is an error to create a mailing list that isn't a fully qualified list name
(i.e. posting address).

    >>> list_manager.create('foo')
    Traceback (most recent call last):
    ...
    InvalidEmailAddressError: foo


Deleting a mailing list
=======================

Use the list manager to delete a mailing list.

    >>> list_manager.delete(mlist)
    >>> sorted(list_manager.names)
    []

After deleting the list, you can create it again.

    >>> mlist = list_manager.create('_xtest@example.com')
    >>> print mlist.fqdn_listname
    _xtest@example.com


Retrieving a mailing list
=========================

When a mailing list exists, you can ask the list manager for it and you will
always get the same object back.

    >>> mlist_2 = list_manager.get('_xtest@example.com')
    >>> mlist_2 is mlist
    True

If you try to get a list that doesn't existing yet, you get ``None``.

    >>> print list_manager.get('_xtest_2@example.com')
    None

You also get ``None`` if the list name is invalid.

    >>> print list_manager.get('foo')
    None


Iterating over all mailing lists
================================

Once you've created a bunch of mailing lists, you can use the list manager to
iterate over either the list objects, or the list names.

    >>> mlist_3 = list_manager.create('_xtest_3@example.com')
    >>> mlist_4 = list_manager.create('_xtest_4@example.com')
    >>> sorted(list_manager.names)
    [u'_xtest@example.com', u'_xtest_3@example.com', u'_xtest_4@example.com']
    >>> sorted(m.fqdn_listname for m in list_manager.mailing_lists)
    [u'_xtest@example.com', u'_xtest_3@example.com', u'_xtest_4@example.com']
