import tkinter as tki
from diagram import *
from files import *
from GUI import *
from canvasvg import saveall
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source file")
    parser.add_argument("-d", "--destination", default=None, help="Destination file")
    parser.add_argument("-m", "--margin", type=int, default=10, help="Margin in pixels")
    parser.add_argument(
        "-o",
        "--opacity",
        type=float,
        default=0.5,
        help="Opacity from 0 (transparent) to 1 (opaque)",
    )
    parser.add_argument(
        "-p",
        "--preferences",
        default="dark",
        choices=["dark", "light"],
        help="Preferences",
    )
    args = parser.parse_args()
    source_file = args.source
    if args.destination is None:
        destination_file = source_file.replace(".txt", ".svg")
    else:
        destination_file = args.destination
    margin = args.margin
    opacity = args.opacity
    preferences = args.preferences
    print(source_file, destination_file, margin, opacity, preferences)
    try:
        diag = open_file(source_file)
        window = Window(diag)
        window.draw()
        saveall(destination_file, window.can, margin=margin)
    except:
        print("Error: Invalid file")
    window.tk.quit()
    window.tk.destroy()
