import logging
from abc import ABC, abstractmethod

class Logging(ABC):
  def __init__(self):
    self.logger = logging.getLogger(self.__class__.__name__)
    self.logger.setLevel(logging.DEBUG)
    self.logger.propagate = False

    if not self.logger.handlers:
      handler = logging.FileHandler(f'src/logger_{self.__class__.__name__}.log', encoding='utf-8')
      handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
      ))
      self.logger.addHandler(handler)

  @abstractmethod
  def logging_debug(self, message) -> logging.Logger:
    pass

  @abstractmethod
  def logging_warning(self, message) -> logging.Logger:
    pass

  @abstractmethod
  def logging_info(self, message) -> logging.Logger:
    pass

  @abstractmethod
  def logging_error(self, message) -> logging.Logger:
    pass