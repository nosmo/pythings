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


class ThingsCollection(ThingsObject):
    """A collection of wrapped Things objects.

    Subclasses supply the contents by implementing _fetch(); everything
    is queried up front, so building one of these is as slow as the
    AppleScript interface is (see the README).
    """

    def __init__(self):
        super().__init__()
        self._items = list(self._fetch())

    def _fetch(self):
        """Yield the wrapped objects that make up this collection."""
        raise NotImplementedError

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]


class Projects(ThingsCollection):
    def _fetch(self):
        return (Project(i) for i in self.things.projects())

    @property
    def projects(self):
        return self._items


class Project(ThingsObject):
    def __init__(self, project_object):
        super().__init__()
        self.project_object = project_object
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

    AppleScript properties of a ToDo - id, tagNames,
    cancellationDate, creationDate, dueDate, contact, modficationDate,
    project, A specific osascript ID (referenced in the bridge
    object), notes, activationDate, completionDate, status, name

    Instantiating a ToDo creates one in Things. To wrap a ToDo that
    already exists, use from_sb_object() or from_id().

    """

    def __init__(self, name="", tags=None, notes="",
                 location="Inbox", creation_area=""):
        super().__init__()

        self.name = name
        self.notes = notes
        self.tags = list(tags) if tags else []

        if location and creation_area:
            warnings.warn("Inserting to a location and a creation_area at the "
                          "same time will create two ToDos")

        self.todo_object = self.things.classForScriptingClass_("to do").alloc()
        self.todo_object = self.todo_object.initWithProperties_({
            "name": name,
            "tagNames": ", ".join(self.tags),
            "notes": notes,
        })

        for thingslist in self.things.lists():
            if thingslist.name() == location:
                thingslist.toDos().append(self.todo_object)
                break
        else:
            # In rare cases where there has been some kind of weird
            # internal OS X fuck-up, self.things.lists() will be empty
            # despite Things performing perfectly fine and ToDos being
            # accessed correctly. I have no idea how to reproduce or
            # guard against it, so throwing an exception here is okay
            # with me for now.
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

        self._read_bridge_properties()

    @classmethod
    def from_sb_object(cls, todo_object):
        """Wrap an existing ScriptingBridge ToDo, creating nothing."""
        todo = cls.__new__(cls)
        ThingsObject.__init__(todo)
        todo.todo_object = todo_object
        todo.name = todo_object.name()
        todo.notes = todo_object.notes()
        todo.tags = todo_object.tagNames().split(", ")
        todo._read_bridge_properties()
        return todo

    @classmethod
    def from_id(cls, desired_id):
        """Wrap the existing ToDo with the given Things id."""
        return cls.from_sb_object(get_things().toDos().objectWithID_(desired_id))

    def _read_bridge_properties(self):
        self.thingsid = self.todo_object.id()
        self.creation_date = self.todo_object.creationDate()
        self.modification_date = self.todo_object.modificationDate()

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


class ToDos(ThingsCollection):

    def __init__(self, thingslist=None):
        self.thingslist = thingslist
        super().__init__()

    def _fetch(self):
        if self.thingslist:
            selectedlist = None
            for templist in self.things.lists():
                if templist.name() == self.thingslist:
                    selectedlist = templist
                    break
            if not selectedlist:
                # get ready to wait
                selectedlist = self.things
            todos = selectedlist.toDos()
        else:
            everything = list(self.things.toDos().get() or [])
            todos = []
            if everything:
                # The unscoped query can hand back entries that aren't
                # ToDos, so key off the type of a known-good one rather
                # than trusting everything in the list.
                todotype = type(everything[0])
                todos = [i for i in everything if isinstance(i, todotype)]

        for todo in todos:
            try:
                yield ToDo.from_sb_object(todo)
            except IndexError:
                # If Things is in use while we're working on it the
                # index length can sometimes change. Skip whatever
                # moved out from under us and plough on regardless.
                continue

    @property
    def todos(self):
        return self._items


class Areas(ThingsCollection):
    def _fetch(self):
        return (Area(i) for i in self.things.areas())

    @property
    def areas(self):
        return self._items


class Area:
    def __init__(self, area_object):
        self.area_object = area_object
        self.name = area_object.name()
        self.thingsid = area_object.id()
        self.todos = [ToDo.from_sb_object(i) for i in area_object.toDos()]
        self.tags = area_object.tagNames().split(", ")
        self.suspended = bool(area_object.suspended())
        # self.projects = area_object.projects()


class Contacts(ThingsCollection):
    # TODO
    def _fetch(self):
        raise NotImplementedError


class Contact:
    # TODO
    pass
