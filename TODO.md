# DONE:
Détection de boucle dans le diagram : Mise en place de Design.status
    Ok lors de la création de lien et la mise à jour des positions
    Permet de conditionner les appels récursif et de laisser une trace de l'erreur
Résolution du Warning dans Diagram.disconnect_nodes()

# TODO:
**Options :**  
+ Espace par étage (si rien, auto) → centrer le diagramme (offset)  

**ReadME :**
+ Edition des paramètres

**GUI.py :** 
+ texte alignement : Proposer de justifier le nom des noeuds libres
+ dessiner des rectangles en pointillés 
+ Mettre en place .scale sur self.can ?   
+ Un drag pour déplacer l'ensemble du diagram ? avec scrollregion ?  
+ Constante pour le taux de rafraichissement du after()
+ Lever des exceptions plus propres dans les try (au lieu de pass)

**OS :**
+ Vérifier si accès aux chemins correct sur Windows  

Alternative/Existant : https://app.diagrams.net/
