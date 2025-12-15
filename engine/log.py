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

Pass 'log' to a function:

    Game().run(log)

Now that Game().run() can use 'log', even if it is defined in another file.
The file where 'Game' is defined does not need to import logging.

You can also use 'log' in lib code without explicitly passing 'log' in from
the main application. The next section details this use case.


Setup to log in lib code
------------------------
At top of lib code module:
    import logging
    log = logging.getLogger(__name__)
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
