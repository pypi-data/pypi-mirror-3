
This package provides additional loghandlers for use with the Python
standardlib `logging` module.

Currently, only one additional logging handler is provided, which
manages log file rotation based on Cron-like settings. So you can tell
to rotate the logs at every day, week, month, or similar. Different to
the `logging.handlers.TimedRotatingFileHandler` you can expect the
rotation to happen at beginning of intervals.

For instance, if you start daily logging with
`logging.handlers.TimedRotatingFileHandler` at 11:12h, a rollover will
happen at 11:12h on the next day. With
`ulif.loghandlers.DatedRotatingFileHandler` the rollover will instead
happen at midnight, regardless of when you started the logging.

Furthermore you can let the number of backup files increase
indefinitely by passing *backupCount* = -1.

Please note, that this package is still in a very early state and
changes, also to the API, are likely to happen in near future.

Comments and patches are welcome. Please send these to uli at gnufix
dot de.

Installation
============

The package can easily be installed by::

  $ pip install ulif.loghandlers

Afterwards you can use ulif.loghandlers in your Python programmes. See
the documentation_ for details.

.. _documentation: http://packages.python.org/ulif.loghandlers
