'''Python interface to Things.app's Applescript interface.

Lol! :'(
'''

try:
    import ScriptingBridge
except ImportError as exc:
    raise ImportError("ScriptingBridge is unavailable. Install it with "
                      "\"pip install pyobjc-framework-ScriptingBridge\" and use "
                      "an OS X specific version of Python") from exc

import enum
import warnings


class Status(enum.IntEnum):
    """The integers Things uses internally to set the status of a task."""

    OPEN = 1952737647  # "tdio"
    CLOSED = 1952736109  # "tdcm"
    CANCELLED = 1952736108  # "tdcl"


def get_things():
    return ScriptingBridge.SBApplication.applicationWithBundleIdentifier_(
        "com.culturedcode.things")


class ThingsObject:
    def __init__(self):
        self.things = get_things()


# TODO
class Projects(ThingsObject):
    def __init__(self):
        super().__init__()
        self.projects = list(self.things.projects())


class Project(ThingsObject):
    def __init__(self, project_object):
        super().__init__()
        self.name = project_object.name()
        self.notes = project_object.notes()
        self.creation_date = project_object.creationDate()
        self.modification_date = project_object.modificationDate()
        self.thingsid = project_object.id()
        self.todos = [ToDo.from_sb_object(i) for i in project_object.toDos()]
        self.tags = project_object.tagNames().split(", ")
        self.area = project_object.area().name()
        self.completion_date = project_object.completionDate()
        # hack
        self.completed = bool(project_object.completionDate())
        self.contact = project_object.contact().name()

    def complete(self):
        # TODO
        # Implementation involves moving to List "Logbook"
        raise NotImplementedError


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

    def __init__(self, name="", tags=None, notes="",
                 location="Inbox", creation_area="", todo_obj=None):
        super().__init__()

        tags = list(tags) if tags else []

        if not todo_obj:
            self.name = name
            if location and creation_area:
                warnings.warn("Inserting to a location and a creation_area at the "
                              "same time will create two ToDos")

            self.todo_object = self.things.classForScriptingClass_("to do").alloc()
            self.todo_object = self.todo_object.initWithProperties_({
                "name": name,
                "tagNames": ", ".join(tags),
                "notes": notes,
            })

            for thingslist in self.things.lists():
                if thingslist.name() == location:
                    thingslist.toDos().append(self.todo_object)
                    break
            else:
                # In rare cases where there has been some kind of
                # weird internal OS X fuck-up, self.things.lists()
                # will be empty despite Things performing perfectly
                # fine and ToDos being accessed correctly. I have no
                # idea how to reproduce or guard against it, so
                # throwing an exception here is okay with me for now.
                available = [t.name() for t in self.things.lists()]
                raise KeyError(f"Couldn't assign Things ToDo \"{self.name}\" to a list "
                               f"(location {location}, available locations: {available}.")

            if creation_area:
                for area in self.things.areas():
                    if area.name() == creation_area:
                        area.toDos().append(self.todo_object)
                        break
                else:
                    available = [a.name() for a in self.things.areas()]
                    raise KeyError(f"Couldn't assign Things ToDo \"{self.name}\" to an area "
                                   f"(creation_area {creation_area}, "
                                   f"available areas: {available}.")
        else:
            self.name = todo_obj.name()
            self.todo_object = todo_obj

        self.tags = tags

        self.thingsid = self.todo_object.id()
        self.creation_date = self.todo_object.creationDate()
        self.modification_date = self.todo_object.modificationDate()

    @classmethod
    def from_sb_object(cls, todo_object):
        return cls(todo_object.name(), tags=todo_object.tagNames().split(", "),
                   notes=todo_object.notes(), creation_area=todo_object.area().name(),
                   todo_obj=todo_object)

    @classmethod
    def from_id(cls, desired_id):
        return cls(todo_obj=get_things().toDos().objectWithID_(desired_id))

    def cancel(self):
        self.todo_object.setStatus_(Status.CANCELLED)

    def complete(self):
        self.todo_object.setStatus_(Status.CLOSED)

    def is_closed(self):
        return self.todo_object.status() == Status.CLOSED

    def is_cancelled(self):
        return self.todo_object.status() == Status.CANCELLED

    def __eq__(self, other):
        if not isinstance(other, ToDo):
            return NotImplemented
        return self.thingsid == other.thingsid

    def __hash__(self):
        return hash(self.thingsid)


class ToDos(ThingsObject):

    def __init__(self, thingslist=None):
        super().__init__()
        selectedlist = None
        todos = []
        if thingslist:
            for templist in self.things.lists():
                if templist.name() == thingslist:
                    selectedlist = templist
                    break
            if not selectedlist:
                # get ready to wait
                selectedlist = self.things
            todos = selectedlist.toDos()
        else:
            everything = list(self.things.toDos().get() or [])
            if everything:
                # The unscoped query can hand back entries that aren't
                # ToDos, so key off the type of a known-good one rather
                # than trusting everything in the list.
                todotype = type(everything[0])
                todos = [i for i in everything if isinstance(i, todotype)]

        todolist = []
        for todo in todos:
            try:
                todolist.append(ToDo.from_sb_object(todo))
            except IndexError:
                # If Things is in use while we're working on it the
                # index length can sometimes change. Skip whatever
                # moved out from under us and plough on regardless.
                continue

        self.todos = todolist

    def __len__(self):
        """Return the number of todo objects. """
        return len(self.todos)

    def __iter__(self):
        """Iterate over the todo objects."""
        return iter(self.todos)


class Areas(ThingsObject):

    def __init__(self):
        super().__init__()
        self.areas = [Area(i) for i in self.things.areas()]


class Area:
    def __init__(self, area_object):
        self.name = area_object.name()
        self.thingsid = area_object.id()
        self.todos = [ToDo.from_sb_object(i) for i in area_object.toDos()]
        self.tags = area_object.tagNames().split(", ")
        self.suspended = bool(area_object.suspended())
        # self.projects = area_object.projects()


class Contacts(ThingsObject):
    # TODO
    pass


class Contact:
    # TODO
    pass
