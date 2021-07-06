"""
This module creates a Markdown file for the environemnt variables of the config
"""
import os
from iniparser import Config

FILE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_config_markdown():
    """Creates the config script"""
    config = Config(mode="all_allowed").scan(FILE_DIR, True).read()
    config.to_env("./env_ml_wrapper.md")


if __name__ == "__main__":
    create_config_markdown()
