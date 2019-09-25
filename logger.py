"""

Brandon Dunbar
Logger
Creates a log of activity for debugging

"""

from datetime import datetime


def log(text):
    """
    Writes text to log file

    :param text:
    The text to be logged.
    """

    with open('PersistentData/log.txt', 'a') as file:
        file.write(f"{datetime.now()}: {text}\n")
