import sqlobject

class UserAuth( sqlobject.SQLObject ):
    username = sqlobject.StringCol()
    domain = sqlobject.StringCol(default='localdomain')
    password = sqlobject.StringCol()


class JitsiProperty(sqlobject.SQLObject):

    class sqlmeta:
        defaultOrder=['spriority','ppriority']

    
    subject = sqlobject.StringCol(length=50)
    spriority = sqlobject.IntCol(default=10)
    ppriority = sqlobject.IntCol(default=10)
    propertyKey = sqlobject.StringCol()
    propertyValue = sqlobject.StringCol()

    subjectIndex = sqlobject.DatabaseIndex(subject)
