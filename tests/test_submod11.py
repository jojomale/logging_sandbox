from unittest import TestCase, main, mock
import os
import logging
from logging_sandbox import logfactory
from logging_sandbox.module1 import submod11
from datetime import datetime


class TestSampleClass_Mock(TestCase):
    projdir = "output"
    exec_time = datetime(2021, 1, 1, 0, 0, 0)
    logfilename = "logfile"
    loglevel = "CRITICAL"
    logdir = os.path.join(projdir, logfactory.LOGDIR)
    mock_logger = mock.create_autospec(logging.Logger)

    def setUp(self) -> None:
        return super().setUp()

    @mock.patch.object(submod11.SampleClass, "set_logger")
    def test_set_logger(self, mock_set_logger):
        sc = submod11.SampleClass(self.loglevel, self.projdir)
        mock_set_logger.assert_called_once_with(self.loglevel, self.logdir)

    @mock.patch.object(logfactory.LoggingMPIBaseClass, "_set_filename")
    @mock.patch.object(logfactory.LoggingMPIBaseClass, "_mk_logdir")
    @mock.patch.object(logfactory.LoggingMPIBaseClass,
             "_set_check_default_handlers")
    def test_init(self, mock_check, mock_mk, mock_fn):
        filename_fmt = logfactory.FILENAME_FMT
        sc = submod11.SampleClass(self.loglevel, self.projdir)
        mock_fn.assert_called_once_with(self.logdir, filename_fmt)
        mock_mk.assert_called_once_with(self.logdir)
        mock_check.assert_called_once()
        self.assertEqual(sc.logger.name, ".".join([
            submod11.__name__, "", sc.__class__.__name__])
            + logfactory.RANK_STRFMT.format(rank=0))

    @mock.patch.object(submod11.SampleClass, "set_logger")
    def test_do_something(self, mock_set_logger):
        sc = submod11.SampleClass(self.loglevel, self.projdir)
        sc.logger = self.mock_logger
        sc.do_something()
        sc.logger.info.assert_called_once_with("I am doing something")


if __name__ == "__main__":
    main()
