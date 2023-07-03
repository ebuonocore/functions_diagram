# DONE:
Certains types contiennent des virgules : dict[str,dict[str,float]]
    => création de split_unembed() qui split seulement les virgules non comprises entre [] ou ()
TSP exemple (ReadMe, résolution, diagrammes)

# TODO:
**TSP example**
Simplifier les 2 versions en calculant les permutations seulement à partir la cities. Pas besoin de faire appal à cost.

**Tools**
Plantages récurents à cause de la fct distance:
File "/home/buonocore/Documents/NSI/functions_diagram/functions_diagram/tools.py", line 162, in distance
    x2, y2 = target_position
TypeError: cannot unpack non-iterable NoneType object

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
