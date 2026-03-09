import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
	"""Configure root logging once for the application process."""
	if logging.getLogger().handlers:
		return

	logging.basicConfig(level=level, format=LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
	"""Return a logger instance bound to a module name."""
	configure_logging()
	return logging.getLogger(name)
