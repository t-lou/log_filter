import json
from pathlib import Path
import re
import shutil
import sys


# global variables, try to refactor
GLOBALS = {}


class Filter:
    def __init__(self, settings: dict) -> None:
        self._settings = settings

    @staticmethod
    def _match_setting(setting: dict, line: str) -> bool:
        if setting["reg"]:
            # Regex match
            return bool(re.search(setting["keyword"], line))
        else:
            # Simple substring match
            return setting["keyword"] in line

    def match(self, line) -> bool:
        return any(Filter._match_setting(setting, line) for setting in self._settings)


def is_headless() -> bool:
    try:
        import tkinter as tk
    except ImportError:
        print("Tkinter is not available in this Python installation.")
        return True

    try:
        # Try to create and immediately destroy a root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.update_idletasks()
        root.destroy()
        print("Tkinter can be imported and a window can be launched.")
    except tk.TclError as e:
        print(
            "Tkinter is available but cannot open a window (likely headless environment)."
        )
        return True

    return False


# Load filters from JSON
def load_filters() -> dict:
    json_path = Path("config.json")
    if not json_path.exists():
        shutil.copy(Path("example_config.json"), json_path)
    with json_path.open("r", encoding="utf-8") as fc:
        main_config = json.load(fc)

        with Path(main_config["entry_config"]).open("r", encoding="utf-8") as ff:
            settings = json.load(ff)

    filters = {s["name"]: Filter(s["filters"]) for s in settings}
    assert len(filters) == len(settings), "Names must be unique."
    return filters


def load_file():
    import tkinter as tk
    from tkinter import filedialog

    filepath = filedialog.askopenfilename(
        title="Select a text file",
        filetypes=[
            ("Text files", "*.txt"),
            ("Log files", "*.log"),
            ("All files", "*.*"),
        ],
    )
    path = Path(filepath)
    if not filepath or not path.exists():
        return

    # Clear existing text boxes
    for text_widget in GLOBALS["text_widgets"].values():
        text_widget.delete("1.0", tk.END)

    # Stream through the file line by line
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue

            # Always show in "Original"
            GLOBALS["text_widgets"]["Original"].insert(tk.END, stripped + "\n")

            # Apply filters
            for tab_name, tab_filters in GLOBALS["filters"].items():
                if tab_filters.match(stripped):
                    GLOBALS["text_widgets"][tab_name].insert(tk.END, stripped + "\n")


def main_gui() -> None:
    import tkinter as tk
    from tkinter import ttk, scrolledtext

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("LOG VIEWER")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Predefined "Original" tab
    GLOBALS["text_widgets"] = {}
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Original")
    text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
    text_area.pack(fill="both", expand=True)
    GLOBALS["text_widgets"]["Original"] = text_area

    # Create tabs dynamically from filters
    for flt in GLOBALS["filters"].keys():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=flt)
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        text_area.pack(fill="both", expand=True)
        GLOBALS["text_widgets"][flt] = text_area

    # Menu for loading file
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open File", command=load_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)

    root.mainloop()


def parse_cli_args():
    import argparse

    parser = argparse.ArgumentParser(
        description="Process an input file and optionally specify an output directory."
    )

    # Mandatory positional argument
    parser.add_argument(
        "input_file", type=Path, help="Path to the input file (mandatory)"
    )

    # Optional positional argument with default
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=Path("./output"),
        type=Path,
        help="Output directory (optional, default: ./output)",
    )

    return parser.parse_args()


def main_cli() -> None:
    args = parse_cli_args()

    print("Input file:", args.input_file, type(args.input_file))
    print("Output dir:", args.output_dir, type(args.output_dir))

    # Check input
    assert args.input_file.exists(), f"Input file {args.input_file} doesn't exist."

    # Clear output
    if args.output_dir.exists():
        assert args.output_dir.is_dir(), (
            f"Existing output path {args.output_dir} is a file."
        )
        shutil.rmtree(args.output_dir)

    args.output_dir.mkdir()

    # Stream through the file line by line
    outputs = []
    ordered_filters = []
    for name, filters in GLOBALS["filters"].items():
        f = (args.output_dir / (name + ".txt")).open("w", encoding="utf-8")
        outputs.append(f)
        ordered_filters.append(filters)

    try:
        # Stream input line by line
        with args.input_file.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue

                for filters, outfile in zip(ordered_filters, outputs):
                    if filters.match(stripped):
                        outfile.write(stripped + "\n")
    finally:
        # Close all outputs
        for f in outputs:
            f.close()


if __name__ == "__main__":
    # Load filters from JSON file as use as global variable
    GLOBALS["filters"] = load_filters()

    if is_headless():
        main_cli()
    else:
        main_gui()
