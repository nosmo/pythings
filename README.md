pythings
========

Python interface (via AppleScript) to Cultured Code's excellent Things app.

Implementation
-------------
Swabber uses the PyObjC Python/Objective-C bridge for communication with Things.

Use
-------------

At the moment the library is seriously dumb and avoids any kind of fancy object creation. Projects and ToDos are returned as dicts.

Objects that currently work:
Lists of all $objects that contains all $objects in the $objects attribute
* Projects
* Areas
* ToDos
Simple objects that contain a dictionary of the expected attributes for the object
* Project
* Area
* ToDo

As of yet none of these support modification.

Stuff that doesn't work yet:
* Contacts
* Lists (largely will be used for internal status setting/project use)

Known issues
-------------
Using the ScriptingBridge object will create a Python process that's visible in the dock. This is somewhat unavoidable. This will sometimes mess with the dock: command-tabbing and moving between spaces can be slowed.

The use of the ScriptingBridge object means that you must use a version of Python with this functionality built in. When in doubt, use /usr/bin/python. The version I have installed from prefix Portage does not have this support included.

The Applescript interface is slow like Philip Glass on DXM. Querying all ToDos or all Projets will take minutes for mature Things profiles. Querying all projects with their constituent todos takes 7 minutes on my computer. This is a prime candidate for storing objects in some other format keyed by id.

The Applescript interface is also a massive hog while it's being slow - CPU use will stick at 100% for a while while stuff is being queried.
