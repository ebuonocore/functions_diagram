# DONE:
+ Modification du taux de rafraichissement du after(): de 10 à 100ms
+ texte alignement : Justification des noms des noeuds libres ('left, 'center','separator', 'right')
  + Lecture du diagramme (fait), attribut du noeud(Ok), interface sur édition et écriture dans le fichier, offset dans le diagramme avec priorité à l'attribut du noeud courant sinon, valeur par défaut dans les paramètres.

# TODO:
**GUI.py :** 
+ dessiner des rectangles en pointillés : rectangle(x1, y1, x2, y2, title=title, annotation=annotation)
+ Mettre en place .scale sur self.can ?   
+ Selection multiple :
  + gérer la destination comme une liste (Un seul élément possible pour l'édition par exemple)
  + window.copy_all déclenché par le bind dans main en attente
  + Détection de l'enfoncement dans Shift pour déclencher la multisélection pour les déplacements ou suppression
+ Détection de la touche Ctrl pour déplacer le point de reférence de l'ensemble du diagram : avec scrollregion ?  
+ Lever des exceptions plus propres dans les try (au lieu de pass)

!? Faut il virer pyinput ? Le bind dans le main fonctionne très bien ...

**OS :**
+ Vérifier si accès aux chemins correct sur Windows  

Alternative/Existant : https://app.diagrams.net/
