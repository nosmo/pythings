#!/usr/bin/python

import ScriptingBridge
from collections import namedtuple

class ThingsObject(object):
    def __init__(self):
        self.things = ScriptingBridge.SBApplication.applicationWithBundleIdentifier_("com.culturedcode.things")

#TODO
class Projects(ThingsObject):
    def __init__(self, **entries):
        ThingsObject.__init__(self)
        self.projects = [ i for i in self.things.projects() ]

class Project(object):
    def __init__(self, project_object):
        ThingsObject.__init__(self)
        self.__dict__ = {
            "name": project_object.name(),
            "notes": project_object.notes(),
            "creation_date": project_object.creationDate(),
            "modification_date": project_object.modificationDate(),
            "thingsid": project_object.id(),
            "todos": [ ToDo.__init_fromSBObject(i) for i in project_object.toDos() ],
            "tags": project_object.tagNames().split(", "),
            "area": project_object.area().name(),
            "completion_date": project_object.completionDate(),
            # hack
            "completed": True if project_object.completionDate() else False,
            "contact": project_object.contact().name()
        }

    def complete(self):
        #TODO
        #move to list Logbook
        raise NotImplemented

class ToDo(ThingsObject):

    """Unique functions of a toDo object: ['show', 'tagNames',
    'setProject_', 'modificationDate', 'close', 'id', 'setArea_',
    'completionDate', 'area', 'setContact_', 'dueDate',
    'setModificationDate_', 'printWithProperties_printDialog_',
    'cancellationDate', 'status', 'tags', 'moveTo_', 'creationDate',
    'duplicateTo_withProperties_', 'setTagNames_', 'scheduleFor_',
    'name', 'edit', 'setCreationDate_', 'setCompletionDate_',
    'setCancellationDate_', 'project', 'activationDate', 'contact',
    'setStatus_', 'setName_', 'setDueDate_', 'setNotes_', 'notes',
    'delete']

    AppleScript properties of a "to do" - id, tagNames,
    cancellationDate, creationDate, dueDate, contact, modficationDate,
    project, A specific osascript ID (referenced in the bridge
    object), notes, activationDate, completionDate, status, name

    """

    def __init__(self, name, tags=[], notes="", location="Inbox", creation_area=""):
        ThingsObject.__init__(self)

        if location and creation_area:
            print ("WARNING! Inserting to a location and a creation_area at the "
                   "same time will create two ToDos")

        todo_object = self.things.classForScriptingClass_("to do").alloc()
        todo_object = todo_object.initWithProperties_({
            "name": "testing applescript",
            "tagNames": ", ".join(tags),
            "notes": notes,
        })

        self.tags = tags

        assigned = False
        for thingslist in self.things.lists():
            if thingslist.name() == location:
                thingslist.toDos().append(todo_object)
                assigned = True

        if not assigned:
            raise KeyError

        for area in self.things.areas():
            if area.name() == creation_area:
                area.toDos().append(todo_object)

        self.thingsid = todo_object.id()
        self.creation_date = todo_object.creationDate()
        self.modification_date = todo_object.modificationDate()

    def __init_fromSBObject(self, todo_object):
        self.todo_object = todo_object
        self.__dict__ = {
            "name": todo_object.name(),
            "notes": todo_object.notes(),
            "creation_date": todo_object.creationDate(),
            "modification_date": todo_object.modificationDate(),
            "thingsid": todo_object.id(),
            "tags": todo_object.tagNames().split(", "),
            "area": todo_object.area().name(),
            "completion_date": todo_object.completionDate(),
            # hack
            "completed": True if todo_object.completionDate() else False,
            "contact": todo_object.contact().name()
        }

    def cancel(self):
        #TODO (oh the irony)
        # Once how to set status has been figured out...
        # set status to canceled
        raise NotImplemented

    def complete(self):
        #TODO
        # set status to completed or move to Logbook list
        raise NotImplemented

class ToDos(ThingsObject):
    def __init__(self):
        ThingsObject.__init__(self)
        self.todos = [ ToDo.__init_fromSBObject(i) for i in self.things.toDos() ]

class Areas(ThingsObject):

    def __init__(self):
        ThingsObject.__init__(self)
        self.areas = [ Area(i) for i in self.things.areas() ]
        #x = Area(z)
        #print x.toDos

class Area(object):
    def __init__(self, area_object):
        self.__dict__ = {
            "name": area_object.name(),
            "thingsid": area_object.id(),
            "toDos": [ ToDo.__init_fromSBObject(i) for i in area_object.toDos() ],
            "tags": area_object.tagNames().split(", "),
            "suspended": True if area_object.suspended() else False
            #"projects": area_object.projects()
            }

class Contacts(ThingsObject):
    #TODO
    pass

class Contact(object):
    #TODO
    pass

def main():
    a = ToDo("Test", tags=["lol", "hax"],
             notes="definitely a test", location="Today") #, creation_area="Home")

if __name__ == "__main__":
    main()
