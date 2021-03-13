from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.Qt import QStandardItemModel, QStandardItem

import json
import sys

from pprint import pprint

from Models import RegisterItem, FieldItem


# TODO Show data in Hex/Decimal/Binary
# TODO Improve edit of lists (for example i2c addresses)


class Window(QtWidgets.QMainWindow):

    dataHandles = {}

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("mainWindow.ui", self)

        self.cyanobyteVersion = self.findChild(QtWidgets.QLabel, "cyanobyteVersion")
        self.dataHandles["#/cyanobyte"] = self.cyanobyteVersion

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
        self.show()

        self.loadYamlFile()#Temporary, normally will be made from open command
        #self.reset()

    data = None

    def addlog(self, msg):
        self.log.appendPlainText(msg)

    def reset(self):
        for name, handle in self.dataHandles.items():
            if isinstance(handle, QtWidgets.QGroupBox):
                pass
            elif isinstance(handle, QtWidgets.QCheckBox):
                handle.setChecked(False)
            elif isinstance(handle, QtWidgets.QRadioButton):
                handle.setAutoExclusive(False)
                handle.setChecked(False)
                handle.setAutoExclusive(True)
            else:
                handle.clear()

        self.enableSPI(False)
        self.enableI2C(False)

    def loadYamlFile(self):
        import yaml
        with open('../test/peripherals/example.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        self.enableI2C('i2c' in data)
        self.enableSPI('spi' in data)

        self.dataToFields(data)

    def enableI2C(self, set):
        self.I2CEnable.setChecked(set)
        for name, handle in self.dataHandles.items():
            if name.startswith("#/i2c/"):
                handle.setEnabled(set)

    def enableSPI(self, set):
        self.SPIEnable.setChecked(set)
        for name, handle in self.dataHandles.items():
            if name.startswith("#/spi/"):
                handle.setEnabled(set)

    def dataToFields(self, data, baseaddress="#"):
        for key, item in data.items():
            address= f'{baseaddress}/{key}'
            if address == "#/registers":
                for name, register in item.items():
                    self.addRegister(name,register)
            if address == "#/fields":
                for name, field in item.items():
                    self.addField(name, field)
            elif isinstance(item, str):
                self.safeSetField(address, item)
            elif isinstance(item, int):
                self.safeSetField(address, item)
            elif isinstance(item, dict):
                self.dataToFields(item, address)
            elif isinstance(item, list):
                self.safeSetField(address, str(item).strip('[]'))
            else:
                self.addlog(f"Cannot Set field{address}")

    def addField(self, name, field):
        if 'title' not in field:
            field['title'] = "" #required

        if 'description' not in field:
            field['description'] = "" #required

        if 'register' not in field:
            field['register'] = "ND"

        if 'readWrite' not in field:
            field['readWrite'] = "ND" #required
            #Must be R, R/W, W, n

        if 'bitstart' not in field:
            field['bitstart'] = 0;

        if 'bitend' not in field:
            field['bitend'] = 0

        if 'type' not in field:
            field['type'] = 0
            #Must enum, number

        if 'enum' not in field:
            field['enum'] = []
            #TODO

        registername = field['register'].split("#/registers/")[1]

        self.FieldsTreeRoot.appendRow([
            FieldItem(name),
            QStandardItem(field['readWrite']),
            QStandardItem(field['bitstart']),
            QStandardItem(field['bitend']),
            QStandardItem(field['type']),
            QStandardItem(field['title']),
            QStandardItem(field['description']),
            QStandardItem(registername),
        ])

        address = "#/fields/" + name
        self.dataHandles[address] = self.FieldsTreeRoot.child(self.FieldsModel.rowCount() - 1)

        self.addFieldToRegisterTree(
            registername,
            name,
            field
        )

    def addRegister(self, name, register):
        if 'title' not in register:
            register['title'] = "" #required

        if 'description' not in register:
            register['description'] = "" #required

        if 'address' not in register:
            register['address'] = 0 #required

        if 'length' not in register:
            register['length'] = 0 #required

        if 'signed' not in register:
            register['signed'] = "ND"

        if 'readWrite' not in register:
            register['readWrite'] = "ND"

        self.RegistersTreeRoot.appendRow([
            RegisterItem(name),
            QStandardItem(str(register['address'])),
            QStandardItem(str(register['length'])),
            QStandardItem(register['signed']),
            QStandardItem(register['readWrite']),
            QStandardItem(register['title']),
            QStandardItem(register['description']),
        ])

        address = "#/registers/" + name
        self.dataHandles[address] = self.RegistersTreeRoot.child(self.RegistersModel.rowCount() - 1)


    def addFieldToRegisterTree(self, registername, name, field):
        if "#/registers/" + registername not in self.dataHandles:
            return False

        register = self.dataHandles["#/registers/" + registername]

        null = QStandardItem("")
        null.setEditable(False)

        register.appendRow([
            QStandardItem(name),
            null,
            QStandardItem(str(field['bitend'] - field['bitstart'])),
            null,
            null,
            QStandardItem(field['title']),
            QStandardItem(field['description'])
        ])


    def getFieldsOfRegister(self, registername):
        fields = []
        for name, item in self.dataHandles.items():
            if isinstance(item, FieldItem):
                name = self.FieldsModel.item(item.index().row(), 7).text() # register name is the 7th column
                if registername == name:
                    fields.append(item)

        return fields


    def newRegister(self):
        names = [name for name in self.dataHandles.keys() if name.startswith("#/registers/newRegister")]
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

        #TODO check if there are fields that are already pointing to this new register


    def editRegister(self):
        index = self.RegisterTree.currentIndex()
        item = self.RegistersModel.item(index.row())

        if isinstance(item, RegisterItem):
            key = "#/registers/" + item.text()

        #self.getFieldsOfRegister()

    def deleteRegister(self):
        index = self.RegisterTree.currentIndex()
        item = self.RegistersModel.item(index.row())

        if isinstance(item, RegisterItem):
            key = "#/registers/" + item.text()
            if key in self.dataHandles:
                del self.dataHandles[key]
            self.RegistersModel.removeRow(index.row(), index.parent())


    def newField(self):
        pass

    def editField(self):
        pass

    def deleteField(self):
        pass

    def safeSetField(self, address, value):
        if address in self.dataHandles:
            if isinstance(self.dataHandles[address], QtWidgets.QLabel):
                self.dataHandles[address].setText(value)
            elif isinstance(self.dataHandles[address], QtWidgets.QLineEdit):
                self.dataHandles[address].setText(value)
            elif isinstance(self.dataHandles[address], QtWidgets.QGroupBox):
                subaddress = f'{address}.{value}'
                self.dataHandles[subaddress].setChecked(True)
            elif isinstance(self.dataHandles[address], QtWidgets.QSpinBox):
                self.dataHandles[address].setValue(value)
            else:
                self.addlog(f"cannot set field {address} of type type {self.dataHandles[address]}")
        else:
            self.addlog(f"{address} doesn't exist in the UI")

    def readData(self, address):
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
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.info, "#/info")
            elif group == "i2c":
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.I2C, "#/i2c")
            elif group == "spi":
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.SPI, "#/spi")
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

    def createRegistersUI(self):
        #Button
        buttons = QtWidgets.QHBoxLayout()
        new = QtWidgets.QPushButton("New")
        new.setMaximumWidth(100)
        new.clicked.connect(self.newRegister)
        edit = QtWidgets.QPushButton("Edit")
        edit.setMaximumWidth(100)
        edit.clicked.connect(self.editRegister)
        delete = QtWidgets.QPushButton("Delete")
        delete.setMaximumWidth(100)
        delete.clicked.connect(self.deleteRegister)
        buttons.addWidget(new)
        buttons.addWidget(edit)
        buttons.addWidget(delete)
        self.Registers.addLayout(buttons)

        #Model
        self.RegistersModel = QStandardItemModel()
        self.RegistersModel.setHorizontalHeaderLabels(["Name", "Address", "Length", "Signed", "R/W", "Title", "Description"])
        #self.RegistersModel.dataChanged.connect(...) TODO
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


        self.Registers.addWidget(self.RegisterTree)

    def createFieldsUI(self):
        # Button
        buttons = QtWidgets.QHBoxLayout()
        new = QtWidgets.QPushButton("New")
        new.setMaximumWidth(100)
        new.clicked.connect(self.newField)

        delete = QtWidgets.QPushButton("Delete")
        delete.setMaximumWidth(100)
        delete.clicked.connect(self.deleteField)
        buttons.addWidget(new)

        buttons.addWidget(delete)
        self.Fields.addLayout(buttons)

        # Model
        self.FieldsModel = QStandardItemModel()
        self.FieldsModel.setHorizontalHeaderLabels(
            ["Name", "R/W", "bitstart", "bitend", "type", "Title", "Description", "Register"])
        # self.FieldModel.dataChanged.connect(...) TODO
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

        self.Fields.addWidget(self.FieldTree)



    def createFunctionsUI(self):
        pass

    def createRadioField(self, name, description,  obj, parent, basename):
        groupbox = QtWidgets.QGroupBox()
        self.dataHandles[basename] = groupbox
        groupboxlayout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(groupboxlayout)
        groupbox.setToolTip(description)

        for option in obj['enum']:
            radiobutton = QtWidgets.QRadioButton(option)
            groupboxlayout.addWidget(radiobutton)
            handlename = f'{basename}.{option}'
            self.dataHandles[handlename] = radiobutton

        parent.addRow(name, groupbox)

    def createCheckBoxField(self, name, description,  obj, parent, basename):
        groupbox = QtWidgets.QGroupBox()
        self.dataHandles[basename] = groupbox
        groupboxlayout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(groupboxlayout)
        groupbox.setToolTip(description)

        for option in obj['enum']:
            radiobutton = QtWidgets.QCheckBox(option)
            groupboxlayout.addWidget(radiobutton)
            handlename = f'{basename}.{option}'
            self.dataHandles[handlename] = radiobutton

        parent.addRow(name, groupbox)

    def createLineField(self, name, description,  obj, parent, basename):
        lineedit = QtWidgets.QLineEdit()
        lineedit.setToolTip(description)
        self.dataHandles[basename] = lineedit
        parent.addRow(name, lineedit)

    def createSpinBoxField(self, name, description, obj, parent, basename, type='double'):
        if type == 'double':
            spinbox = QtWidgets.QDoubleSpinBox()
        elif type == 'integer':
            spinbox = QtWidgets.QSpinBox()
        spinbox.setRange(0,1000000000)
        spinbox.setToolTip(description)
        self.dataHandles[basename] = spinbox
        parent.addRow(name, spinbox)

    def expandField(self, name, obj, parent, basename):
        handlename = f'{basename}/{name}'

        if 'description' in obj:
            description = obj['description']
        else:
            description = ""

        if 'enum' in obj:

            self.createRadioField(
                name,
                description,
                obj,
                parent,
                handlename
            )
        elif 'anyOf' in obj:
            for data in obj['anyOf']:
                if 'enum' in data:
                    self.createCheckBoxField(
                        name,
                        description,
                        data,
                        parent,
                        handlename
                    )
        elif 'type' not in obj or obj['type'] == 'string':
            self.createLineField(
                name,
                description,
                obj,
                parent,
                handlename)
        elif obj['type'] == 'number':
            self.createSpinBoxField(
                name,
                description,
                obj,
                parent,
                handlename,
            )
        elif obj['type'] == 'integer':
            self.createSpinBoxField(
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
            for childname, childfielddata in obj['properties'].items():
                self.expandField(childname, childfielddata, form, handlename)
        else:
            self.addlog(f"Cannot expand field {handlename} when loading the spec")


app = QtWidgets.QApplication([])
window = Window()
app.exec_()