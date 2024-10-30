import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Logger._initialized:
            # Create logs directory if it doesn't exist
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            # Configure the root logger
            self.logger = logging.getLogger('PromptWizards')
            self.logger.setLevel(logging.DEBUG)

            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            )
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )

            # File handler for all logs
            log_file = os.path.join(logs_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)

            # Error file handler
            error_file = os.path.join(logs_dir, f'error_{datetime.now().strftime("%Y%m%d")}.log')
            error_file_handler = RotatingFileHandler(
                error_file,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(file_formatter)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)

            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(error_file_handler)
            self.logger.addHandler(console_handler)

            Logger._initialized = True

    def get_logger(self):
        return self.logger