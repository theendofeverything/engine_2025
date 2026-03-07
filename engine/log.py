"""Helper to set up logging

Use log.debug() instead of print()
----------------------------------
    log.debug("Run %s", Path(__file__).name)


Setup to log in __main__
------------------------
Top of file:
    from lib.log import setup_logging

In __main__:
    log = setup_logging()
    log.debug("Run %s", Path(__file__).name)

Setup to log in modules (lib code)
----------------------------------
At top of lib code module:
    import logging
    log = logging.getLogger(__name__)

Do not use log in modules (lib code) by passing to a function
-------------------------------------------------------------
I used to log in lib code by passing 'log' to a function:

    Game().run(log)

Game().run() can use 'log' even though the log is defined in another file.
The file where 'Game' is defined does not need to import logging, except for type hinting.

The problem with this approach is I end up passing 'log' to every function that does logging.
This is just noise in the function signatures.

"""
import logging


def setup_logging(loglevel: str = "DEBUG") -> logging.Logger:
    """Return a logger to replace print(). See module docstring for usage."""
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            "%(filename)s:%(lineno)d %(funcName)s -- %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    return _logger
