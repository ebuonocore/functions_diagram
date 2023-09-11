# DONE:
Suppression de code mort, correction d'errreus (self.margins,tools.update_dict_ratio ...) 
+ Suppression de GUI.mouse_movement() : Code mort.
+ Dessin des groupe en Ok.
+ réparation de tools.update_dict_ratio() : Ecrasement successif de self.MARGINS entrainait des décalages cumulatifs sur les positions des noeuds.
+ Plusieurs self.margins (fonction du zoom) au lieu de self.MARGINS (marges sans tenir comte du zoom)
+ Correction de plusieurs title_char_height dans GUI mal utilisés selon la nécessié de * self.zoom ou non.
+ try/except remis dans GUI.draw()
+ Suppression du code mort en début de tools.nearest_objet()
+ CTRL+y : Redo

# TOFIX : 


# TOTEST :
+ Zoom/Molette de souris sous Windows

# TODO:
+ Shortcuts dans l'aide
+ Mettre à jour l'aide. Expliquer
  + Déplacement : CRTL+v
  + Annulation : CTRL+z
  + Sélection totale : CTRL+a
  + Zoom + et Zoom - : CTRL+q et CTRL+w
  + Construction d'un groupe et utilité (déplacement, duplication, chgt groupé du positionnement, suppession)

Alternative/Existant : https://app.diagrams.net/
