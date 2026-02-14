"""Centralized logging for OptionsAgent."""

import logging

_initialized = False


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger. Call once from each entry point."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
