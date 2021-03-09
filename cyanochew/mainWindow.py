from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import json
import sys

from pprint import pprint

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
        self.Registers = QtWidgets.QFormLayout()
        Registers.setLayout(self.Registers)

        Fields = self.findChild(QtWidgets.QWidget, "Fields")
        self.Fields = QtWidgets.QFormLayout()
        Fields.setLayout(self.Fields)

        Functions = self.findChild(QtWidgets.QWidget, "Functions")
        self.Functions = QtWidgets.QFormLayout()
        Functions.setLayout(self.Functions)

        Functions = self.findChild(QtWidgets.QWidget, "Functions")
        self.Functions = QtWidgets.QFormLayout()
        Functions.setLayout(self.Functions)

        Extensions = self.findChild(QtWidgets.QWidget, "Extensions")
        self.Extensions = QtWidgets.QFormLayout()
        Extensions.setLayout(self.Extensions)

        self.log = self.findChild(QtWidgets.QPlainTextEdit, "log")

        self.loadPropertiesFromSchema()
        self.show()

        self.loadYamlFile()
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
            self.data = yaml.load(f, Loader=yaml.FullLoader)

        self.enableI2C('i2c' in self.data)
        self.enableSPI('spi' in self.data)

        self.dataToFields(self.data)

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
            if isinstance(item, str):
                self.safeSetField(address, item)
            elif isinstance(item, int):
                self.safeSetField(address, item)
            elif isinstance(item, dict):
                self.dataToFields(item, address)
            elif isinstance(item, list):
                self.safeSetField(address, str(item).strip('[]'))
            else:
                self.addlog(f"Cannot Set field{address}")

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
                self.loadRegisters()
            elif group == "fields":
                self.loadFields()
            elif group == "functions":
                self.loadFunctions()
            elif group == "extensions":
                pass
            elif group == "cyanobyte":
                pass
            else:
                print(group)

    def loadRegisters(self):
        pass

    def loadFields(self):
        pass

    def loadFunctions(self):
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