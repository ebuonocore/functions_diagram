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
    # window.tk.bind("<Control-a>", window.copy_all)
    window.tk.mainloop()
