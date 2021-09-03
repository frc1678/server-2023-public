#!/usr/bin/env python3
# Copyright (c) 2019-2021 FRC Team 1678: Citrus Circuits
"""log() outputs information the operator should be aware of

TODO: Add stack trace to write to log file
"""
from enum import Enum
from termcolor import colored

LOG_FILE = "server.log"


class Severity(Enum):
    Info = 0
    Debug = 1
    Warning = 2
    Error = 3
    Fatal = 4
    Raw = 5


def console_log(message: str, severity: Severity):
    """Prints the log message with severity"""
    # Print only the raw message
    if severity == Severity.Raw:
        print(message)
        return

    # Add the type of log before the message
    message_type = f"{severity.name}"

    color = None
    # Change the color of the message if severity it high
    if severity == Severity.Warning:
        color = "yellow"
    elif severity == Severity.Error:
        color = "red"
    elif severity == Severity.Fatal:
        color = "red"

    if color:
        message_type = colored(message_type, color)

    message = f"{message_type}: {message}"
    print(message)

    # Quit the program if the severity is fatal
    if severity == Severity.Fatal:
        print("Exiting...")
        exit(1)


def log(message: str, severity: Severity, hide: bool = False):
    """Writes the message and severity to the log file

    output is optional but on by default"""
    if not hide:
        console_log(message, severity)

    with open(LOG_FILE, "a") as file:
        file.write(f"{severity.name}: {message}\n")
