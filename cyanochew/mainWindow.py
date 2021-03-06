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
                    self.expandFields(name, fielddata, self.info, "info")

        print(self.dataHandles)


    def expandFields(self, name, obj, parent, basename):
        handlename = f'{basename}.{name}'
        if 'type' not in obj or obj['type'] == 'string':
            if 'description' in obj:
                description = obj['description']
            else:
                description = ""

            lineedit = QtWidgets.QLineEdit()
            lineedit.setToolTip(description)
            self.dataHandles[handlename] = lineedit
            parent.addRow(name, lineedit)

        elif obj['type'] == 'object':
            form = QtWidgets.QFormLayout()
            parent.addRow(name,form)
            for childname, childfielddata in obj['properties'].items():
                self.expandFields(childname, childfielddata, form, handlename)
        else:
            print(name + "##############################")
            pprint(obj)


app = QtWidgets.QApplication([])
window = Window()
app.exec_()