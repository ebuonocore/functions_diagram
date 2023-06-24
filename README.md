<style>
img[src*='#left'] {
    float: left;
}
img[src*='#right'] {
    float: right;
}
</style>

![ex1](/assets/logo_fd_dark_bckgd.svg#right)
# Functions diagram

Functions-diagram is a Python program for graphically representing functions by specifying the input and output types.  
Elements (nodes and functions) can be linked and connected to each other.  
The graphical representation can be exported in SVG format.


## Description
### Example of simple diagram
![example_XOR_simple_encryption](/assets/example_XOR_simple_encryption.svg)  

This diagram represents of the following code:  
```{python} 
cipher_Text = xor(plain_text, key)
```
We can gess that the <code>xor</code> function takes two parameters and returns a value.
### Example of associated functions  
Another example involving a second call to the <code>xor</code> function.  
![example_XOR_decryption](/assets/example_XOR_decryption.svg)  
Here is the corresponding code:
```{python} 
cipher_Text = xor(plain_text, key)
deciphered_text = xor(cipher_Text, key)
```

The same diagram with type indications and the corresponding code.  
![example_XOR_decryption](/assets/example_XOR_decryption_type_hints.svg)  

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


### The buttons
![new](/images/new.png) Create a new file  
![open](/images/open.png) Open a file  
![save](/images/save.png) Save file. See "Backup file format" below.    
![export](/images/export.png) Export diagram to image (.SVG)  
![move](/images/move.png) Move function or node  
![add_function](/images/add_function.png) Add a function  
![add_node](/images/add_node.png) Add a free node  
![add_link](/images/add_link.png) Connect two nodes  
![edit](/images/edit.png) Edit element (node or function)  
![erase](/images/erase.png) Delete element (node, function or connexion)  
![undo](/images/undo.png) Undo  
![redo](/images/redo.png) Redo  
![auto](/images/auto.png) Place automaticly the objects on the screen  
![configuration](/images/configuration.png) Edit settings  
![information](/images/information.png) Show informations  

### Backup file format


## Author
Eric Buonocore

## Project status
The programme is now operational.
+ Adding elements (nodes, functions)
+ Interconnecting elements
+ Opening and saving diagrams
+ Moving and editing elements
+ Undo/Redo
+ Automatic positioning of elements
+ Settings and help

## Roadmap
+ Enable zooming and shifting of the whole layout 
+ Set the spacing of elements during automatic placement
+ Allow the names of free noueds to be justified

## License

![licence-by-nc-sa](/images/licence-by-nc-sa.png)