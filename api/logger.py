# logging.py
import logging
import os

def get_logger(logger_name: str):
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Set up basic configuration for logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler("logs/application.log"),
            logging.StreamHandler()  # To output to the console as well
        ]
    )
    return logging.getLogger(logger_name) 

    # If needed, you can set up more specific loggers here
    # For example, a logger for database-related logs:
    # db_logger = logging.getLogger('db')
    # db_logger.setLevel(logging.DEBUG)
    # db_file_handler = logging.FileHandler('logs/db.log')
    # db_logger.addHandler(db_file_handler)