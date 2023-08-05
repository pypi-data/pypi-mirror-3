from pentacle.client import Authorization, Session
from pentacle.bus.partners import OpenPartneredClient
from pentacle.runtime import contextmanager

REGISTRY_SERVICE = 'penobscotrobotics.us/Pentacle/SystemRegistry'
REGISTRY_API = 'PenobscotRobotics[Registry::Active]'

DEFAULT_NOTES = 'todo'

class NoteManager:
    def __init__(self, username, secret_key = '', notes = DEFAULT_NOTES):
        self.username = username
        self.secret_key = secret_key
        self.notes = notes

    def addNote(self, addRecord, dateIndex = None, *recordArgs, **recordKwd):
        if dateIndex is None:
            dateIndex = CurrentDateIndex()

        auth = Authorization(username, secret_key)
        with Session(auth.Authenticate(OpenPartneredClient(REGISTRY_SERVICE))) as client:
            with client.api(REGISTRY_API) as api:
                with api.OpenDirectory(self.notes) as todo:
                    records = todo.getValue(dateIndex)
                    self.UpdateNoteRecords(records, addRecord, (recordArgs, recordKwd))
                    todo.setValue(dateIndex, records)
                    todo.synchronizeStore()

    def UpdateNoteRecords(self, records, addRecord, (recordArgs, recordKwd)):
        records.append(addRecord(records, *recordArgs, **recordKwd))

    # Types of Notes
    def addArtist(self, name, *albums):
        def createArtistRecord(records):
            name = str(name)
            albums = map(str, albums)
            return dict(name = name, albums = albums)

        return self.addNote(createArtistRecord)

# NoteManager('fraun').addArtist('tom waits', 'rain dogs', 'alice')
