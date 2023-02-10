"""
This file is responsible for setting up and configuring the logging system for the program.
The logging system is used to log messages during the program's execution, including errors and important events.
The messages are logged to both the console and a log file.
"""

from rich.console import Console
import logging
from rich.logging import RichHandler
import time
import os

# Initialize the console for logging
console = Console()

# Set the format for the log messages
FORMAT = "%(message)s"

# Create the logs directory if it doesn't exist
os.makedirs("data/logs", exist_ok=True)

# Configure the logging system
logging.basicConfig(
    level="NOTSET",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True),
        logging.FileHandler(f"data/logs/{int(time.time())}"),
    ],
)
