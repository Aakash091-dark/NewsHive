import logging
import os
import boto3
from datetime import datetime
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_LOGS_REGION = os.getenv("AWS_LOGS_REGION")
LOG_GROUP_NAME = 'newshive-logs'
SERVICE_NAME = "newshive"
COMPANY_NAME = "Orbitaim"

# --- CloudWatch Handler ---
class CloudWatchHandler(logging.Handler):
    def __init__(self, log_group_name):
        super().__init__()
        self.log_group_name = log_group_name
        self.log_stream_name = f"app-log-stream-{datetime.now().strftime('%Y-%m-%d')}"
        
        self.client = boto3.client(
            'logs',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_LOGS_REGION
        )
        self._ensure_log_group_and_stream_exist()

    def _ensure_log_group_and_stream_exist(self):
        try:
            self.client.create_log_group(logGroupName=self.log_group_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def emit(self, record):
        log_entry = self.format(record)
        timestamp_ms = int(record.created * 1000)
        
        try:
            self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[
                    {
                        'timestamp': timestamp_ms,
                        'message': log_entry
                    }
                ]
            )
        except Exception as e:
            pass

# --- Filter for log levels ---
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO

# --- Logger Setup ---
def setup_logger():
    logger = logging.getLogger(SERVICE_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # prevent duplicate logs in parent loggers

    # --- JSON Formatter ---
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "service"
        }
    )

    # --- CloudWatch Handler (if AWS configured) ---
    if AWS_ACCESS_KEY and AWS_SECRET_KEY and AWS_LOGS_REGION:
        cloudwatch_handler = CloudWatchHandler(log_group_name=LOG_GROUP_NAME)
        cloudwatch_handler.setFormatter(formatter)
        cloudwatch_handler.addFilter(InfoFilter())
        logger.addHandler(cloudwatch_handler)
    else:
        logger.warning("CloudWatch credentials not found. Logging to console only.")

    # --- Console Handler (always) ---
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(InfoFilter())
    logger.addHandler(console_handler)

    # --- Add static fields ---
    logger = logging.LoggerAdapter(logger, {"company": COMPANY_NAME})
    
    return logger


# --- Instantiate Logger ---
log = setup_logger()
