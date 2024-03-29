import sys
from PyQt5.Qt import QStandardItem, QStyledItemDelegate
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget

class FieldItem(QStandardItem):
    name = None
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)


class FieldBitEnd(QStandardItem):
    def __init__(self, bitEnd):
        super().__init__(str(bitEnd))


class FieldBitStart(QStandardItem):
    def __init__(self, bitStart):
        super().__init__(str(bitStart))


class FieldDescription(QStandardItem):
    pass


class FieldEnum(QStandardItem):
    pass


class FieldReadWrite(QStandardItem):
    pass


class FieldRegister(QStandardItem):
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)
    pass


class FieldTitle(QStandardItem):
    pass


class FieldType(QStandardItem):
    pass


class NullItem(QStandardItem):
    def __init__(self):
        super(QStandardItem, self).__init__()
        self.setEditable(False)


class FieldReadWriteDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    valid = ["R", "R/W", "W", "n"]

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QComboBox:
        editor = QtWidgets.QComboBox(parent)
        editor.addItems(self.valid)
        return editor

class FieldBitStartDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QSpinBox:
        editor = QtWidgets.QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(128)
        return editor

class FieldBitEndDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QSpinBox:
        editor = QtWidgets.QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(128)
        return editor

class FieldTypeDelegate(QStyledItemDelegate):

    def __init__(self, owner):
        super().__init__(owner)

    valid = ['enum', 'number']

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QComboBox:
        editor = QtWidgets.QComboBox(parent)
        editor.addItem("")
        editor.addItems(self.valid)
        return editor

class FieldRegisterDelegate(QStyledItemDelegate):
    def __init__(self, owner, getter):
        super().__init__(owner)
        self.getter = getter #The getter function passed should list the possible registers

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QComboBox:
        editor = QtWidgets.QComboBox(parent)
        editor.addItem("")
        editor.addItems(self.getter())
        return editor


class Field:
    FieldItem = None

    bitEnd = None
    bitStart = None
    description = None
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

        if 'bitEnd' in data: #Spec does not require, but I think it should
            self.bitEnd = FieldBitEnd(int(data['bitEnd']))
        else:
            self.bitEnd = FieldBitEnd(0)

        if 'bitStart' in data:
            self.bitStart = FieldBitStart(int(data['bitStart']))
        else:
            self.bitStart = FieldBitStart(0)

        if 'description' in data:  # Required
            self.description = FieldDescription(data['description'])
        else:
            self.description = FieldDescription("")

        if 'enum' in data:  # TODO, for now storing the data on the same dict
            self.enum = data['enum']

        if 'readWrite' in data:  # Required
            self.readWrite = FieldReadWrite(data['readWrite'])
        else:
            self.readWrite = FieldReadWrite('')

        if 'type' in data:
            self.type = FieldType(data['type'])
        else:
            self.type = FieldType("")

        if 'register' in data:
            self.register = FieldRegister(
                data['register'].split("#/registers/")[1]
            )
        else:
            self.register = FieldRegister("")

        if 'title' in data:  # Required
            self.title = FieldTitle(data['title'])
        else:
            self.title = FieldTitle("")

    def getName(self) -> str:
        return self.FieldItem.text()

    def toData(self):
        field = {}
        field['readWrite'] = self.readWrite.text()#required
        field['bitStart'] = int(self.bitStart.text())
        field['bitEnd'] = int(self.bitEnd.text())

        if self.type.text() in FieldTypeDelegate.valid:
            field['type'] = self.type.text()

        field['title'] = self.title.text()#required
        field['description'] = self.description.text()#required

        field['enum'] = self.enum

        if self.register.text() != '':
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
        self.registerViewFieldItem = FieldItem(
            self.FieldItem.name
        )
        self.registerViewFieldItem.setEditable(False)

        self.registerViewTitle = FieldTitle(
            self.title.text()
        )
        self.registerViewTitle.setEditable(False)

        self.registerViewDescription = FieldDescription(
            self.description.text()
        )
        self.registerViewDescription.setEditable(False)

        return [
            self.registerViewFieldItem,
            NullItem(),
            NullItem(),
            NullItem(),
            NullItem(),
            self.registerViewTitle,
            self.registerViewDescription
        ]

    def getRegisterName(self):
        if isinstance(self.register, QStandardItem):
            return self.register.text()
        else:
            return False


    def itemDataChanged(self, item): #Some data has to be also updated on the register view
        if isinstance(item, FieldItem):
            if isinstance(self.registerViewFieldItem, FieldItem):
                self.registerViewFieldItem.setText(
                    item.text()
                )
        elif isinstance(item, FieldTitle):
            if isinstance(self.registerViewFieldItem, FieldTitle):
                self.registerViewTitle.setText(
                    item.text()
                )
        elif isinstance(item, FieldDescription):
            if isinstance(self.registerViewFieldItem, FieldDescription):
                self.registerViewDescription.setText(
                    item.text()
                )