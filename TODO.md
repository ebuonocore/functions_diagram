# DONE:
+ Ajout d'un attribut  "group margin" aux prefs et "Margin" aux groupes.
+ Group/Auto : Donner les dimensions minimales pour englober les objets du groupe + margins  
    Fonctions: Ajout de la hauteur de l'entête seulement sur les fonctions
    Tient compte de la marge si modifiée  
+ Déplacement d'objets & Automatic positionning : Recalculer les position/dimensions des groupes 'Auto'
+ Sélection et déplacement des groupes (et des éléments du groupe)

# TODO:
**GUI.py :** 
+ Move, Edit et Erase /Group (prévoir la sélection coin sup gauche et inf droit)
+ Group : Bouton Delete all elements
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
