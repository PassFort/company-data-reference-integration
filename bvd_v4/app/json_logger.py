import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

root = logging.getLogger()

"""
This stops the logging module from printing exceptions when trying to log.
"""
logging.raiseExceptions = False


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


supported_keys = [
    "asctime",
    "filename",
    "levelname",
    "lineno",
    "module",
    "message",
    "pathname",
]
formatted_keys = ["%({0:s})".format(i) for i in supported_keys]
custom_format = " ".join(formatted_keys)


root.propagate = False
json_log_handler = logging.StreamHandler()
json_log_handler.setFormatter(CustomJsonFormatter(custom_format))
root.addHandler(json_log_handler)
root.setLevel(logging.INFO)
