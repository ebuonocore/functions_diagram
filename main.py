import tkinter as tki
from diagram import *
from files import *
from GUI import *

if __name__ == "__main__":
    # diag = open_file("diagrams/diag2.txt")
    window = Window()
    window.draw()
    window.tk.bind("<Button-1>", window.left_click)
    window.tk.bind("<Button-3>", window.right_click)
    window.tk.bind("<Escape>", window.right_click)
    # General keyboard controls: Select all, Copy/Paste, Undo
    window.tk.bind("<Control -s>", window.save)
    window.tk.bind("<Control -a>", window.group_all)
    window.tk.bind("<Control -c>", window.copy)
    window.tk.bind("<Control -z>", window.undo)
    window.tk.bind("<Control -y>", window.redo)
    # Detect mouse wheel with Windows
    window.tk.bind("<MouseWheel>", window.zoom_wheel)
    # Detect mouse wheel with Linux
    window.tk.bind("<Button-4>", window.zoom_wheel)
    window.tk.bind("<Button-5>", window.zoom_wheel)
    # Keyboard zoom control
    window.tk.bind("<Control -o>", window.reset_origin)
    window.tk.bind("<Control -q>", window.zoom_more)
    window.tk.bind("<Control -w>", window.zoom_less)
    # Dectecting dragging: Move the reference
    window.tk.bind("<B1-Motion>", window.drag_origin)

    window.tk.mainloop()
