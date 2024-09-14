import logging
import os

class LoggerManager:
    def __init__(self, name, appendlog=True, level=logging.INFO):
        self.name = name
        self.level = level
        self.appendlog = appendlog
        self.logger = self._create_logger()

    def _create_logger(self):
        os.makedirs(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'featuredata', 'logs'), exist_ok=True)
        
        file_mode = 'a' if self.appendlog else 'w'
        
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'featuredata', 'logs', f'{self.name}.log'), mode=file_mode ,encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if logger.hasHandlers():
            logger.handlers.clear()
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

    def get_logger(self):
        return self.logger

# LOGGER_MANAGER = LoggerManager(name="__main__", appendlog=False, level=logging.INFO)
# LOGGER = LOGGER_MANAGER.get_logger()
# LOGGER.info("Hello World")