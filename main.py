"""
DONE:
  Export image récupère main background color Ok. Transparence Ok.
  Export image :
    Supprimer choix Background et forcer bck selon preferences
  Sauvegarder après Auto
  window_configuration:
    Boutons Default_light & Default_dark 
    Correction de l'appel à colorchooser(). Passage du paramètre pref_key valide.
    '_' comme séparateur nom, type des pref_key 
    smooth_lines & rounded functions (up & down) avec des box
    Labels justifiés à gauche dans toutes les fenêtres.

TODO:
  Fenêtres : Vérifier les mises en forme (taille des boutons)
  Fenêtre info : Minimiser hauteur
  Options : 
    Espace par étage (si rien, auto) => centrer le diagramme (offset)

  GUI.py
    mettre en place .scale sur self.can ? 
    et un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?

Alternative/Existant : https://app.diagrams.net/
"""

from diagram import *
from files import *
from GUI import *
import tkinter as tki

if __name__ == "__main__":
    #diag = open_file("diagrams/diag2.txt")
    window = Window()
    window.draw()
    window.tk.bind('<Button-1>', window.left_click)
    window.tk.bind('<Button-3>', window.right_click)
    window.tk.bind('<Escape>', window.right_click)
    window.tk.mainloop()
