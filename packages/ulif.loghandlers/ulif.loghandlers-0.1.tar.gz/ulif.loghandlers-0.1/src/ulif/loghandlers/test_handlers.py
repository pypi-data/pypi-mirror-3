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
# Tests for handler module
import cStringIO
import datetime
import logging
import os
import pytest
import shutil
import tempfile
import time
import unittest
from ulif.loghandlers import DatedRotatingFileHandler
from ulif.loghandlers.handlers import (
    next_minute, next_hour, next_day, next_week, next_month, next_year
    )

def timestamp(year, month, day, hour, minute, second):
    # create a timestamp for given datetime values
    dt = datetime.datetime(year, month, day, hour, minute, second)
    return time.mktime(dt.timetuple())

def test_next_minute():
    # we can get the next minute for a timestamp.
    t1 = timestamp(2012, 4, 1, 12, 59, 59)
    t2 = timestamp(2012, 4, 1, 12, 59, 0)
    result1 = next_minute(t1)
    result2 = next_minute(t2)
    assert result1 == t1 + 1
    assert result2 == t2 + 60
    return

def test_next_hour():
    # we can get the next hour for a timestamp.
    t1 = timestamp(2012, 4, 1, 12, 59, 0)
    t2 = timestamp(2012, 4, 1, 12, 0, 0)
    result1 = next_hour(t1)
    result2 = next_hour(t2)
    assert result1 == t1 + 60
    assert result2 == t2 + 3600
    return

def test_next_hour_from_file(tmpdir):
    # make sure that timestamps from files work correctly.
    myfile = tmpdir.join('myfile')
    myfile.open(mode='w').write('hi')
    mtime = myfile.mtime()
    result1 = next_hour(mtime)
    assert result1 - mtime < 3601
    assert result1 - time.time() < 3601
    return

def test_next_day():
    # we can get the next day from a timestamp
    t1 = timestamp(2012, 4, 1, 23, 59, 0)
    t2 = timestamp(2012, 4, 1, 0, 0, 0)
    result1 = next_day(t1)
    result2 = next_day(t2)
    assert result1 == t1 + 60
    assert result2 == t2 + 24 * 3600
    assert datetime.datetime.fromtimestamp(result1) == datetime.datetime(
        2012, 4, 2, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result2) == datetime.datetime(
        2012, 4, 2, 0, 0, 0)
    return

def test_next_week():
    # we can get the start of next weekday.
    t1 = timestamp(2012, 4, 1, 23, 59, 0)
    t2 = timestamp(2012, 4, 2, 0, 0, 0)
    result1 = next_week(t1)
    result2 = next_week(t2)
    result3 = next_week(t1, 1)
    assert result1 == t1 + 60
    assert datetime.datetime.fromtimestamp(result1) == datetime.datetime(
        2012, 4, 2, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result2) == datetime.datetime(
        2012, 4, 9, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result3) == datetime.datetime(
        2012, 4, 3, 0, 0, 0)
    return

def test_next_month():
    # we can get the start of next month.
    t1 = timestamp(2012, 4, 30, 23, 59, 0)
    t2 = timestamp(2012, 4, 1, 0, 0, 0)
    t3 = timestamp(2012, 11, 1, 0, 0, 0)
    t4 = timestamp(2012, 12, 1, 0, 0, 0)
    result1 = next_month(t1)
    result2 = next_month(t2)
    result3 = next_month(t3)
    result4 = next_month(t4)
    assert result1 == t1 + 60
    assert datetime.datetime.fromtimestamp(result1) == datetime.datetime(
        2012, 5, 1, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result2) == datetime.datetime(
        2012, 5, 1, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result3) == datetime.datetime(
        2012, 12, 1, 0, 0, 0)
    assert datetime.datetime.fromtimestamp(result4) == datetime.datetime(
        2013, 1, 1, 0, 0, 0)
    return

def test_next_year():
    # we can get the start of next year.
    t1 = timestamp(2012, 12, 31, 23, 59, 0)
    result1 = next_year(t1)
    assert result1 == t1 + 60
    assert datetime.datetime.fromtimestamp(result1) == datetime.datetime(
        2013, 1, 1, 0, 0, 0)
    return

def test_init(tmpdir):
    # we can create instances
    log_path = tmpdir.join('my.log')
    inst = DatedRotatingFileHandler(str(log_path))
    log_path = str(log_path)
    assert inst is not None
    # we must provide at least a filename
    pytest.raises(TypeError, "DatedRotatingFileHandler()" )
    # unkown whens are not allowed
    pytest.raises(ValueError, DatedRotatingFileHandler,
                  log_path, when='NONSENSE')
    # weekdays are required with 'W'
    pytest.raises(ValueError, DatedRotatingFileHandler,
                  log_path, when='W')
    pytest.raises(ValueError, DatedRotatingFileHandler,
                  log_path, when='W8')
    return

def test_init_values(tmpdir):
    log_path = tmpdir.join('my.log')
    inst0 = DatedRotatingFileHandler(str(log_path), when='S')
    assert inst0.when == 'S'
    inst1 = DatedRotatingFileHandler(str(log_path))
    assert inst1.when == 'H'
    inst2 = DatedRotatingFileHandler(str(log_path), when='min')
    assert inst2.when == 'MIN'
    inst3 = DatedRotatingFileHandler(str(log_path), when='D')
    assert inst3.when == 'D'
    inst4 = DatedRotatingFileHandler(str(log_path), when='W0')
    assert inst4.when == 'W0'
    inst5 = DatedRotatingFileHandler(str(log_path), when='MON')
    assert inst5.when == 'MON'
    inst6 = DatedRotatingFileHandler(str(log_path), when='Y')
    assert inst6.when == 'Y'
    return

