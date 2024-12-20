import logging
import os
from datetime import datetime
from mpi4py import MPI
# import logging.handlers


cformatter = logging.Formatter(
    ('%(asctime)s - %(name)s.%(funcName)s - %(process)s - %(levelname)s: '
     + '%(message)s'),
    datefmt='%y-%m-%d %H:%M:%S')
HANDLERNAME_FILE = "default-file"
HANDLERNAME_CONSOLE = "default-console"
DEFAULT_HANDLERNAMES = [HANDLERNAME_CONSOLE, HANDLERNAME_FILE]
LOGDIR = "log"
LOG_TSTRFMT = '%Y-%m-%d-%H:%M:%S'
RANK_STRFMT = "{rank:03d}"  # "%03d"
FILENAME_FMT = "{classname}-r"+RANK_STRFMT+"_{exectimestr}.log"


def create_logger() -> logging.Logger:
    """
    Set logger for the package.
    """
    # Try to get the package name, may not work for python <3.9 versions
    try:
        if __package__ is None and __name__ != "__main__":
            loggername = __name__.split('.')[0]
        elif __package__ == "":
            loggername = "ll"
        else:
            loggername = __package__
    except UnboundLocalError:
        print("Error, using ", __name__.split('.')[0])
        loggername = __name__.split('.')[0]

    logger = logging.getLogger(loggername)
    return logger


def set_consoleHandler(logger, loglevel="DEBUG",
                       handlername="console"):
    """
    Add StreamHandler (stdout) using our our formatter.
    """
    ch = logging.StreamHandler()
    ch.set_name(handlername)
    ch.setLevel(loglevel)
    ch.setFormatter(cformatter)
    logger.addHandler(ch)
    logger.debug("Added console handler")


def set_fileHandler(logger, filename, loglevel="DEBUG",
                    handlername="file"):
    """
    Add FileHandler using our formatter.
    """
    fh = logging.FileHandler(filename,)
    fh.set_name(handlername)
    fh.setLevel(loglevel)
    fh.setFormatter(cformatter)
    logger.addHandler(fh)
    logger.debug("Added file handler %s" % str(fh))


def get_handlers_by_name(logger) -> dict:
    """
    Returns dictionary with handler names as keys and list of handlers as
    values.
    """
    handlers = {}
    for h in (logger.handlers):
        try:
            handlers[h.name].append(h)
        except KeyError:
            handlers[h.name] = [h]
    return handlers


def get_duplicate_handlers(logger) -> dict:
    """
    Returns dictionary with handler names as keys and list of handlers as
    values if there are more than one handler with the same name.
    """
    handlers = get_handlers_by_name(logger)
    handlers = {hn: h for hn, h in handlers.items() if len(h) > 1}
    return handlers


def remove_duplicate_handlers(logger):
    """
    Remove all but the first handler with the same name.
    """
    handlers = get_duplicate_handlers(logger)
    if len(handlers) == 0:
        logger.info("Found no duplicate loggers")
        return

    for h in handlers.values():
        for hi in h[1:]:
            logger.removeHandler(hi)


class LoggingMPIBaseClass():
    def __init__(self):
        # init MPI
        self.comm = MPI.COMM_WORLD
        self.psize = self.comm.Get_size()
        self.rank = self.comm.Get_rank()
        self.logfilename = None

    def _set_filename(self, logdir=LOGDIR, filename_fmt=FILENAME_FMT):
        """Set filename for log file."""
        if self.rank == 0:
            tstr = datetime.now().strftime(LOG_TSTRFMT)
        else:
            tstr = None
        tstr = self.comm.bcast(tstr, root=0)
        filename = filename_fmt.format(classname=self.__class__.__name__,
                                       rank=self.rank, exectimestr=tstr)
        self.logfilename = os.path.join(logdir, filename)

    def _mk_logdir(self, logdir=LOGDIR):
        if self.rank == 0:
            os.makedirs(logdir, exist_ok=True)

    @property
    def _default_handlers_set(self) -> None:
        try:
            _logger = self.logger.parent
        except AttributeError as E:
            raise E("Logger not set. Call _set_logger first.")
        if not _logger.hasHandlers():
            return False
        else:
            handlers = get_handlers_by_name(_logger)
            hns = list(handlers.keys())
            if len(hns) != len(DEFAULT_HANDLERNAMES):
                return False
            return all([dhn in hns for dhn in DEFAULT_HANDLERNAMES])

    def _set_logger(self, loglevel):
        loglvl = loglevel.upper()
        loggername = ".".join([self.__module__, "",
                               self.__class__.__name__
                               + RANK_STRFMT.format(rank=self.rank)])
        self.logger = logging.getLogger(loggername)
        self.logger.parent.setLevel(loglvl)
        logging.captureWarnings(True)

    def _set_check_default_handlers(self):
        if not self._default_handlers_set:
            loglvl = self.logger.parent.getEffectiveLevel()
            set_fileHandler(self.logger.parent, self.logfilename,
                            loglvl, HANDLERNAME_FILE)
            set_consoleHandler(self.logger.parent, loglvl,
                               HANDLERNAME_CONSOLE)
        remove_duplicate_handlers(self.logger.parent)

        self.logger.debug("ID of core {:01d} is {:d}".format(
            self.rank, id(self.comm)))
        self.logger.debug("My parent logger is %s" % self.logger.parent.name)

    def set_logger(self, loglevel="DEBUG", logdir=LOGDIR,
                   filename_fmt=FILENAME_FMT):
        self._set_logger(loglevel)
        self._set_filename(logdir, filename_fmt)
        self._mk_logdir(logdir)
        self._set_check_default_handlers()
        self.logger.info("Logging to file %s" % self.logfilename
                         + " and console")
