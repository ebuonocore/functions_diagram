# DONE:
ReadME : Traduction d'une phrase en fr
Vérification des mises en forme (taille des boutons)  
Versions de l'algoritme TSP naif

# TODO:
**File**
Dans function_definition(line), reprendre parameters = parameters_line.split(",")
    ! Certains types contiennent des virgules : dict[str,dict[str,float]]
    => Créer une fonction qui split seulement les virgules non comprises entre [] ou ()

**ReadME**  
+ save_diagram : Format des enregistrements
+ Auto
+ Edit
+ version fr
  
**Options** :  
+ Espace par étage (si rien, auto) → centrer le diagramme (offset)  
+ Autoriser les boucles / feedback

**GUI.py** :  
+ Mettre en place .scale sur self.can ?   
+ Un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?  
+ texte alignement : Proposer de justifier le nom des noeuds libres
+ dessiner des rectangles en pointillés
  
**OS** : 
+ Vérifier si accès aux chemins correct sur Windows  

Alternative/Existant : https://app.diagrams.net/
