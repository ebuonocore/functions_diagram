[![flag_en](/readme/assets/flag_en.png)](/README.md)
[![flag_fr](/readme/assets/flag_fr.png)](/README_fr.md)
# Functions diagram

Functions-diagram is a Python program for graphically representing functions by specifying the input and output names and types.  
Its aim is to help learners take their first steps with functions and analyse how a programme works.  
Elements (nodes and functions) can be linked and connected to each other.   
The graphical representation can be exported in SVG format.  
 
<div style="text-align: center">
    <a href="https://github.com/ebuonocore/functions_diagram">
        <img src="readme/assets/logo_fd_dark_bckgd.svg">
    </a>
</div>


## Table of contents
* [Description](#description)
  * [Example of simple diagram](#example-of-simple-diagram)
  * [Example of associated functions](#example-of-associated-functions)
  * [A more complete example](#a-more-complete-example)
* [Backup file format](#backup-file-format)
* [Buttons](#buttons)
  * [Export diagram to image (.SVG)](readme/export_SVG.md)
  * [Add or edit elements](readme/add_edit_elements.md)  
  * [Edit settings](readme/settings.md)
  * [Keyboard shortcuts](#keyboard-shortcuts)
  * [Mouse controls](#mouse-controls)   
* [Render](#render)
* [Author](#author)
* [Project status](#project-status)
* [Roadmap](#roadmap)
* [License](#license)

## Description
### Example of simple diagram
![example_XOR_simple_encryption](/readme/assets/example_XOR_simple_encryption.svg)  

This diagram represents the call of a <code>xor</code> function:  
```{python} 
cipher_text = xor(plain_text, key)
```
We can gess that this function takes two parameters and returns a value.
### Example of associated functions  
Another example involving a second call to the <code>xor</code> function.  
![example_XOR_decryption](/readme/assets/example_XOR_decryption.svg)  
Here is the corresponding code:
```{python} 
cipher_Text = xor(plain_text, key)
deciphered_text = xor(cipher_Text, key)
```

The same diagram with type indications and the corresponding code.  
![example_XOR_decryption](/readme/assets/example_XOR_decryption_type_hints.svg)  

```{python} 
def xor(a: int, b: int) -> int:
    """
    Return the bitwise operation xor on the two positive integers a and b.

    >>> xor(8, 7)
    15

    >>> xor(7, 3)
    4
    """
    return a ^ b

cipher_Text = xor(plain_text, key)
deciphered_text = xor(cipher_Text, key)
```

The code and diagram are consistent with the signature of the <code>xor</code> function.  
```{python} 
>>> import inspect
>>> inspect.signature(xor)
<Signature (a: int, b: int) -> int>
```

### A more complete example
Here we propose a naive approach to solving the [Travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem).  
Let be a list of cities such as:
```{python} 
cities = ["Paris", "Lyon", "Marseille", ...]
```
We have to explore all possible combinations and finds the shortest possible route that visits each city exactly once and returns to the city of origin.

As a first approach, we can imagine building a two-entry table to find out the cost of a route between each city.
![two-entries_table](/readme/TSP_example/assets/TSP_two_entries_table.png)  

Each cell can be filled in by calling an API (OpenStreetMap, for example). The result is implemented by a dictionary.

```{python} 
cost = {
    "Paris": {"Paris": 0, "Lyon": 462.941, "Marseille": 772.335, ...},
    "Lyon": {"Paris": 462.941, "Lyon": 0, "Marseille": 312.659, ...},
    "Marseille": {"Paris": 772.335, "Lyon": 312.659, "Marseille": 0, ...},
    ...
}
```
From this same list of cities, we need to generate all the possible route combinations back to the city of origin. 
For example:
```{python} 
["Paris", "Lyon", "Marseille", ..., "Paris"]
...
["Paris", "Marseille", "Lyon" ..., "Paris"]
```
Now that we know the cost table and all the possible routes, all we have to do is find the route with the lowest cost.  
This is what a global schematic of the problem would look like.  

[![Top_diagram](/readme/TSP_example/assets/TSP_diagram.svg)](readme/TSP_example/assets/TSP_diagram.svg)  
The last function will be responsible for systematically calculating the cost of each route.  
After that, we'll just have to take this top-down approach a step further by specifying each of the sub-functions more precisely.  
Click here to see a [possible resolution](https://github.com/ebuonocore/TSP_naive_approach/tree/main) with the associated diagrams.  

## Backup file format
Diagrams are saved in a .DGM file.  
This is how the backup of the previous diagram looks.  

```
def create_cost_table(cities:list[str])->dict[str,dict[str,float|None]]
create_cost_table.position(257,236)
create_cost_table.dimension(258,39)

def all_routes(cities:list[str])->list[list[str]]
all_routes.position(291,320)
all_routes.dimension(190,39)

def search_minimum(cost:dict[str,dict[str,float]],permutations_routes:list[list[str]])->tuple[float|None,list[str]]
search_minimum.position(860,349)
search_minimum.dimension(380,58)

node(cost,(620,320))  # fixed
node(permutations_routes,(620,416))
node(cities:list[str],(123,235))

create_cost_table<0---cities
create_cost_table>---cost
all_routes<0---cities
all_routes>---permutations_routes
search_minimum<0---cost
search_minimum<1---permutations_routes
```
Lines beginning with <code>def</code> are used to create function blocks.  
They follow the Python function definition syntax (the final <code>':'</code> is optional).  
After each <code>def</code> line, you can specify the <code>position</code> and/or <code>dimension</code> attributes of the block.

Nodes are created from a line starting with <code>node</code>. The parameters entered define the node name and its characteristics (type hint, position).  
The comment <code># fixed</code> indicates whether this element cannot be moved by automatic placement: **'Auto'**.  

Note that the <code>'*'</code> character in the name designates a separator: the characters preceding this separator correspond to the label displayed. This makes it possible to have functions or nodes with identical labels but unique names (identifiers).

Links between nodes follow the syntax below:  
```
node_name1---node_name2
```

Function nodes are designated by : ```function_name>``` for the output, and ```function_name<id``` for inputs with <code>id</code> starting at 0.

## Buttons
![new](/images/new.png) Create a new file  
![open](/images/open.png) Open a file  
![save](/images/save.png) [Save file](#backup-file-format)     
![export](/images/export.png) [Export diagram to image (.SVG)](readme/export_SVG.md)  
![move](/images/move.png) Move function, a node or a group. Also allows to move the lower right corner of the groups in "Fixed" mode  
![add_function](/images/add_function.png) [Add a function](readme/add_edit_elements.md#function)  
![add_node](/images/add_node.png) [Add a free node](readme/add_edit_elements.md#node)    
![add_group](/images/group.png) [Create a group](readme/add_edit_elements.md#group)  
![add_link](/images/add_link.png) Connect two nodes  
![edit](/images/edit.png) [Edit element (function, node or group)](readme/add_edit_elements.md)    
![erase](/images/erase.png) Delete element (node, function, group or connection). Note: To delete all elements of a group, it must be edited.    
![undo](/images/undo.png) Undo  
![redo](/images/redo.png) Redo  
![auto](/images/auto.png) Place automaticly the objects on the screen  
![configuration](/images/configuration.png) [Edit settings](readme/settings.md)    
![information](/images/information.png) Show informations  

Some operations require you to select a destination first. You can exit this mode by right-clicking or by pressing *Enter* or *Esc*.

## Keyboard shortcuts
  + **CTRL + s**: Save
  + **CTRL + c**: Copy/paste
  + **CTRL + z** & **CTRL + y**: Undo & Redo
  + **CTRL + a**: Create a group including all diagram elements
  + **CTRL + q** & **CTRL + w**: Zoom + et Zoom -
  + **CTRL + o**: Return to original zoom and offset
## Mouse controls
  + **Wheel**: Zoom + et Zoom -
  + **Clic + Move**: Offset of the drawing

## Render
<code>render.py</code> is a rendering tool that converts .DMG files or a directory of .DMG files to .SVG.  
Example of use :  

```
python3 render.py ./diagrams -m 40 -o 0.9
```

This instruction converts all .DMG files in the <code>diagrams</code> directory with an additional margin of 40 pixels (-m option) and a transparency of 0.9 (-o option)  

Help:  

```
usage: render.py [-h] [-d DESTINATION] [-m MARGIN] [-o OPACITY] [-p {None,dark,light}] [-a AUTOMODE] source  

positional arguments:  
  source                Source file  
  
options:  
  -h, --help            show this help message and exit  
  -d DESTINATION, --destination DESTINATION  
                        Destination file  
  -m MARGIN, --margin MARGIN  
                        Margin in pixels  
  -o OPACITY, --opacity OPACITY  
                        Opacity from 0 (transparent) to 1 (opaque)  
  -p {None,dark,light}, --preferences {None,dark,light}  
                        Preferences  
  -a AUTOMODE, --automode AUTOMODE  
                        Runs automatic placement if True  
```

## Author
Eric Buonocore

## Project status
The program is operational.
- [x] Adding elements (nodes, functions)
- [x] Interconnecting elements
- [x] Opening and saving diagrams
- [x] Moving and editing elements
- [x] Undo/Redo
- [x] Automatic positioning of elements
- [x] Settings and help
- [x] Multi-select items to move or delete them  
- [x] Set the spacing of elements for automatic placement  
- [x] Allow the names of free nodes to be justified  
- [x] Enable zooming and shifting of the whole layout
- [x] A rendering tool (render.py) for converting .dmg files (or directories) into .svg files

## Roadmap
- [ ] Testing and fixing bugs

## License

![licence-by-nc-sa](/images/licence-by-nc-sa.png)
