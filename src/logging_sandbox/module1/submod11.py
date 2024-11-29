from mpi4py import MPI
import logging
import os
from datetime import datetime
from .. import logfactory
from ..module2 import submod21


parentlogger = logfactory.create_logger()
module_logger = logging.getLogger(parentlogger.name+".submod11")
HANDLERNAME_FILE = "default-file"
HANDLERNAME_CONSOLE = "default-console"
DEFAULT_HANDLERNAMES = [HANDLERNAME_CONSOLE, HANDLERNAME_FILE]
LOGDIR = "log"
LOG_TSTRFMT = '%Y-%m-%d-%H:%M:%S'
RANK_STRFMT = "%03d"


class SampleClass():
    def __init__(self, loglevel, proj_dir):
        # init MPI
        self.comm = MPI.COMM_WORLD
        self.psize = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        # directories
        self.proj_dir = proj_dir
        self._set_logger(loglevel)

        self.other_class = submod21.ClassInOtherModule()

    def _make_logdir(self):
        logdir = os.path.join(self.proj_dir, LOGDIR)
        if self.rank == 0:
            os.makedirs(logdir, exist_ok=True)

    def _set_logger(self, loglevel):
        loglvl = loglevel.upper()
        loggername = ".".join([module_logger.name, "",
                               (self.__class__.__name__
                                + RANK_STRFMT) % self.rank])
        self.logger = logging.getLogger(loggername)
        self.logger.parent.setLevel(loglvl)
        logging.captureWarnings(True)

        logdir = os.path.join(self.proj_dir, LOGDIR)

        # Let only rank 0 make log dir and get start of log
        if self.rank == 0:
            os.makedirs(logdir, exist_ok=True)
            tstr = datetime.now().strftime(LOG_TSTRFMT)
        else:
            tstr = None
        tstr = self.comm.bcast(tstr, root=0)

        if not self._default_handlers_set:
            logfilename = os.path.join(logdir,
                                       ('correlate%srank'+RANK_STRFMT) %
                                       (tstr, self.rank))
            logfactory.set_fileHandler(self.logger.parent, logfilename,
                                       loglvl, HANDLERNAME_FILE)
            logfactory.set_consoleHandler(self.logger.parent, loglvl,
                                          HANDLERNAME_CONSOLE)
        logfactory.remove_duplicate_handlers(self.logger.parent)

        self.logger.debug("ID of core {:01d} is {:d}".format(
            self.rank, id(self.comm)))
        self.logger.debug("My parent logger is %s" % self.logger.parent.name)

    @property
    def _default_handlers_set(self) -> None:
        _logger = self.logger.parent
        if not _logger.hasHandlers():
            return False
        else:
            handlers = logfactory.get_handlers_by_name(_logger)
            hns = list(handlers.keys())
            return all([dhn in hns for dhn in DEFAULT_HANDLERNAMES])

    def do_something(self):
        self.logger.info("I am doing something")

    def do_something_different(self):
        self.logger.info("Doing somethin' different")
        function_in_submod11()

    def do_something_with_other_class(self):
        self.other_class.do_stuff()


def function_in_submod11():
    module_logger.info("Info Hello")
    module_logger.debug("Debug Hello")
