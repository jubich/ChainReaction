#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Deals with setting up the logger of client and server processes.

Based on https://www.youtube.com/watch?v=9L77QExPmI0 from https://www.youtube.com/@mCoding
"""


from __future__ import annotations
import os
import datetime as dt
import json
import logging
import logging.config
import logging.handlers
import traceback


CONFIG = {
  "version": 1,
  "disable_existing_loggers": True,
  "formatters": {
    "simple": {
      "format": "%(levelname)s: %(message)s",
      "datefmt": "%Y-%m-%dT%H:%M:%S%z"
    },
    "json": {
      "()": "chainreaction.loggingsetup.MyJSONFormatter",
      "fmt_keys": {
        "level": "levelname",
        "message": "message",
        "timestamp": "timestamp",
        "logger": "name",
        "module": "module",
        "function": "funcName",
        "line": "lineno",
        "thread_name": "threadName"
      }
    }
  },
  "handlers": {
    "stderr": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "simple",
      "stream": "ext://sys.stderr"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "json",
      "filename": "logs/default.log.jsonl",
      "maxBytes": 10_000_000,
      "encoding": "utf-8",
      "backupCount": 3
    }
  },
  "loggers": {},
  "root": {
    "level": "DEBUG",
    "handlers": [
      "stderr",
      "file"
    ]
  }
}

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    """JSON Formatter used for the logger."""
    def __init__(self, *, fmt_keys: dict[str, str] | None = None,):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


def setup_logging(filename: str) -> logging.Logger:
    """Creats a logger with output log files called "filename" in file "./logs/".

    Args:
        filename: Name of the log files.

    Returns:
        A configured logger.
    """
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    CONFIG["handlers"]["file"]["filename"] = os.path.join("logs", filename)
    logging.config.dictConfig(CONFIG)
    logger = logging.getLogger("chainreaction_main_logger")
    logger.disabled = False
    return logger


def formatted_traceback(err: Exception) -> str:
    """Returns a "improved" traceback containing the local variables of the last two functions.

    Args:
        err: Raised exception containing the traceback information.

    Returns:
        Returns a "improved" traceback containing the local variables of the last two functions.
    """
    frame = err.__traceback__
    formatted_tb_l = traceback.format_tb(frame)
    frame = frame.tb_next
    tb_list = []
    len_tb_l = len(formatted_tb_l)
    for num, formatted_tb in enumerate(formatted_tb_l):
        tb_list.append(formatted_tb)
        if (len_tb_l-num <= 3) and (len_tb_l-num > 1):
            tb_list.append(f"Locals in {frame.tb_frame.f_code.co_name}(): {frame.tb_frame.f_locals}\n")
        if frame is not None:
            frame = frame.tb_next
    tb_list.append(f"{err.__class__.__name__}: {err.args}")
    return "".join(tb_list)
