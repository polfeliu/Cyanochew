import sys
from PyQt5.Qt import QStandardItem

class FieldItem(QStandardItem):pass
class FieldBitEnd(QStandardItem):
    def __init__(self, bitEnd):
        super().__init__(str(bitEnd))
class FieldBitStart(QStandardItem):
    def __init__(self, bitStart):
        super().__init__(str(bitStart))
class FieldDescription(QStandardItem):pass
class FieldEnum(QStandardItem):pass
class FieldReadWrite(QStandardItem):pass
class FieldRegister(QStandardItem):pass
class FieldTitle(QStandardItem):pass
class FieldType(QStandardItem):pass

class NullItem(QStandardItem):
    def __init__(self):
        super(QStandardItem,self).__init__()
        self.setEditable(False)

class Field:

    FieldItem = None

    bitEnd = None
    bitStart  = None
    description  = None
    enum = None
    readWrite = None
    register = None
    title = None
    type = None

    registerViewFieldItem = None
    registerViewTitle = None
    registerViewDescription = None


    def __init__(self, name: str, data: dict):

        self.FieldItem = FieldItem(name)
        self.registerViewFieldItem = FieldItem(name)
        self.registerViewFieldItem.setEditable(False)

        if 'bitEnd' in data:
            self.bitEnd = FieldBitEnd(int(data['bitEnd']))
        else:
            self.bitEnd = FieldBitEnd()

        if 'bitStart' in data:
            self.bitStart = FieldBitStart(int(data['bitStart']))
        else:
            self.bitStart = FieldBitStart()

        if 'description' in data: #Required
            self.description = FieldDescription(data['description'])
            self.registerViewDescription = FieldDescription(data['description'])
        else:
            self.description = FieldDescription()
            self.registerViewDescription = FieldDescription()
        self.registerViewDescription.setEditable(False)

        if 'enum' in data: #TODO, for now storing the data on the same dict
            self.enum = data['enum']

        if 'readWrite' in data: #Required
            self.readWrite = FieldReadWrite(data['readWrite'])
        else:
            self.readWrite = FieldReadWrite()

        if 'type' in data:
            self.type = FieldType(data['type'])
        else:
            self.type = FieldType()

        if 'register' in data:
            self.register = FieldRegister(
                data['register'].split("#/registers/")[1]
            )
        else:
            self.register = FieldRegister()

        if 'title' in data: #Required
            self.title = FieldTitle(data['title'])
            self.registerViewTitle = FieldTitle(data['title'])
        else:
            self.title = FieldTitle()
            self.registerViewTitle = FieldTitle()
        self.registerViewTitle.setEditable(False)


    def toData(self):
        field = {} #TODO
        field['readWrite'] = self.readWrite.text()
        field['bitStart'] = int(self.bitStart.text())
        field['bitEnd'] = int(self.bitEnd.text())
        field['type'] = self.type.text()
        field['title'] = self.title.text()
        field['description'] = self.description.text()
        field['enum'] = self.enum
        field['register'] = "#/registers/" + self.register.text()
        return field

    def getFieldViewRow(self):
        return [
            self.FieldItem,
            self.readWrite,
            self.bitStart,
            self.bitEnd,
            self.type,
            self.title,
            self.description,
            self.register,
        ]

    def getFieldViewRowIndex(self):
        return self.FieldItem.index().row()


    def getRegisterViewRow(self):
        return [
            self.registerViewFieldItem,
            NullItem(),
            NullItem(),
            NullItem(),
            NullItem(),
            self.registerViewTitle,
            self.registerViewTitle
        ]

    def getRegisterName(self):
        if isinstance(self.register, QStandardItem):
            return self.register.text()
        else:
            return False