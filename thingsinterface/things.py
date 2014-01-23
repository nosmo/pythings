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
            "id": project_object.id(),
            "todos": [ ToDo(i) for i in project_object.toDos() ],
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

class ToDo(object):
    def __init__(self, todo_object):
        self.todo_object = todo_object
        self.__dict__ = {
            "name": todo_object.name(),
            "notes": todo_object.notes(),
            "creation_date": todo_object.creationDate(),
            "modification_date": todo_object.modificationDate(),
            "id": todo_object.id(),
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
        self.todos = [ ToDo(i) for i in self.things.toDos() ]

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
            "id": area_object.id(),
            "toDos": [ ToDo(i) for i in area_object.toDos() ],
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
    # Nothing to see here
    # http://venturefans.org/w/images/thumb/9/98/GGI.png/250px-GGI.png
    z = Areas().areas[0]
    import pprint
    pprint.pprint(dir(z))
    print z.properties()
    print z.attributeKeys()
    print z.suspended()
    print ";"
    x = Areas().things.toDos()[0]
    pprint.pprint(dir(Areas().things))
    print x.project()
    #x = ToDos().todos[0].suspended()
    #a = ThingsInterface()
    #import pprint
    #pprint.pprint(a.getToDos())
    #pprint.pprint(a.getProjects())

if __name__ == "__main__":
    main()
