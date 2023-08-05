=========================
Command line list removal
=========================

A system administrator can remove mailing lists by the command line.
::

    >>> create_list('test@example.com')
    <mailing list "test@example.com" at ...>

    >>> from mailman.interfaces.listmanager import IListManager
    >>> from zope.component import getUtility
    >>> list_manager = getUtility(IListManager)
    >>> list_manager.get('test@example.com')
    <mailing list "test@example.com" at ...>

    >>> class FakeArgs:
    ...     quiet = False
    ...     archives = False
    ...     listname = ['test@example.com']
    >>> args = FakeArgs()

    >>> from mailman.commands.cli_lists import Remove
    >>> command = Remove()
    >>> command.process(args)
    Removed list: test@example.com
    Not removing archives.  Reinvoke with -a to remove them.

    >>> print list_manager.get('test@example.com')
    None

You can also remove lists quietly.
::

    >>> create_list('test@example.com')
    <mailing list "test@example.com" at ...>

    >>> args.quiet = True
    >>> command.process(args)

    >>> print list_manager.get('test@example.com')
    None


Removing archives
=================

By default 'mailman remove' does not remove a mailing list's archives.
::

    >>> create_list('test@example.com')
    <mailing list "test@example.com" at ...>

    # Fake an mbox file for the mailing list.
    >>> import os
    >>> def make_mbox(fqdn_listname):
    ...     mbox_dir = os.path.join(
    ...         config.PUBLIC_ARCHIVE_FILE_DIR, fqdn_listname + '.mbox')
    ...     os.makedirs(mbox_dir)
    ...     mbox_file = os.path.join(mbox_dir, fqdn_listname + '.mbox')
    ...     with open(mbox_file, 'w') as fp:
    ...         print >> fp, 'A message'
    ...     assert os.path.exists(mbox_file)
    ...     return mbox_file

    >>> mbox_file = make_mbox('test@example.com')
    >>> args.quiet = False
    >>> command.process(args)
    Removed list: test@example.com
    Not removing archives.  Reinvoke with -a to remove them.

    >>> os.path.exists(mbox_file)
    True

Even if the mailing list has been deleted, you can still delete the archives
afterward.
::

    >>> args.archives = True
    
    >>> command.process(args)
    No such list: test@example.com; removing residual archives.

    >>> os.path.exists(mbox_file)
    False
