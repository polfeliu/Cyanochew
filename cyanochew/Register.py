import sys
from PyQt5.Qt import QStandardItem
from Field import Field


class RegisterItem(QStandardItem):pass
class RegisterTitle(QStandardItem):pass
class RegisterDescription(QStandardItem):pass
class RegisterAddress(QStandardItem):pass
class RegisterLength(QStandardItem):pass
class RegisterSigned(QStandardItem):pass
class RegisterReadWrite(QStandardItem):pass


class Register:

    RegisterItem = None

    title = None
    description = None
    address = None
    length = None
    signed = None
    readWrite = None

    def __init__(self, name: str, data: dict):
        self.RegisterItem = RegisterItem(name)

        if 'title' in data:
            self.title = RegisterTitle(data['title'])
        else:
            self.title = RegisterTitle()

        if 'description' in data:
            self.description = RegisterDescription(data['description'])
        else:
            self.description = RegisterDescription()

        if 'address' in data:
            self.address = RegisterAddress(data['address'])
        else:
            self.address = RegisterAddress()

        if 'length' in data:
            self.length = RegisterLength(data['length'])
        else:
            self.length = RegisterLength()

        if 'signed' in data:
            self.signed = RegisterSigned(data['signed'])
        else:
            self.signed = RegisterSigned()

        if 'readWrite' in data:
            self.readWrite = RegisterReadWrite(data['readWrite'])
        else:
            self.readWrite = RegisterReadWrite()

    def toData(self):
        register = {} #TODO
        register['title'] = ""
        register['description'] = ""
        register['address'] = ""
        register['length'] = ""
        register['signed'] = ""
        register['readWrite'] = ""
        return register

    def getRegisterViewRow(self):
        null = QStandardItem("")
        null.setEditable(False)
        return [
            self.RegisterItem,
            self.address,
            self.length,
            self.signed,
            self.readWrite,
            self.title,
            self.description
        ]

    def getRegisterViewRowIndex(self):
        return self.RegisterItem.index().row()

    def addFieldToTree(self, field: Field):
        self.RegisterItem.appendRow(
            field.getRegisterViewRow()
        )