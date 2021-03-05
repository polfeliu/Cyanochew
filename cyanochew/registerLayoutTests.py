from PyQt5 import QtCore, QtGui, QtWidgets
from registerLayout import RegisterLayoutView

app = QtWidgets.QApplication([])
volume = RegisterLayoutView()
volume.show()
app.exec_()