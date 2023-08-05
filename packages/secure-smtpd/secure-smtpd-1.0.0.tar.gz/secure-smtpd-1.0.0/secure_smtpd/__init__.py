import logging
from logging.handlers import RotatingFileHandler
from smtp_server import SMTPServer
from fake_credential_validator import FakeCredentialValidator

def _create_logger():
    log_name = '/var/log/secure_smtpd.log'
    logger = logging.getLogger( log_name )
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        log_name, 
        maxBytes=10485760,
        backupCount=3
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = _create_logger()
