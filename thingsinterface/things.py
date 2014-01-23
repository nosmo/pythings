#!/usr/bin/python

import ScriptingBridge
from collections import namedtuple

#TODO
class Project(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __str__(self):
        return str(self.__dict__)

#TODO
class Todo(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

class ThingsInterface(object):

    def __init__(self):
        self.things = ScriptingBridge.SBApplication.applicationWithBundleIdentifier_("com.culturedcode.things")

    def getTodo(self, todo):
        return {
            "name": todo.name(),
            "notes": todo.notes(),
            "creation_date": todo.creationDate(),
            "modification_date": todo.modificationDate(),
            "id": todo.id(),
            "tags": todo.tagNames().split(", "),
            "area": todo.area().name(),
            "completion_date": todo.completionDate(),
            "completed": True if todo.completionDate() else False,
            "contact": todo.contact().name()
        }


    def getToDos(self):
        todolist = []
        for todo in self.things.toDos():
            todo_details = self.getTodo(todo)
            todolist.append(todo_details)
        return todolist

    def getProjects(self):
        projectlist = []
        for project in self.things.projects():
            project_details = {
                "name": project.name(),
                "notes": project.notes(),
                "creation_date": project.creationDate(),
                "modification_date": project.modificationDate(),
                "id": project.id(),
                #TODO make this a native todo object
                "todos": [ self.getTodo(i) for i in project.toDos() ],
                #"todos": len(project.toDos()),
                "tags": project.tagNames().split(", "),
                "area": project.area().name(),
                "completion_date": project.completionDate(),
                "completed": True if project.completionDate() else False,
                "contact": project.contact().name()
            }
            #projectlist.append(Project(**project_details))
            projectlist.append(project_details)
        return projectlist

def main():
    a = ThingsInterface()
    import pprint
    #pprint.pprint(a.getToDos())
    pprint.pprint(a.getProjects())

if __name__ == "__main__":
    main()
