from App.config import getConfiguration
from raptus.torii import carrier

def getHumanSize(size):
        size
        if type(size) is type(''):
            return s

        if size >= 1048576.0:
            return '%.1fM' % (size/1048576.0)
        return '%.1fK' % (size/1024.0)


config = getConfiguration()

for db in config.databases:
    path = [i[1:] for i in db.getVirtualMountPaths()]
    mount = app
    if not '' in path:
        for i in path:
            mount = mount[i]
    db = mount._p_jar.db()
    size_before = getHumanSize(db.getSize())
    db.pack()
    size_after = getHumanSize(db.getSize())
    conversation(carrier.PrintText('Database: %s from %s to %s packed' % (db.database_name, size_before, size_after)))


