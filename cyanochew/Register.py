from PyQt5.Qt import QStandardItem, QStyledItemDelegate
from Field import Field
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget


class RegisterItem(QStandardItem):
    name = None
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)

class RegisterTitle(QStandardItem): #Required
    pass


class RegisterDescription(QStandardItem): #Required
    pass


class RegisterAddress(QStandardItem): #Required
    def __init__(self, address: int):
        super().__init__(str(address))


class RegisterLength(QStandardItem): #Required
    def __init__(self, length):
        super().__init__(str(length))


class RegisterSigned(QStandardItem):
    pass


class RegisterReadWrite(QStandardItem):
    pass

class RegisterLengthDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QtWidgets.QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(128)
        return editor

class RegisterAddressDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QtWidgets.QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(2**16)
        return editor

class RegisterSignedDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QtWidgets.QComboBox(parent)
        editor.addItem("")
        editor.addItem("true")
        editor.addItem("false")
        return editor

class RegisterReadWriteDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QtWidgets.QComboBox(parent)
        editor.addItem("")
        editor.addItem("R")
        editor.addItem("R/W")
        editor.addItem("W")
        editor.addItem("n")
        return editor

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
            self.description = RegisterDescription("")

        if 'address' in data:
            self.address = RegisterAddress(data['address'])
        else:
            self.address = RegisterAddress(0)

        if 'length' in data:
            self.length = RegisterLength(data['length'])
        else:
            self.length = RegisterLength(0)

        if 'signed' in data:
            self.signed = RegisterSigned(data['signed'])
        else:
            self.signed = RegisterSigned("")

        if 'readWrite' in data:
            self.readWrite = RegisterReadWrite(data['readWrite'])
        else:
            self.readWrite = RegisterReadWrite("")

    def toData(self):
        register = {}
        register['title'] = self.title.text()
        register['description'] = self.description.text()
        register['address'] = int(self.address.text())
        register['length'] = int(self.length.text())
        register['signed'] = self.signed.text()
        register['readWrite'] = self.readWrite.text()
        return register

    def getName(self) -> str:
        return self.RegisterItem.text()

    def getLength(self) -> int:
        return int(self.length.text())

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
