#!/usr/bin/env python3

from src.utils import is_headless


def run_cli():
    from src.cli import main_cli

    main_cli()


def run_gui():
    try:
        from src.gui import main_gui

        main_gui()
    except Exception as e:
        print("GUI mode failed to start. Falling back to CLI.")
        print(f"Reason: {e}")
        run_cli()


if __name__ == "__main__":
    if is_headless():
        run_cli()
    else:
        run_gui()
