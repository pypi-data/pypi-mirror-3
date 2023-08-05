Console Utils project

Python module: alex_console
submodule: Menu and Selectors.


Usage of Menu

You can specify a title and a text to show.
The "Exit" choice is automatically added. To remove it use the parameter "show_exit" setted to False.
If a choice is required program continue to show a prompt.
If user don't make a choice or select "Exit", the "Exit" command key is returned.
Given voices must be a dictionary with all keys of string type.
Keys are case-insensitive, so user can use lower or upper case (in case key is a letter).
The selected key is returned in the same case as it is given in voices dictionary.


Example 1: show a menu with three possible choice

from consolemenu import menu

main_menu = menu.Menu()
main_menu.add('A', 'Chose A')
main_menu.add('B', 'Chose B')
main_menu.add('C', 'Chose C')

main_menu.show(title)

output:
A -> Chose A
B -> Chose B
C -> Chose C
Esc -> Exit
Your selection: _



Example 2: 


[todo]


