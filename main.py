#!/usr/bin/env python3


from src.cli import main_cli
from src.gui import main_gui
from src.utils import is_headless, load_filters


if __name__ == "__main__":
    # Load filters from JSON file as use as global variable
    filters = load_filters()

    if is_headless():
        main_cli(filters)
    else:
        main_gui(filters)
