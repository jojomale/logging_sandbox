import logging
# import logging.handlers


cformatter = logging.Formatter(
    ('%(asctime)s - %(name)s.%(funcName)s - %(process)s - %(levelname)s: '
     + '%(message)s'),
    datefmt='%y-%m-%d %H:%M:%S')


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
