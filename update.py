# Auto update
import os

from bin.github import download_folder_from_github
print(f"Current directory: {os.getcwd()}")
download_folder_from_github("DDadeA", "DDbot", os.getcwd())