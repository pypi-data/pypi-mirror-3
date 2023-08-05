import logging
from logging.handlers import RotatingFileHandler

LOG_NAME = 'secure-smtp'

class Log(object):
    
    def __init__(self, log_name):
        self.log_name = log_name
        self.logger = logging.getLogger( self.log_name )
        self._remove_handlers()
        self._create_file_handler()
        self.logger.setLevel(logging.DEBUG)
    
    def _remove_handlers(self):
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
    
    def _create_file_handler(self):
        handler = RotatingFileHandler(
            '/var/log/%s.log' % self.log_name,
            maxBytes=10485760,
            backupCount=3
        )
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

Log(LOG_NAME)