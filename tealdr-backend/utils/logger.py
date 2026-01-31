import logging
import sys
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logger():
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        'bot.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name):
    return logging.getLogger(name)
