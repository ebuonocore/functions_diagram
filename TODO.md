# DONE:
**Groups**
+ Dessin des groupes
+ Interface d'édition des groupes (liste des éléments)
+ Thickness: Ajuster le paramétrage du dash dans le dessin des pointillés en fonction de thickness
+ Test de validité de thickness et color Ok
+ Auto/Fixed : Griser position ET dimension si Auto.
+ Nouveau calcul de la hauteur de fenêtre en fonction de self.frame.bbox()

# TODO:
**GUI.py :** 
+ Ajouter un attribut "Marge" aux groupes et "group marge" aux prefs
+ Auto : Donner les dimensions minimales pour englober les objets du groupe + marges
+ Move, Edit et Erase /Group (prévoir la sélection coin sup gauche et inf droits)
+ Sauvegarde et lecture des groupes

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
