Changelog
---------

0.11 (2012-08-24)
~~~~~~~~~~~~~~~~~

* Enhance the ``Model.browse()`` method to accept the same
  keyword arguments as the ``Client.search()`` method.

* Fix the verbose level on ``Client.connect()``.

* Fix the ``Record.copy()`` method.

* Fix the ``Record.perm_read()`` method (workaround an OpenERP bug when
  dealing with single ids).

* Drop the ``--search`` argument, because the search terms can be passed as
  positional arguments after the options.  Explain it in the description.

* Fix the shell command.  Request the password interactively if it's not
  in the options and not in the configuration file.


0.10 (2012-08-23)
~~~~~~~~~~~~~~~~~

* Add the ``--verbose`` switch to log the XML-RPC messages.
  Lines are truncated at 79 chars.  Use ``-vv`` or ``-vvv``
  to truncate at 179 or 9999 chars respectively.

* Removed the ``--write`` switch because it's not really useful.
  Use :meth:`Record.write` or :meth:`client.write` for example.

* Stop raising RuntimeError when calling ``Client.model(name)``.
  Simply print the message if the name does not match.

* Fix ``RecordList.read()`` and ``Record.read()`` methods to accept the
  same diversity of ``fields`` arguments as the ``Client.read()`` method.

* ``RecordList.read()`` and ``Record.read()`` return instances of
  ``RecordList`` and ``Record`` for relational fields.

* Optimize: store the name of the ``Record`` when a relational field
  is accessed.

* Fix message wording on module install or upgrade.


0.9.2 (2012-08-22)
~~~~~~~~~~~~~~~~~~

* Fix ``Record.write()`` and ``Record.unlink()`` methods.

* Fix the caching of the ``Model`` keys and fields and the ``Record``
  name.


0.9.1 (2012-08-22)
~~~~~~~~~~~~~~~~~~

* Fix ``client.model()`` method.  Add ``models()`` to the ``globals()``
  in interactive mode.


0.9 (2012-08-22)
~~~~~~~~~~~~~~~~

* Add the Active Record pattern for convenience.  New classes :class:`Model`,
  :class:`RecordList` and :class:`Record`.  The :meth:`Client.model` method
  now returns a single :class:`Model` instance.  These models can be
  reached using camel case attribute too.  Example:
  ``client.model('res.company')`` and ``client.ResCompany`` return the same
  :class:`Model`.

* Refresh the list of modules before install or upgrade.

* List all modules which have ``state not in ('uninstalled', 'uninstallable')``
  when calling ``client.modules(installed=True)``.

* Add documentation.


0.8 (2012-04-24)
~~~~~~~~~~~~~~~~

* Fix ``help(client)`` and ``repr(...)``.

* Add basic safeguards for argument types.


0.7 (2012-04-04)
~~~~~~~~~~~~~~~~

* Fix RuntimeError on connection.


0.6 (2012-04-03)
~~~~~~~~~~~~~~~~

* Support Python 3.

* Return Client method instead of function when calling ``client.write``
  or similar.

* Fix the case where :meth:`~Client.read()` is called with a single id.


0.5 (2012-03-29)
~~~~~~~~~~~~~~~~

* Implement ``Client.__getattr__`` special attribute to call any object
  method, like ``client.write(obj, values)``.  This is somewhat
  redundant with ``client.execute(obj, 'write', values)`` and its
  interactive alias ``do(obj, 'write', values)``.

* Add ``--write`` switch to enable unsafe helpers: ``write``,
  ``create``, ``copy`` and ``unlink``.

* Tolerate domain without square brackets, but show a warning.

* Add long options ``--search`` for ``-s``, ``--interact`` for ``-i``.


0.4 (2012-03-28)
~~~~~~~~~~~~~~~~

* Workaround for ``sys.excepthook`` ignored, related to a
  `Python issue <http://bugs.python.org/issue12643>`__.


0.3 (2012-03-26)
~~~~~~~~~~~~~~~~

* Add ``--config`` and ``--version`` switches.

* Improve documentation with session examples.

* Move the project from Launchpad to GitHub.


0.2 (2012-03-24)
~~~~~~~~~~~~~~~~

* Allow to switch user or database: methods ``client.login`` and
  ``client.connect``.

* Allow ``context=`` keyword argument.

* Add ``access(...)`` method.

* Add ``%(...)s`` formatting for the fields parameter of the ``read(...)`` method.

* Refactor the interactive mode.

* Many improvements.

* Publish on PyPI.


0.1 (2012-03-14)
~~~~~~~~~~~~~~~~

* Initial release.
