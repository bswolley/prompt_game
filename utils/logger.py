import logging
import sys
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
            # Configure the root logger
            self.logger = logging.getLogger('PromptWizard')
            self.logger.setLevel(logging.DEBUG)

            try:
                # Create formatters
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
                )

                # Always use StreamHandler for safety
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)

                # Error handler to stderr
                error_handler = logging.StreamHandler(sys.stderr)
                error_handler.setLevel(logging.ERROR)
                error_handler.setFormatter(formatter)
                self.logger.addHandler(error_handler)

                Logger._initialized = True
                self.logger.info("Logger initialized successfully")

            except Exception as e:
                # Fallback to basic logging if anything fails
                logging.basicConfig(
                    stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
                )
                self.logger = logging.getLogger('PromptWizard')
                self.logger.error(f"Failed to initialize custom logger: {str(e)}")
                Logger._initialized = True

    def get_logger(self):
        return self.logger