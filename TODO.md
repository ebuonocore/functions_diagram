# DONE:
File "/home/buonocore/Documents/NSI/functions_diagram/functions_diagram/GUI.py", line 660, in import_image
    resized_image = image_source.resize((25, 25), Image.ANTIALIAS)
    Image.ANTIALIAS supprimé

# TOFIX :
+ render.py passe par la création d'une fenêtre. 
+ Ne prend pas en compte les arguments lors de l'appel.
+ Prend des arguments par défaut pour l'opacité et les marges
+ Ne lance pas le placement automatique des élèments

# TOTEST :

# TODO:
Aide noeuds : Commentaires
Accepter les '(', ')' dans les noms de fonctions
  dans files.function_definition() changer first_open_parentheses par last_open_parentheses ?
Renderer : Programme .py qui génère directement le SVG en fonction du nom de fichier de sauvegarde txt
  + render.py chemin/source.txt chemin/destination.svg
  + render.py chemin/source.txt => chemin/source.svg si la destination n'est pas renseignée
  + render.py -a chemin/source.txt chemin/destination.svg : Lance le mode auto en fin de lecture de fichier.
  + récupérer les préférences
  + gérer la transformation du fichier SVG : voir window_export_image.export_SVG() à scinder en sous-fonction pour ne pas faire de redondance de code
  + rendu de tous les fichiers si source est un répertoire et non un fichier
  https://docs.python.org/fr/3/howto/argparse.html#argparse-tutorial

Alternatives/Existants : 
https://app.diagrams.net/
https://github.com/kevinpt/symbolator


