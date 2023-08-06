## $Id$
##
## Copyright (C) 2012 Uli Fouquet
##
## This file is part of ulif.loghandlers.
##
## ulif.loghandlers is free software: you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation, either version 3 of
## the License, or (at your option) any later version.
##
## ulif.loghandlers is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with ulif.loghandlers.  If not, see
## <http://www.gnu.org/licenses/>.
##
"""
ulif.loghandlers.handlers -- Additional Log Handlers.
"""
import datetime
import os
import time
from logging.handlers import BaseRotatingHandler, RotatingFileHandler
from stat import ST_MTIME

def next_minute(timestamp):
    """Return begin of next hour after timestamp as a timestamp.
    """
    dt = datetime.datetime.fromtimestamp(timestamp + 60)
    dt = dt.replace(second=0, microsecond=0)
    return time.mktime(dt.timetuple())

def next_hour(timestamp):
    """Return begin of next hour after timestamp as a timestamp.
    """
    dt = datetime.datetime.fromtimestamp(timestamp + 3600)
    dt = dt.replace(minute=0, second=0, microsecond=0)
    return time.mktime(dt.timetuple())

def next_day(timestamp):
    """Return begin of next day after timestamp as a timestamp.
    """
    dt = datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(
        days=1)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return time.mktime(dt.timetuple())

def next_week(timestamp, weekday=0):
    """Return begin of next week after timestamp as a timestamp.

    The start of week can be set with `weekday` (0 for Monday, ..., 6
    for Sunday). Default is Monday.
    """
    curr_wday = time.localtime(timestamp).tm_wday
    day_diff = weekday - curr_wday + 7
    dt = datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(
        days=day_diff)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return time.mktime(dt.timetuple())

def next_month(timestamp):
    """Return begin of next month after timestamp as a timestamp.
    """
    year, month = time.localtime(timestamp)[:2]
    year += month / 12
    month = month % 12 + 1
    dt = datetime.datetime(year, month, 1, 0, 0 ,0)
    return time.mktime(dt.timetuple())

def next_year(timestamp):
    """Return begin of next year after timestamp as a timestamp.
    """
    year = time.localtime(timestamp).tm_year
    dt = datetime.datetime(year+1, 1, 1, 0, 0, 0)
    return time.mktime(dt.timetuple())

class DatedRotatingFileHandler(RotatingFileHandler):
    """
    Handler for logging to a file, rotating the log file at certain timed
    intervals.

    By default there will be an infinite number of backups. You can
    specify *backupCount* to limit the maximum number of backup files.

    Different to other rotating file handlers, you can set backupCount
    to -1 to require indefinite number of backup files.

    Rollover occurs whenever a point in time specified by *when* is
    reached. See the list of possible values below.  Note that they
    are not case sensitive.

    +----------------+-----------------------+
    | Value          | Type of interval      |
    +================+=======================+
    | ``'S'``        | Seconds               |
    +----------------+-----------------------+
    | ``'MIN'``      | Minutes               |
    +----------------+-----------------------+
    | ``'H'``        | Hours                 |
    +----------------+-----------------------+
    | ``'D'``        | Days                  |
    +----------------+-----------------------+
    | ``'W'``        | Week day (0=Monday)   |
    +----------------+-----------------------+
    | ``'MON'``      | Months                |
    +----------------+-----------------------+
    | ``'Y'``        | Years                 |
    +----------------+-----------------------+

    A *when* value of 'H' will rotate the logs on every full hour
    (localtime), while 'W0' will rotate on every Monday at 0:00 h.

    Different to :class:`logging.handlers.TimedRotatingFileHandler`
    the rotation will happen at beginning of a new interval. If the
    interval is measured in hours, we rollover at beginning of each
    hour, if it is months, then we rollover at 0:00 h of first day of
    a new month after logging started.

    If *backupCount* is nonzero, at most *backupCount* files will be
    kept, and if more would be created when rollover occurs, the
    oldest one is deleted. If *backupCount* is -1, an indefinite
    number of backup files will be kept.

    If *delay* is true, then file opening is deferred until the first
    call to :meth:`emit`.

    The *interval* parameter is currently ignored. It might be used
    for more Cron-like finetuning in future versions.
    """
    def __init__(self, filename, when='h', interval=1, backupCount=-1,
                 encoding=None, delay=False):
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)
        self.when = when.upper()
        self.backupCount = backupCount
        if self.when == 'S':
            self.next_func = lambda x: x+1
        elif self.when == 'MIN':
            self.next_func = next_minute
        elif self.when == 'H':
            self.next_func = next_hour
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.next_func = next_day
        elif self.when.startswith('W'):
            if len(self.when) != 2:
                raise ValueError(
                    "You must specify a day for weekly rollover from "
                    "0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError(
                    "Invalid day specified for weekly "
                    "rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.next_func = lambda x: next_week(x, self.dayOfWeek)
        elif self.when == 'MON':
            self.next_func = next_month
        elif self.when == 'Y':
            self.next_func = next_year
        else:
            raise ValueError(
                "Invalid rollover interval specified: %s" % self.when)
        self.interval = interval
        t = int(time.time())
        if os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        self.rolloverAt = self.computeRollover(t)

    def computeRollover(self, currentTime):
        """
        Work out the rollover time based on the specified time.
        """
        result = self.next_func(currentTime)
        return result

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        *record* is not used, as we are just comparing times, but it
        is needed so the method signatures are the same
        """
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def doRollover(self):
        """Do a rollover.

        If *backupCount* is <> 0, the system will successively create
        new files with the same pathname as the base file, but with
        extensions '.1', '.2' etc. appended to it. For example, with a
        backupCount of 5 and a base file name of 'app.log', you would
        get 'app.log', 'app.log.1', 'app.log.2', ... through to
        'app.log.5'. The file being written to is always 'app.log' -
        when it gets filled up, it is closed and renamed to
        'app.log.1', and if files 'app.log.1', 'app.log.2' etc.
        exist, then they are renamed to 'app.log.2', 'app.log.3' etc.
        respectively.
        """
        currentTime = time.time()

        if self.stream:
            self.stream.close()
        if self.backupCount <> 0:
            # rename existing backups
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)
        self.mode = 'w'
        self.stream = self._open()

        self.rolloverAt = self.computeRollover(currentTime)
        return
