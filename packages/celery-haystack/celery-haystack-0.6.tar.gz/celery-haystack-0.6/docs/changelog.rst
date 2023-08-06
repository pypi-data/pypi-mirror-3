Changelog
=========

v0.6 (2012-06-27)
-----------------

* *backwards incompatible change* Added support for
  `django-celery-transactions`_ to make sure the tasks are respecting
  Django's transaction management. It holds on to Celery tasks
  until the current database transaction is committed, avoiding potential
  race conditions as described in `Celery's user guide`_.

  This is **enabled by default** but can be disabled in case you want
  to manually manage the tranasctions:

      CELERY_HAYSTACK_TRANSACTION_SAFE = False

* Refactored the error handling to always return a message about what
  happened in every step of the index interaction. Raise exception about
  misconfiguration and wrong parameters quicker.

* Improved support for multiple search indexes as implemented by
  Haystack 2.X. Many thanks to Germán M. Bravo (Kronuz).

.. _`django-celery-transactions`: https://github.com/chrisdoble/django-celery-transactions 
.. _`Celery's user guide`: http://celery.readthedocs.org/en/latest/userguide/tasks.html#database-transactions

v0.5 (2012-05-23)
-----------------

* Moved repository to personal account again: http://github.com/jezdez/celery-haystack

* Removed versiontools dependency again.

* Moved to using Travis-CI for tests: http://travis-ci.org/jezdez/celery-haystack

v0.4 (2011-09-17)
-----------------

* Fixed bug which caused the deletion of an item to not happen correctly.
  Please rebuild your Haystack indexes using the ``rebuild_index``
  management command.

* Addded initial Sphinx documentation: http://celery-haystack.rtfd.org

* Revamped the tets to test the search results, not only queuing.

v0.3.1 (2011-08-22)
-------------------

* Minor bugfix in new appconf support code.

v0.3 (2011-08-22)
-----------------

* Moved configuration defaults handling to django-appconf_.

* Fixed issue that occured when retrying a task.

.. _django-appconf: http://pypi.python.org/pypi/django-appconf

v0.2.1 (2011-08-05)
-------------------

* Fixed typo in exception message handling.

v0.2 (2011-08-04)
-----------------

* Added support for Haystack 1.2.X.

* Properly stop indexing if instance couldn't be found.

* Forced Celery task config values to be of the correct type.

v0.1.2 (2011-07-29) and v0.1.3 (2011-08-01)
-------------------------------------------

* Removed stale print statement.

v0.1.1 (2011-07-29)
-------------------

* Fixed packaging issue (added manifest template).


v0.1 (2011-07-29)
-----------------

* Initial release.
