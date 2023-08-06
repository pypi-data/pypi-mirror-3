Choice, a Python dialog library
================================

choice is a quick little library for getting user input in Python in a dialog-like fashion. Here's a little example:

~~~
import choice

# Get a yes or no response (default is no)
confirm = choice.Binary('Are you sure you want to delete?', False).ask()
if confirm:
    deleteIt()

# Input an arbitrary value, check for correctness
howmany = choice.Input('How many pies?', int).ask()
print("You ordered {} pies".format(howmany))

# Choose from a set of options
entree = choice.Menu(['steak', 'potatoes', 'eggplant']).ask()
~~~

choice automatically displays the best UI available to the user: basic text console, curses, or GUI windows. (curses and GUI are in development!)

Requirements and Installation
=============================

For basic functionality, `choice` has no external dependencies, and requires only:

* Python 2.7 or 3

To install, just run:

~~~
pip install choice
~~~

Documentation
=============

API docs are coming soon. More in-depth documentation can be found on Github:

https://github.com/fyhuang/choice/wiki
