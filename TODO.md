# DONE:
+ Création/Suppression/Modification de groupes
+ Suppression de pyinput
+ Mise en commentaire du bind de Ctrl+a
+ Suppression de l'offset au déplacement des groupes
+ Les sous-groupes suivent les déplacement d'un groupe supérieur
+ Redessiner le groupe lors de sélection/deselection d'éléments dans la liste d'édition
+ Sélection et édition de groupe
+ Sélection et suppression de groupe
+ Sauvegarde des groupes
+ Aucun élément (fonction , noeud, group) n'a d'homonyme.
+ Lecture/création des groupes
+ Intégration des créations/modifications de groupes dans le Undo/Redo

# TODO:
**Groups :** 
+ dans diagram add_function. Changer le test d'existence du nom par tl.all_previous_names(self)
+ Redimensionner : prévoir la sélection coin sup gauche et inf droit si Mode Fixe et non Auto
+ Group : Bouton Delete all elements

**ReadMe**
+ Feuille de route : 3 derniers points Ok!
+ Ajouter explication et icone Groupes

+ Mettre en place .scale sur self.can ?   
+ Selection multiple :
  + gérer la destination comme une liste (Un seul élément possible pour l'édition par exemple)
  + window.copy_all déclenché par le bind dans main en attente
  + Détection de l'enfoncement dans Shift pour déclencher la multisélection pour les déplacements ou suppression
+ Détection de la touche Ctrl pour déplacer le point de reférence de l'ensemble du diagram : avec scrollregion ?  
+ Lever des exceptions plus propres dans les try (au lieu de pass)

**OS :**
+ Vérifier si accès aux chemins correct sur Windows  

Alternative/Existant : https://app.diagrams.net/
