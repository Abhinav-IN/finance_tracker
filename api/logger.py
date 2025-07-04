import logging

class ColoredFormatter(logging.Formatter):
    # ANSI escape codes for colors
    COLOR_CODES = {
        'DEBUG': '\033[90m',    # Grey
        'INFO': '\033[96m',     # Cyan
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m'      # Reset to default color
    }

    def format(self, record):
        levelname = record.levelname
        color_code = self.COLOR_CODES.get(levelname, self.COLOR_CODES['RESET'])
        record.levelname = f"{color_code}{levelname}{self.COLOR_CODES['RESET']}"
        return super().format(record)

def create_info_logger(name="my_info_logger"):
  """
  Args:
    name (str): The name of the logger. Defaults to "my_info_logger".
  """
  if logging.getLogger(name).handlers:
    return logging.getLogger(name)

  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)

  handler = logging.StreamHandler()

  # Use our custom ColoredFormatter instead of the standard one
  formatter = ColoredFormatter('[%(name)s] [%(levelname)s] - [%(asctime)s] - %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return logger