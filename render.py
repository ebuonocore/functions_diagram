import tkinter as tki
from diagram import *
from files import *
from render_GUI import *
from canvasvg import saveall
import argparse
import window_export_image as wei
import os

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
        default=None,
        choices=[None, "dark", "light"],
        help="Preferences",
    )
    parser.add_argument(
        "-a",
        "--automode",
        type=bool,
        help="Runs automatic placement if True",
    )
    args = parser.parse_args()
    automode = args.automode
    source_file = args.source
    destination = args.destination
    if not os.path.exists(source_file):
        exception_txt = (
            source_file + " doesn't exist." + " source_file must be a file or directory"
        )
        raise Exception(exception_txt)
    margin = args.margin
    opacity = args.opacity
    preferences = args.preferences
    if os.path.isfile(source_file):
        destination_file = destination
        sources = [source_file]
    elif os.path.isdir(source_file):
        destination = None
        sources = [
            source_file + "/" + file
            for file in os.listdir(source_file)
            if os.path.isfile(source_file + "/" + file) and file[-4:] == ".dgm"
        ]
    nb_file = 0
    for source in sources:
        # try:
        if True:
            if destination is None:
                destination_file = source.replace(".dgm", ".svg")
            window = Window()
            diag = open_file(source)
            window.diagram = diag
            window.preferences = tl.load_preferences(preferences)
            background_color = window.preferences["main background color_color"]
            if automode:
                window.cmd_auto()
            window.position_functions_nodes()
            window.draw()
            saveall(destination_file, window.can)
            wei.modify_SVG(destination_file, background_color, margin, opacity)
            nb_file += 1
            window.quit()
        """
        except:
            print("Error: Invalid file")
        """
    print(nb_file, "out of ", len(sources), "files converted to .SVG")
