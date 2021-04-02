from _ast import List, Dict

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.Qt import QStandardItemModel, QStandardItem

import json
import sys
import yaml
from Field import Field, FieldItem, FieldReadWriteDelegate, FieldBitStartDelegate, FieldBitEndDelegate, FieldTypeDelegate, FieldRegisterDelegate
from Register import Register, RegisterItem, RegisterLengthDelegate, RegisterAddressDelegate, RegisterSignedDelegate, RegisterReadWriteDelegate
from pprint import pprint

from registerLayout import RegisterLayoutView

class Window(QtWidgets.QMainWindow):

    objectHandles = {}

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("mainWindow.ui", self)

        self.cyanobyteVersion = self.findChild(QtWidgets.QLabel, "cyanobyteVersion")
        self.objectHandles["#/cyanobyte"] = self.cyanobyteVersion

        info = self.findChild(QtWidgets.QWidget, "Info")
        self.info = QtWidgets.QFormLayout()
        info.setLayout(self.info)

        I2C = self.findChild(QtWidgets.QWidget, "I2C")
        self.I2C = QtWidgets.QFormLayout()
        self.I2CEnable = QtWidgets.QCheckBox("Enable")
        self.I2CEnable.stateChanged.connect(self.enableI2C)
        self.I2C.addRow("I2C", self.I2CEnable)
        I2C.setLayout(self.I2C)

        SPI = self.findChild(QtWidgets.QWidget, "SPI")
        self.SPI = QtWidgets.QFormLayout()
        self.SPIEnable = QtWidgets.QCheckBox("Enable")
        self.SPIEnable.stateChanged.connect(self.enableSPI)
        self.SPI.addRow("SPI", self.SPIEnable)
        SPI.setLayout(self.SPI)

        Registers = self.findChild(QtWidgets.QWidget, "Registers")
        self.Registers = QtWidgets.QVBoxLayout()
        Registers.setLayout(self.Registers)

        Fields = self.findChild(QtWidgets.QWidget, "Fields")
        self.Fields = QtWidgets.QVBoxLayout()
        Fields.setLayout(self.Fields)

        Functions = self.findChild(QtWidgets.QWidget, "Functions")
        self.Functions = QtWidgets.QFormLayout()
        Functions.setLayout(self.Functions)

        Extensions = self.findChild(QtWidgets.QWidget, "Extensions")
        self.Extensions = QtWidgets.QFormLayout()
        Extensions.setLayout(self.Extensions)


        Lifecycle = self.findChild(QtWidgets.QWidget, "Lifecycle")
        self.Lifecycle = QtWidgets.QFormLayout()
        Lifecycle.setLayout(self.Lifecycle)


        self.log = self.findChild(QtWidgets.QPlainTextEdit, "log")

        self.loadPropertiesFromSchema()

        self.actionNew = self.findChild(QtWidgets.QAction, "actionNew")
        self.actionNew.triggered.connect(self.newFile)

        self.actionOpen = self.findChild(QtWidgets.QAction, "actionOpen")
        self.actionOpen.triggered.connect(
            lambda: self.openFile(
                QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')[0]
            )
        )

        self.actionSave = self.findChild(QtWidgets.QAction, "actionSave")
        self.actionSave.triggered.connect(
            lambda: self.saveFile(
                self.openedFile
            )
        )
        self.actionSaveAs = self.findChild(QtWidgets.QAction, "actionSaveAs")
        self.actionSaveAs.triggered.connect(
            lambda: self.saveFile(
                QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')[0]
            )
        )

        self.actionSaveCopy = self.findChild(QtWidgets.QAction, "actionSaveCopy")
        self.actionSaveCopy.triggered.connect(
            lambda: self.saveFile(
                QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')[0],
                copy=True
            )
        )

        self.show()

        #self.openFile('../test/peripherals/example.yaml')#Temporary, normally will be made from open command
        #self.saveFile('../test/peripherals/exampleSaveAs.yaml', copy=True)#Temporary
        #self.reset()

    data = None

    def addlog(self, msg: str):
        self.log.appendPlainText(msg)

    def reset(self):
        for name, handle in self.objectHandles.items():
            if isinstance(handle, QtWidgets.QGroupBox):
                pass
            elif isinstance(handle, QtWidgets.QCheckBox):
                handle.setChecked(False)
            elif isinstance(handle, QtWidgets.QRadioButton):
                handle.setAutoExclusive(False)
                handle.setChecked(False)
                handle.setAutoExclusive(True)
            elif isinstance(handle, QtWidgets.QLabel):
                handle.clear()
            elif isinstance(handle, QtWidgets.QLineEdit):
                handle.clear()
            elif isinstance(handle, QtWidgets.QSpinBox):
                handle.clear()
            elif isinstance(handle, QtWidgets.QDoubleSpinBox):
                handle.clear()
            else:
                self.addlog(f"Cannot reset Handle {name} of type {type(handle)}")

        #TODO Delete All registers and fields

        self.enableSPI(False)
        self.enableI2C(False)
        self.openedFile = None

    def newFile(self):
        diag = QtWidgets.QMessageBox()
        diag.setIcon(QtWidgets.QMessageBox.Warning)
        diag.setText("Do you want to create a new file?")
        diag.setInformativeText("You will lose all unsaved changes")
        diag.setWindowTitle("New File")
        diag.setStandardButtons(QtWidgets.QMessageBox.Ok |QtWidgets.QMessageBox.Cancel)
        diag.buttonClicked.connect(self.newFileAnswer)
        diag.exec_()

    def newFileAnswer(self, button):
        if button.text() == 'OK':
            self.reset()
            self.actionSave.setEnabled(False)
            self.actionSaveAs.setEnabled(True)
            self.actionSaveCopy.setEnabled(False)


    def openFile(self, path: str):
        if path == "":
            return False
        
        with open(path) as f:
            try:
                data = yaml.load(f, Loader=yaml.FullLoader)
            except:
                diag = QtWidgets.QMessageBox()
                diag.setIcon(QtWidgets.QMessageBox.Critical)
                diag.setText("The selected file is invalid")
                diag.setWindowTitle("Invalid File")
                diag.setStandardButtons(QtWidgets.QMessageBox.Ok)
                diag.exec_()
                return False


            self.enableI2C('i2c' in data)
            self.enableSPI('spi' in data)

            self.dataToObjects(data)
            self.originalData = data
            self.openedFile = path

            self.actionSave.setEnabled(True)
            self.actionSaveAs.setEnabled(True)
            self.actionSaveCopy.setEnabled(True)


    originalData = {}
    openedFile = None

    def saveFile(self, path: str, copy: bool = False):
        if path == "": #TODO It should also check if the folder exists
            #TODO Throw dialog
            return False

        data = self.objectsToData()
        with open(path, 'w') as f:
            yaml.dump(data, f)

        if not copy:
            self.openedFile = path
            self.originalData = data

        #If its a new file these actions wont be enabled
        self.actionSave.setEnabled(True)
        self.actionSaveCopy.setEnabled(True)


    def objectsToData(self):
        data = {}

        def addData(address: str, d: dict):
            keys = address.split("/")
            keys.pop(0) #Remove '#'
            loc = data
            for i, key in enumerate(keys):
                if key not in loc:  # Key doesn't exist
                    loc[key] = {}  # Create empty dict
                elif not isinstance(loc[key], dict):  # Key exist but its not a dict and cannot further be expanded.
                    del loc[key]  # Delete
                    loc[key] = {}  # and place empty dict

                if i < len(keys) - 1:
                    loc = loc[key]

            loc[key] = d

        for key, object in self.objectHandles.items():
            if key.startswith('#/i2c') and not self.I2CEnable.isChecked():
                continue
            elif key.startswith('#/spi') and not self.SPIEnable.isChecked():
                continue
            obj = self.getObject(key)

            if obj is not None:
                addData(key, obj)

        #Conserve Original Functions and Extensions for now (TODO)
        if 'functions' in self.originalData:
            data['functions'] = self.originalData['functions']

        if 'extensions' in self.originalData:
            data['extensions'] = self.originalData['extensions']

        return data

    def enableI2C(self, set: bool):
        self.I2CEnable.setChecked(set)
        for name, handle in self.objectHandles.items():
            if name.startswith("#/i2c/"):
                handle.setEnabled(set)

    def enableSPI(self, set: bool):
        self.SPIEnable.setChecked(set)
        for name, handle in self.objectHandles.items():
            if name.startswith("#/spi/"):
                handle.setEnabled(set)

    def dataToObjects(self, data: dict, baseaddress: str ="#"):
        for key, item in data.items():
            address= f'{baseaddress}/{key}'
            if address == "#/registers":
                for name, register in item.items():
                    self.addRegister(name,register)
            elif address == "#/fields":
                for name, field in item.items():
                    self.addField(name, field)
            elif isinstance(item, str):
                self.setObject(address, item)
            elif isinstance(item, int):
                self.setObject(address, item)
            elif isinstance(item, dict):
                self.dataToObjects(item, address)
            elif isinstance(item, list):
                self.setObject(address, item)
            else:
                self.addlog(f"Cannot Set object {address}")

    def addField(self, name: str, field: dict):
        f = Field(name, field)
        self.FieldsTreeRoot.appendRow(f.getFieldViewRow())
        self.objectHandles["#/fields/" + name] = f
        self.addFieldToRegisterTree(f)

    def getField(self, fieldname: str):
        address = "#/fields/" + fieldname

        if address in self.objectHandles:
            field = self.objectHandles[address]
            if isinstance(field, Field):
                return field
        return False

    def addRegister(self, name: str, register:dict):
        r = Register(name, register)

        self.RegistersTreeRoot.appendRow(r.getRegisterViewRow())

        address = "#/registers/" + name
        self.objectHandles[address] = r

        #Check if there are fields point to this register
        for fieldname, field in self.getFieldsOfRegister(name).items():
            self.addFieldToRegisterTree(field)

    def getRegister(self, registername):
        address = "#/registers/" + registername
        if address in self.objectHandles:
            register = self.objectHandles[address]
            if isinstance(register, Register):
                return register

        return False


    def getRegisterNames(self):
        names = []
        for key in self.objectHandles.keys():
            if key.startswith('#/registers/'):
                names.append(
                    key.split('#/registers/')[1]
                )
        return names

    def addFieldToRegisterTree(self, field: Field):
        registername = field.getRegisterName()
        if "#/registers/" + registername not in self.objectHandles:
            return False

        register = self.objectHandles["#/registers/" + registername]
        if isinstance(register, Register):
            register.addFieldToTree(field)

    def getFieldsOfRegister(self, registername) -> Dict(Field):
        fields = {}
        for address, item in self.objectHandles.items():
            if isinstance(item, Field):
                if registername == item.getRegisterName():
                    name = address.split("#/fields/")[1]
                    fields[name] = item
        return fields

    def newRegister(self):
        names = [name for name in self.objectHandles.keys() if name.startswith("#/registers/newRegister")]
        if len(names):
            num = 1
            for name in names:
                try:
                    split = name.split("#/registers/newRegister")
                    num = max(num, int(split[1]))
                except:
                    pass

            name = "newRegister" + str(num + 1)
        else:
            name = "newRegister"

        register = { #Required fields
            'title': f"title of {name}",
            'description': f"description of {name}",
            'address': 0,
            'length': 0
        }
        self.addRegister(name,register)

    registerLayoutView = None

    def registerLayoutViewSave(self):
        #delete fields of register
        for name, field in self.getFieldsOfRegister(self.editingRegister.getName()).items():
            self.deleteField(name)

        #create updated fields
        for field in self.registerLayoutView.registerLayout.fields:
            data = {
                'readWrite': field.readWrite,
                'bitStart': field.bitStart,
                'bitEnd': field.bitEnd,
                'type': field.type,
                'title': field.title,
                'description': field.description,
                'register': "#/registers/" + self.editingRegister.getName()
            }

            self.addField(field.name, data)

            print(field.name)

    def registerLayoutViewClose(self):
        self.registerLayoutView.close()
        self.registerLayoutView.deleteLater()
        self.registerLayoutView = None
        self.editingRegister = None

    editingRegister: Register = None

    def editRegisterSelected(self):
        index = self.RegisterTree.currentIndex()

        if index.parent().isValid(): #if it has parent it is a field, not a register
            #Open Parent of the selected field
            index = index.parent()

        item = self.RegistersModel.item(index.row())

        if not isinstance(item, RegisterItem):
            return False

        key = "#/registers/" + item.text()

        self.editingRegister = self.objectHandles[key]

        fields = self.getFieldsOfRegister(item.text())

        if self.registerLayoutView is not None:
            self.registerLayoutViewClose()

        self.registerLayoutView = None
        self.registerLayoutView = RegisterLayoutView()
        self.registerLayoutView.registerLayout.registerlength = self.editingRegister.getLength()

        self.registerLayoutView.SaveRequest.connect(self.registerLayoutViewSave)
        self.registerLayoutView.CloseRequest.connect(self.registerLayoutViewClose)
        self.registerLayoutView.setWindowTitle(item.text())


        #Load Data
        for name, field in fields.items():
            if isinstance(field, Field):
                self.registerLayoutView.registerLayout.newField(
                    name,
                    field.toData()
                )

        self.registerLayoutView.show()

    def deleteRegisterSelected(self):
        index = self.RegisterTree.currentIndex()

        if index.parent().isValid(): #If it has parent it is a field
            return False

        item = self.RegistersModel.item(index.row())

        if isinstance(item, RegisterItem):
            self.deleteRegister(item.text())

    def deleteRegister(self, name):
        key = "#/registers/" + name
        if key not in self.objectHandles:
            return False

        register = self.objectHandles[key]
        if isinstance(register, Register):
            del self.objectHandles[key]
            self.RegistersModel.removeRow(register.getRegisterViewRowIndex())

    def newField(self):
        names = [name for name in self.objectHandles.keys() if name.startswith("#/fields/newField")]
        if len(names):
            num = 1
            for name in names:
                try:
                    split = name.split("#/fields/newField")
                    num = max(num, int(split[1]))
                except:
                    pass

            name = "newField" + str(num + 1)
        else:
            name = "newField"

        field = {  # Required fields
            'title': f"title of {name}",
            'description': f"description of {name}",
        }
        self.addField(name, field)

    def deleteFieldSelected(self):
        index = self.FieldTree.currentIndex()
        item = self.FieldsModel.item(index.row())
        if isinstance(item, FieldItem):
            self.deleteField(item.text())

    def deleteField(self, name: str):
        key = "#/fields/" + name
        if key not in self.objectHandles:
            return False

        field = self.objectHandles[key]
        if isinstance(field, Field):
            registername = field.getRegisterName()
            self.removeFieldOfRegisterTree(registername, name)

            del self.objectHandles[key]
            self.FieldsModel.removeRow(field.getFieldViewRowIndex())

    def removeFieldOfRegisterTree(self, registername: str, fieldname: str):

        registerkey = f'#/registers/{registername}'
        if registerkey not in self.objectHandles:
            return False

        register = self.objectHandles[registerkey]
        if not isinstance(register, Register):
            return False
        registerModel = self.RegistersModel.item(register.getRegisterViewRowIndex())

        index = None

        for i in range(registerModel.rowCount()):
            field = registerModel.child(i,0)
            if field.text() == fieldname:
                index = i;

        if index is not None:
            registerModel.removeRow(index)

    def setObject(self, address, value):
        if address in self.objectHandles:
            obj = self.objectHandles[address]
            if isinstance(obj, QtWidgets.QLabel):
                obj.setText(value)
            elif isinstance(obj, ArrayEdit):
                obj.setArray(value)
            elif isinstance(obj, QtWidgets.QLineEdit):
                obj.setText(value)
            elif isinstance(obj, QtWidgets.QGroupBox):
                subaddress = f'{address}.{value}'
                self.objectHandles[subaddress].setChecked(True)
            elif isinstance(obj, QtWidgets.QSpinBox):
                obj.setValue(value)
            else:
                self.addlog(f"cannot set object {address} of type {type(self.objectHandles[address])}")
        else:
            self.addlog(f"{address} doesn't exist in the UI")

    def getObject(self, address):
        if address in self.objectHandles:
            obj = self.objectHandles[address]
            if isinstance(obj, QtWidgets.QLabel):
                return obj.text()
            elif isinstance(obj, ArrayEdit):
                return obj.getArray()
            elif isinstance(obj, QtWidgets.QLineEdit):
                text = obj.text()
                if text == "":
                    return None
                else:
                    return text
            elif isinstance(obj, QtWidgets.QGroupBox):
                for key in self.objectHandles:
                    if key.startswith(address) and key != address:
                        name = key.replace(address + ".", "")
                        if self.objectHandles[key].isChecked():
                            return name
                return None
            elif isinstance(obj, QtWidgets.QRadioButton):
                pass
            elif isinstance(obj, QtWidgets.QSpinBox):
                return self.objectHandles[address].value()
            elif isinstance(obj, QtWidgets.QDoubleSpinBox):
                return self.objectHandles[address].value()
            elif isinstance(obj, Register):
                return self.getRegister(address.split("/")[-1]).toData()
            elif isinstance(obj, Field):
                return self.getField(address.split("/")[-1]).toData()
            else:
                print(f"cannot retrieve object {address} of type {type(self.objectHandles[address])}")
                self.addlog(f"cannot retrieve object {address} of type {type(self.objectHandles[address])}")
        else:
            self.addlog(f"{address} doesn't exist in the UI")

    def readObject(self, address):
        for key in address.split('/'):
            if key == "#":
                unpack = self.data
            else:
                if key in unpack:
                    unpack = unpack[key]
                else:
                    return None

        return unpack

    def loadPropertiesFromSchema(self):
        with open('cyanobyte.schema.json') as f:
            data = json.load(f)

        for group,groupdata in data['properties'].items():
            if group == "info":
                for name, object in groupdata['properties'].items():
                    self.expandObject(name, object, self.info, "#/info")
            elif group == "i2c":
                for name, object in groupdata['properties'].items():
                    self.expandObject(name, object, self.I2C, "#/i2c")
            elif group == "spi":
                for name, object in groupdata['properties'].items():
                    self.expandObject(name, object, self.SPI, "#/spi")
            elif group == "registers":
                self.createRegistersUI()
            elif group == "fields":
                self.createFieldsUI()
            elif group == "functions":
                self.createFunctionsUI()
            elif group == "extensions":
                pass
            elif group == "cyanobyte":
                pass
            else:
                print(group)

        self.enableSPI(False)
        self.enableI2C(False)

    def createRegistersUI(self):
        #Button
        buttons = QtWidgets.QHBoxLayout()
        new = QtWidgets.QPushButton("New")
        new.setMaximumWidth(100)
        new.clicked.connect(self.newRegister)
        edit = QtWidgets.QPushButton("Edit")
        edit.setMaximumWidth(100)
        edit.clicked.connect(self.editRegisterSelected)
        delete = QtWidgets.QPushButton("Delete")
        delete.setMaximumWidth(100)
        delete.clicked.connect(self.deleteRegisterSelected)
        buttons.addWidget(new)
        buttons.addWidget(edit)
        buttons.addWidget(delete)
        self.Registers.addLayout(buttons)

        #Model
        self.RegistersModel = QStandardItemModel()
        self.RegistersModel.setHorizontalHeaderLabels(["Name", "Address", "Length", "Signed", "R/W", "Title", "Description"])
        self.RegistersModel.itemChanged.connect(self.RegistersItemChanged)
        self.RegistersTreeRoot = self.RegistersModel.invisibleRootItem()


        # TreeView
        self.RegisterTree = QtWidgets.QTreeView()
        self.RegisterTree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.RegisterTree.setModel(self.RegistersModel)
        self.RegisterTree.setUniformRowHeights(True)
        self.RegisterTree.setColumnWidth(0, 200)
        self.RegisterTree.setColumnWidth(1, 70)
        self.RegisterTree.setColumnWidth(2, 70)
        self.RegisterTree.setColumnWidth(3, 70)
        self.RegisterTree.setColumnWidth(4, 70)

        self.RegisterTree.setItemDelegateForColumn(1,RegisterAddressDelegate(self.RegisterTree))
        self.RegisterTree.setItemDelegateForColumn(2,RegisterLengthDelegate(self.RegisterTree))
        self.RegisterTree.setItemDelegateForColumn(3, RegisterSignedDelegate(self.RegisterTree))
        self.RegisterTree.setItemDelegateForColumn(4, RegisterReadWriteDelegate(self.RegisterTree))

        self.Registers.addWidget(self.RegisterTree)

    def RegistersItemChanged(self, item):
        if isinstance(item, RegisterItem): #Changed Name
            newname = self.RegistersModel.item(item.index().row(), 0).text()
            oldname = item.name

            #change fields that point to this register
            for fieldname, field in self.getFieldsOfRegister(oldname).items():
                field.register.setText(newname)

            item.name = newname #Update Name
            #move handle of name
            self.objectHandles[f'#/registers/{newname}'] = self.objectHandles.pop(f'#/registers/{oldname}')


    def FieldsItemChanged(self, item):
        if isinstance(item, FieldItem): #Changed Name
            newname = self.FieldsModel.item(item.index().row(), 0).text()
            oldname = item.name
            item.name = newname #Update Name
            #move handle of name
            self.objectHandles[f'#/fields/{newname}'] = self.objectHandles.pop(f'#/fields/{oldname}')
            name = newname
        else: #Changed Field props
            name = self.FieldsModel.item(item.index().row(), 0).text()

        field = self.getField(name)
        if isinstance(field, Field):
            field.itemDataChanged(item)


    def createFieldsUI(self):
        # Button
        buttons = QtWidgets.QHBoxLayout()
        new = QtWidgets.QPushButton("New")
        new.setMaximumWidth(100)
        new.clicked.connect(self.newField)

        delete = QtWidgets.QPushButton("Delete")
        delete.setMaximumWidth(100)
        delete.clicked.connect(self.deleteFieldSelected)
        buttons.addWidget(new)

        buttons.addWidget(delete)
        self.Fields.addLayout(buttons)

        # Model
        self.FieldsModel = QStandardItemModel()
        self.FieldsModel.setHorizontalHeaderLabels(
            ["Name", "R/W", "bitStart", "bitEnd", "type", "Title", "Description", "Register"])
        self.FieldsModel.itemChanged.connect(self.FieldsItemChanged)
        self.FieldsTreeRoot = self.FieldsModel.invisibleRootItem()

        # TreeView
        self.FieldTree = QtWidgets.QTreeView()
        self.FieldTree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.FieldTree.setModel(self.FieldsModel)
        self.FieldTree.setUniformRowHeights(True)
        self.FieldTree.setColumnWidth(0, 200)
        self.FieldTree.setColumnWidth(1, 70)
        self.FieldTree.setColumnWidth(2, 70)
        self.FieldTree.setColumnWidth(3, 70)

        self.FieldTree.setItemDelegateForColumn(1,FieldReadWriteDelegate(self.FieldTree))
        self.FieldTree.setItemDelegateForColumn(2,FieldBitStartDelegate(self.FieldTree))
        self.FieldTree.setItemDelegateForColumn(3,FieldBitEndDelegate(self.FieldTree))
        self.FieldTree.setItemDelegateForColumn(4,FieldTypeDelegate(self.FieldTree))


        self.FieldTree.setItemDelegateForColumn(7,FieldRegisterDelegate(self.FieldTree, self.getRegisterNames))

        self.Fields.addWidget(self.FieldTree)

    def createFunctionsUI(self):
        pass#TODO

    def createArrayObject(self, name, description, obj, parent, basename):
        arrayedit = ArrayEdit()
        arrayedit.setToolTip(description)
        self.objectHandles[basename] = arrayedit
        parent.addRow(name, arrayedit)

    def createRadioObject(self, name, description, obj, parent, basename):
        groupbox = QtWidgets.QGroupBox()
        self.objectHandles[basename] = groupbox
        groupboxlayout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(groupboxlayout)
        groupbox.setToolTip(description)

        for option in obj['enum']:
            radiobutton = QtWidgets.QRadioButton(option)
            groupboxlayout.addWidget(radiobutton)
            handlename = f'{basename}.{option}'
            self.objectHandles[handlename] = radiobutton

        parent.addRow(name, groupbox)


    def createCheckBoxObject(self, name, description, obj, parent, basename):
        groupbox = QtWidgets.QGroupBox()
        self.objectHandles[basename] = groupbox
        groupboxlayout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(groupboxlayout)
        groupbox.setToolTip(description)

        for option in obj['enum']:
            radiobutton = QtWidgets.QCheckBox(option)
            groupboxlayout.addWidget(radiobutton)
            handlename = f'{basename}.{option}'
            self.objectHandles[handlename] = radiobutton


        parent.addRow(name, groupbox)


    def createLineObject(self, name, description, obj, parent, basename):
        lineedit = QtWidgets.QLineEdit()
        lineedit.setToolTip(description)
        self.objectHandles[basename] = lineedit
        parent.addRow(name, lineedit)

    def createSpinBoxObject(self, name, description, obj, parent, basename, type='double'):
        if type == 'double':
            spinbox = QtWidgets.QDoubleSpinBox()
        elif type == 'integer':
            spinbox = QtWidgets.QSpinBox()
        spinbox.setRange(0,1000000000)
        spinbox.setToolTip(description)
        self.objectHandles[basename] = spinbox
        parent.addRow(name, spinbox)

    def expandObject(self, name, obj, parent, basename):
        handlename = f'{basename}/{name}'

        if 'description' in obj:
            description = obj['description']
        else:
            description = ""

        if handlename == "#/i2c/address":
            self.createArrayObject(
                name,
                description,
                obj,
                parent,
                handlename
            )
        elif 'enum' in obj:
            self.createRadioObject(
                name,
                description,
                obj,
                parent,
                handlename
            )
        elif 'anyOf' in obj:
            for data in obj['anyOf']:
                if 'enum' in data:
                    self.createRadioObject(
                        name,
                        description,
                        data,
                        parent,
                        handlename
                    )
                    #TODO Licenses can also be a string
        elif obj['type'] == 'string':
            self.createLineObject(
                name,
                description,
                obj,
                parent,
                handlename)
        elif obj['type'] == 'number':
            self.createSpinBoxObject(
                name,
                description,
                obj,
                parent,
                handlename,
            )
        elif obj['type'] == 'integer':
            self.createSpinBoxObject(
                name,
                description,
                obj,
                parent,
                handlename,
                type='integer'
            )
        elif obj['type'] == 'object':
            form = QtWidgets.QFormLayout()
            parent.addRow(name,form)
            for childname, childobject in obj['properties'].items():
                self.expandObject(childname, childobject, form, handlename)
        else:
            self.addlog(f"Cannot expand object {handlename} when loading the spec")

class ArrayEdit(QtWidgets.QLineEdit):

    def setArray(self, val):
        if not isinstance(val, list):
            val = [val] #encapsulate

        self.setText(str(val).strip('[]'))

    def getArray(self):
        #TODO Conversion to int for the address array. Maybe at the start we could store the types... (?)
        # Now if one of the items is not int()able the program crashes
        return [int(s.strip()) for s in self.text().split(",")]


app = QtWidgets.QApplication([])
window = Window()
app.exec_()