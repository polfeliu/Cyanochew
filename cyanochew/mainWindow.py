from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import json

from pprint import pprint

class Window(QtWidgets.QMainWindow):

    dataHandles = {}

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("mainWindow.ui", self)

        info = self.findChild(QtWidgets.QWidget, "Info")
        self.info = QtWidgets.QFormLayout()
        info.setLayout(self.info)

        I2C = self.findChild(QtWidgets.QWidget, "I2C")
        self.I2C = QtWidgets.QFormLayout()
        I2C.setLayout(self.I2C)

        SPI = self.findChild(QtWidgets.QWidget, "SPI")
        self.SPI = QtWidgets.QFormLayout()
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


        self.loadPropertiesFromSchema()
        self.show()

    def loadPropertiesFromSchema(self):
        with open('cyanobyte.schema.json') as f:
            data = json.load(f)

        for group,groupdata in data['properties'].items():
            if group == "info":
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.info, "info")
            elif group == "i2c":
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.I2C, "I2C")
            elif group == "spi":
                for name, fielddata in groupdata['properties'].items():
                    self.expandField(name, fielddata, self.SPI, "SPI")
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

        #pprint(self.dataHandles)

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
        handlename = f'{basename}.{name}'

        lineedit = QtWidgets.QLineEdit()
        lineedit.setToolTip(description)
        self.dataHandles[handlename] = lineedit
        parent.addRow(name, lineedit)

    def createSpinBoxField(self, name, description, obj, parent, basename, type='double'):
        handlename = f'{basename}.{name}'
        if type == 'double':
            spinbox = QtWidgets.QDoubleSpinBox()
        elif type == 'integer':
            spinbox = QtWidgets.QSpinBox()
        spinbox.setToolTip(description)
        self.dataHandles[handlename] = spinbox
        parent.addRow(name, spinbox)

    def expandField(self, name, obj, parent, basename):
        handlename = f'{basename}.{name}'

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
            self.createLineField(name, description, obj, parent, handlename)
        elif obj['type'] == 'number':
            self.createSpinBoxField(
                name,
                description,
                obj,
                parent,
                basename,
            )
        elif obj['type'] == 'integer':
            self.createSpinBoxField(
                name,
                description,
                obj,
                parent,
                basename,
                type='integer'
            )
        elif obj['type'] == 'object':
            form = QtWidgets.QFormLayout()
            parent.addRow(name,form)
            for childname, childfielddata in obj['properties'].items():
                self.expandField(childname, childfielddata, form, handlename)
        else:
            print(name + "##############################")
            pprint(obj)


app = QtWidgets.QApplication([])
window = Window()
app.exec_()