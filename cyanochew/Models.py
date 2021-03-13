from PyQt5.Qt import QStandardItemModel, QStandardItem
from PyQt5 import QtCore


class RegistersModel(QStandardItemModel):

    def data(self, index, role):
        print(role)
        return QStandardItemModel.data(self, index, role)