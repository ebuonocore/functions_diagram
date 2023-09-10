# DONE:
+ Zoom : self.can.scale() abandonné dans GUI.draw() à cause des textes qui ne suivent pas
+ Zoom : Problème de décalage des zones de sélection (move, erase...) réglé
-> Affectation du coef zoom dans GUI.draw_destination_outine
-> Ajout du paramètre zoom dans tl.nearest_objet()
-> Modification du déplacement de la souris
-> Fix : Hauteur des fonctions
+ Zoom : Contrôlé aussi par la molette de la souris event.delta ou event.num selon OS
 + CTRL+a : Créé un groupe regroupant tous les éléments
   -> Lancer la méthode GROUP.update_coordinates() recadrer la dimension
 + CTRL+o : Reset_origin (reset l'offset et le zoom de l'affichage)
+ Espace trop grand entre label et type des noeuds résolu
+ self.margin renommé en self.blanck pour libérer le nom de la méthode
+ refactoring des attribut GUI.MARIN* self.margins est bien affecté par le zoom
+ Taille des noeuds et des flèches correctement affectées par le zoom

# TOFIX : 
+ Espace trop grand et étrangement cumulatif entre le noeud et la position du label
+ Erreur au positionnement des bornes pour le tracé des groupes
+ Remettre le try/except dans GUI.draw()

# TOTEST :
+ Zoom/Molette de souris sous Windows

# TODO:
+ Code mort au début de nearest ?
+ Mettre à jour l'aide. Expliquer
  + Déplacement : CRTL+v
  + Annulation : CTRL+z
  + Sélection totale : CTRL+a
  + Zoom + et Zoom - : CTRL+q et CTRL+w
  + Construction d'un groupe et utilité (déplacement, duplication, chgt groupé du positionnement, suppession)
+ Lever des exceptions plus propres dans les try (au lieu de pass)

Alternative/Existant : https://app.diagrams.net/
