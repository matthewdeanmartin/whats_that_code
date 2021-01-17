"""
File system related
"""
import os

from navio_tasks.settings import PROBLEMS_FOLDER, REPORTS_FOLDER


def initialize_folders() -> None:
    """
    Create folders that are likely to be needed
    """
    for folder in [PROBLEMS_FOLDER, REPORTS_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
