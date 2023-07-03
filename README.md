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
* [Buttons](#buttons)
  * [Save file](readme/save_diagram.md)     
  * [Export diagram to image (.SVG)](readme/export_SVG.md)
  * [Add or edit elements](readme/add_edit_elements.md)  
* [Backup file format](#backup-file-format)
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

As a first approach, we can imagine building a two-entry table to find out the cost of a journey between each city.
![two-entries_table](/readme/TSP_example/assets/TSP_two_entries_table.png)  

Each cell can be filled in by calling an API (OpenStreetMap, for example). The result is implemented by a dictionary.

```{python} 
cost = {
    Paris: {"Paris": 0, "Lyon": 462.941, "Marseille": 772.335, ...},
    Lyon: {"Paris": 462.941, "Lyon": 0, "Marseille": 312.659, ...},
    Marseille: {"Paris": 772.335, "Lyon": 312.659, "Marseille": 0, ...},
    ...
}
```
From this same list of cities, we need to generate all the possible route combinations.  
For example:
```{python} 
["Paris", "Lyon", "Marseille", ..., "Paris"]
["Paris", "Marseille", "Lyon" ..., "Paris"]
```
Now that we know the cost table and all the possible routes, all we have to do is find the route with the lowest cost.  
This is what a global schematic of the problem would look like.  

[![Top_diagram](/readme/TSP_example/assets/TSP_diagram.svg)](readme/TSP_example/assets/TSP_diagram.svg)  
The last function will be responsible for systematically calculating the cost of each journey.  
After that, we'll just have to take this top-down approach a step further by specifying each of the sub-functions more precisely.  
Click here to see a [possible resolution](/readme/TSP_example/) and the [associated diagrams](/readme/TSP_example/assets/).  

## Buttons
![new](/images/new.png) Create a new file  
![open](/images/open.png) Open a file  
![save](/images/save.png) [Save file](readme/save_diagram.md)     
![export](/images/export.png) [Export diagram to image (.SVG)](readme/export_SVG.md)  
![move](/images/move.png) Move function or node  
![add_function](/images/add_function.png) [Add a function](readme/add_edit_elements.md#function)  
![add_node](/images/add_node.png) [Add a free node](readme/add_edit_elements.md#node)    
![add_link](/images/add_link.png) Connect two nodes  
![edit](/images/edit.png) [Edit element (node or function)](readme/add_edit_elements.md)    
![erase](/images/erase.png) Delete element (node, function or connexion)  
![undo](/images/undo.png) Undo  
![redo](/images/redo.png) Redo  
![auto](/images/auto.png) Place automaticly the objects on the screen  
![configuration](/images/configuration.png) Edit settings  
![information](/images/information.png) Show informations  

Some operations require you to select a destination first. You can exit this mode by right-clicking or by pressing Enter or Esc.

## Author
Eric Buonocore

## Project status
The programme is operational.
- [x] Adding elements (nodes, functions)
- [x] Interconnecting elements
- [x] Opening and saving diagrams
- [x] Moving and editing elements
- [x] Undo/Redo
- [x] Automatic positioning of elements
- [x] Settings and help

## Roadmap
- [ ] Enable zooming and shifting of the whole layout  
- [ ] Multi-select items to move or delete them  
- [ ] Set the spacing of elements for automatic placement  
- [ ] Allow the names of free nodes to be justified  

## License

![licence-by-nc-sa](/images/licence-by-nc-sa.png)
