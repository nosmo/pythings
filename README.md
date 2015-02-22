pythings
========

Python interface (via AppleScript) to Cultured Code's excellent Things app.

Implementation
-------------
pythings uses the PyObjC Python/Objective-C bridge for communication with Things.

Use
-------------

At the moment the library is seriously dumb.

Objects that currently work:
Lists of all $objects that contains all $objects in the $objects attribute (these are resource intensive - see below)
* Projects
* Areas
* ToDos

Simple objects that contain a dictionary of the expected attributes for the object
* Project
* Area
* ToDo

As of yet only ToDos support modification, like so:
```
>>> import thingsinterface
>>> thingsinterface.ToDo
<class 'thingsinterface.things.ToDo'>
>>> a = thingsinterface.ToDo("Testing pythings", tags=["useless"], location="Today")
```
And a suitably named todo will appear in Today.

Stuff that doesn't work yet:
* Contacts
* Lists (largely will be used for internal status setting/project use)

Known issues
-------------
Using the ScriptingBridge object will create a Python process that's visible in the dock. This is somewhat unavoidable.

The use of the ScriptingBridge object means that you must use a version of Python with this functionality built in. When in doubt, use /usr/bin/python. The version I have installed from prefix Portage does not have this support included.

The Applescript interface is slow like Philip Glass on DXM. Querying all ToDos or all Projects will take minutes for mature Things profiles. Querying all projects with their constituent todos takes 7 minutes on my computer, because this will query all historical information. This is a prime candidate for storing objects in some other format keyed by id.

The Applescript interface is also a massive hog while it's being slow - CPU use will stick at 100% for a while while stuff is being queried.