class DatedRotatingFileHandlerTests(unittest.TestCase):

    log_format = "%(name)s -> %(levelname)s: %(message)s"

    def setUp(self):
        logger_dict = logging.getLogger().manager.loggerDict
        logging._acquireLock()
        try:
            self.saved_handlers = logging._handlers.copy()
            self.saved_handler_list = logging._handlerList[:]
            self.saved_loggers = logger_dict.copy()
            self.saved_level_names = logging._levelNames.copy()
        finally:
            logging._releaseLock()

        self.root_logger = logging.getLogger("")
        self.original_logging_level = self.root_logger.getEffectiveLevel()

        self.stream = cStringIO.StringIO()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_hdlr = logging.StreamHandler(self.stream)
        self.root_formatter = logging.Formatter(self.log_format)
        self.root_hdlr.setFormatter(self.root_formatter)
        self.root_logger.addHandler(self.root_hdlr)

        # Create a workdir and provide a usable path for a log file
        self.workdir = tempfile.mkdtemp()
        self.log_path1 = os.path.join(self.workdir, 'test1.log')
        self.log_path2 = os.path.join(self.workdir, 'test2.log')
        return

    def tearDown(self):
        self.stream.close()
        self.root_logger.removeHandler(self.root_hdlr)
        while self.root_logger.handlers:
            h = self.root_logger.handlers[0]
            self.root_logger.removeHandler(h)
            h.close()
            pass
        self.root_logger.setLevel(self.original_logging_level)
        logging._acquireLock()
        try:
            logging._levelNames.clear()
            logging._levelNames.update(self.saved_level_names)
            logging._handlers.clear()
            logging._handlers.update(self.saved_handlers)
            logging._handlerList[:] = self.saved_handler_list
            loggerDict = logging.getLogger().manager.loggerDict
            loggerDict.clear()
            loggerDict.update(self.saved_loggers)
        finally:
            logging._releaseLock()
            pass
        shutil.rmtree(self.workdir)
        pass

    def setup_handler(self, handler):
        # get a logger with the handler set up
        #logger = logging.getLogger('ulif.loghandlers.test')
        logger = self.root_logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def test_log(self):
        # we can basically log something
        handler = DatedRotatingFileHandler(self.log_path1)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        contents = open(self.log_path1, 'rb').read()
        self.assertEqual(
            contents, 'root -> INFO: Message1\n')
        return

    def test_should_rollover(self):
        # shouldRollover() gives correct answers
        t = int(time.time())
        handler = DatedRotatingFileHandler(self.log_path1)
        handler.rolloverAt = t + 300
        self.assertEqual(handler.shouldRollover(None), 0)
        handler.rolloverAt = t - 300
        self.assertEqual(handler.shouldRollover(None), 1)
        return

    def test_do_rollover(self):
        # we can rollover. There will be indefinite backups by default
        handler = DatedRotatingFileHandler(self.log_path1)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        handler.doRollover()
        logger.info('Message2')
        contents = open(self.log_path1, 'rb').read()
        self.assertEqual(
            contents, 'root -> INFO: Message2\n')
        dircontents = sorted(os.listdir(self.workdir))
        self.assertEqual(len(dircontents), 2)
        return

    def test_do_rollover_with_backup(self):
        # we can request infinite backups after rollover.
        handler = DatedRotatingFileHandler(self.log_path1, backupCount=-1)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        handler.doRollover()
        logger.info('Message2')
        contents = open(self.log_path1, 'rb').read()
        self.assertEqual(
            contents, 'root -> INFO: Message2\n')
        dircontents = sorted(os.listdir(self.workdir))
        self.assertEqual(len(dircontents), 2)
        return

    def test_backup_count_nothing_to_delete(self):
        # backupCount is respected
        # when no backups need to be deleted
        handler = DatedRotatingFileHandler(
            self.log_path1, when='Y', backupCount=2)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        handler.doRollover()
        self.assertEqual(len(os.listdir(self.workdir)), 2)
        return

    def test_backup_count_something_to_delete(self):
        # backupCount is respected
        # when there are too many backup files
        handler = DatedRotatingFileHandler(
            self.log_path1, when='Y', backupCount=2)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        handler.doRollover()
        self.assertEqual(len(os.listdir(self.workdir)), 2)
        logger.info('Message2')
        handler.doRollover()
        self.assertEqual(len(os.listdir(self.workdir)), 3)
        logger.info('Message3')
        handler.doRollover()
        self.assertEqual(len(os.listdir(self.workdir)), 3)
        return

    def test_rollover_with_one_backup(self):
        # make sure we have at most one backup file if told so.
        # This is a special case we need for test coverage.
        handler = DatedRotatingFileHandler(
            self.log_path1, when='Y', backupCount=1)
        logger = self.setup_handler(handler)
        logger.info('Message1')
        handler.doRollover()
        logger.info('Message2')
        handler.doRollover()
        self.assertEqual(len(os.listdir(self.workdir)), 2)
        return
