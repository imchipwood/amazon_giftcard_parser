import logging


def get_logger(name: str, debug: bool = False) -> logging.Logger:
    """
    Set up loggers
    @param name: name of logger
    @type name: str
    @param debug: flag to enable debug prints
    @type debug: bool
    @return: logger to use
    @rtype: logging.Logger
    """
    debug_level = logging.DEBUG if debug else logging.INFO
    new_logger = logging.getLogger(name)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(debug_level)
    stdout_format = "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
    stdout_formatter = logging.Formatter(stdout_format)
    stream_handler.setFormatter(stdout_formatter)
    new_logger.handlers = []
    new_logger.addHandler(stream_handler)
    new_logger.propagate = False

    pdf_logger = logging.getLogger("pdfplumber")
    pdf_logger.setLevel(logging.WARN)
    pdf_logger.propagate = False

    new_logger.setLevel(debug_level)

    return new_logger
