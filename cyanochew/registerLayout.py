from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from typing import List

# TODO When changing field name, it should validate that it doesn't already exist


class SplitField:
    row: int
    start:int
    end: int
    StartHandle: bool
    EndHandle: bool
    RectHandle: QtCore.QRect
    text: str

class FieldLayoutItem():
    name: str = None
    bitEnd: int = None
    bitStart: int = None
    description: str = None
    readWrite: str = None
    register: str = None
    title: str = None
    type: str = None

    overlapping: bool = False

    def __init__(self,
                 name: str,
                 bitEnd: int,
                 bitStart: int,
                 description: str,
                 readWrite: str,
                 register: str,
                 title: str,
                 type: str
                 ):
        self.name = name
        self.bitEnd = bitEnd
        self.bitStart = bitStart
        self.description = description
        self.readWrite = readWrite
        self.register = register
        self.title = title
        self.type = type

    split: List[SplitField] = []

    def calculateSplit(self, width: int):
        columnend = self.bitEnd % width
        rowend = self.bitEnd // width

        columnstart = self.bitStart % width
        rowstart = self.bitStart // width

        self.split = []

        splitbitend = 0
        splitbitstart = 0

        for row in range(rowend, rowstart+1):
            sf = SplitField()
            if row == rowend: #First row
                sf.end = columnend
                sf.EndHandle = True
            else:
                sf.end = 0
                sf.EndHandle = False

            if row == rowstart: #Last Row
                sf.start = columnstart
                sf.StartHandle = True
            else:
                sf.start = 7
                sf.StartHandle = False

            sf.row = row

            width = sf.start - sf.end + 1
            splitbitstart = splitbitend + width - 1

            sf.text = "%s\r\n[%i:%i]" % (
                self.name,
                splitbitstart,
                splitbitend
            )

            splitbitend = splitbitstart + 1

            self.split.append(sf)

    StartHandle: QtCore.QRect
    EndHandle: QtCore.QRect

class _RegisterLayout(QtWidgets.QWidget):
    SelectedSignal = QtCore.pyqtSignal(object)
    UpdatedData = QtCore.pyqtSignal()
    DoubleClickField = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    _padding: int = 4

    registerlength: int = 8

    selected = None#TODO

    bitwidth: int = 8

    nrows: int = 0

    fields: List[FieldLayoutItem] = []

    def newField(self, name: str, field: dict):
        try:
            f = FieldLayoutItem(
                name=name,
                bitEnd=field['bitEnd'],
                bitStart=field['bitStart'],
                description=field['description'],
                readWrite=field['readWrite'],
                register=field['register'],
                title=field['title'],
                type=field['type']
            )
            self.fields.append(f)
            return True
        except KeyError:
            return False

    # TODO
    def calculateOverlapping2(self):
        return False
        self.overlapping = {}
        for i, field in enumerate(self.fields):
            overlapped = False
            ran = range(field[1], field[2] + 1)
            name = field[0]
            for j, field2 in enumerate(self.fields):
                if i == j:  # Same element, ignore and continue searching
                    continue

                # Find if start element or end element is inside the range
                if field2[1] in ran or field2[2] in ran:
                    overlapped = True
                    break

            self.overlapping[i] = overlapped

    # TODO
    def updateSplitFields(self):
        for field in self.fields:
            field.calculateSplit(
                width=self.bitwidth
            )

        # TODO self.calculateOverlapping()
        return False

        if not self.dragging: #TODO Move to paint field
            self.nrows = max(self.nrows, row)
            self.resize(
                self.size().width(),
                self._padding + self.nrows * self.height_bitbox + 2
            )

    HorizontalMSB = True
    VerticalMSB = True


    # Translate rows and columns of fields according to the MSB settings
    def translateField(self, row, column):
        if self.HorizontalMSB:
            column = self.bitwidth - column - 1

        if self.VerticalMSB:
            row = self.nrows - row - 1

        return row, column

    def postoXY(self, pos):
        return pos % self.bitwidth, pos // self.bitwidth

    def updateBitWidth(self, bitwidth: int):
        self.bitwidth = bitwidth
        self.update()

    def updateNRows(self):
        maxrows = 1
        for field in self.fields:
            for split in field.split:
                maxrows = max(maxrows, split.row + 1)
        self.nrows = maxrows

    height_bitbox = 60

    # TODO
    def paintEvent(self, e: QtGui.QPaintEvent) -> None:

        # For now we will update the split fields every time, this could be optimitzed
        self.updateSplitFields()
        self.updateNRows()

        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()

        # Background
        brush.setColor(QtGui.QColor('lightgray'))
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # Canvas Size
        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        self.width_bitbox = d_width / self.bitwidth

        # Grid
        brush.setColor(QtGui.QColor('gray'))

        # Vertical
        for i in range(0, self.bitwidth + 1):
            rect = QtCore.QRect(
                int(self._padding + i * self.width_bitbox - 1),  # X
                int(0),  # Y
                int(2),  # W
                int(d_height)  # H
            )
            painter.fillRect(rect, brush)

        for field in self.fields:
            for split in field.split:
                row, x1 = self.translateField(split.row, split.start)
                _, x2 = self.translateField(row, split.end)

                left = min(x1, x2)
                width = abs(x1-x2) + 1

                if field.overlapping:
                    brush.setColor(QtGui.QColor(0xEF, 0x83, 0x54, 128))
                else:
                    brush.setColor(QtGui.QColor(0xEF, 0x83, 0x54, 255))

                split.RectHandle = QtCore.QRect(
                    int(self._padding + left * self.width_bitbox + 2),  # X
                    int(self._padding + row * self.height_bitbox + 2),  # Y
                    int(width * self.width_bitbox - 4),  # W
                    int(self.height_bitbox - 4)  # H
                )

                painter.fillRect(split.RectHandle, brush)

                # Handles
                if False: #TODO Selected condition
                    brush.setColor(QtGui.QColor(0, 0, 0))
                else:
                    brush.setColor(QtGui.QColor(70, 70, 70))

                if self.HorizontalMSB:
                    leftHandle = split.StartHandle
                    rightHandle = split.EndHandle
                else:
                    leftHandle = split.EndHandle
                    rightHandle = split.StartHandle

                if leftHandle:
                    # Draw Left Handle
                    handlerect = QtCore.QRect(
                        int(self._padding + left * self.width_bitbox + 5),
                        int(self._padding + row * self.height_bitbox + 17),
                        int(7),
                        int(self.height_bitbox - 22)
                    )
                    painter.fillRect(handlerect, brush)
                    if not self.HorizontalMSB:
                        field.EndHandle = handlerect
                    else:
                        field.StartHandle = handlerect

                if rightHandle:

                    # Draw Right Handle
                    handlerect = QtCore.QRect(
                        int(self._padding + (left + width) * self.width_bitbox - 12),
                        int(self._padding + row * self.height_bitbox + 17),
                        int(7),
                        int(self.height_bitbox - 22)
                    )
                    painter.fillRect(handlerect, brush)

                    if self.HorizontalMSB:
                        field.StartHandle = handlerect
                    else:
                        field.EndHandle = handlerect

                font = painter.font()
                if False: #TODO Selected condition
                    font.setBold(True)
                    painter.setFont(font)

                painter.drawText(
                    split.RectHandle, Qt.AlignCenter,
                    split.text,
                )

                font.setBold(False)
                painter.setFont(font)

        # Numbers
        for pos in range(0, self.bitwidth * self.nrows):

            if pos >= self.registerlength:
                painter.setPen(Qt.red);
            else:
                painter.setPen(Qt.black);

            column, row = self.postoXY(pos)
            row, column = self.translateField(row, column)
            painter.drawText(
                int(column * self.width_bitbox + 9),
                int(row * self.height_bitbox + 17),
                str(pos)
            )

        painter.end()

    def PosToField(self, x, y):
        column = min((x - 2 - self._padding) // self.width_bitbox, self.bitwidth - 1)
        row = min((y - 2 - self._padding) // self.height_bitbox, self.nrows - 1)

        column = max(0, min(column, self.bitwidth - 1))
        row = max(0, min(row, self.nrows - 1))

        row, column = self.translateField(row, column)

        return row, column

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def _trigger_refresh(self):
        self.update()

    # TODO
    def mouseMoveEvent2(self, e):
        return False
        if self.dragging is not None:
            row, column = self.PosToField(e.x(), e.y())

            displacement = int((column - self.draggingOriginColumn) + (row - self.draggingOriginRow) * self.bitwidth)

            start = self.fields[self.dragging][1]
            end = self.fields[self.dragging][2]

            if self.dragMove or self.dragStartHandle:
                start = self.draggingOriginal[1] + displacement
                start = max(0, start)

            if self.dragMove or self.dragEndHandle:
                end = self.draggingOriginal[2] + displacement
                end = max(0, end)

            self.changeFieldData(start, end)
            self.UpdatedData.emit()

        self.update()

    # TODO
    def changeFieldData2(self, start, end):
        return False
        if self.selected is not None:
            self.fields[self.selected][1] = min(start, end)
            self.fields[self.selected][2] = max(start, end)

    # TODO
    def mouseReleaseEvent2(self, e):
        return False
        self.dragging = None
        self.dragMove = False
        self.dragStartHandle = False
        self.dragEndHandle = False
        self.update()

    # TODO
    dragging = None
    draggingOriginRow = None
    draggingOriginColumn = None
    dragMove = False
    dragStartHandle = False
    dragEndHandle = False
    draggingOriginal = None

    # TODO
    def mousePressEvent2(self, e):
        return False
        pos = e.pos()
        self.draggingOriginRow, self.draggingOriginColumn = self.PosToField(pos.x(), pos.y())

        found = False
        for i, rects in self.rectFields.items():
            if found: break
            for rect in rects:
                if rect.contains(pos):
                    name = self.fields[i][0]
                    self.selected = i
                    self.dragging = i
                    self.dragMove = True
                    found = True
                    break

        if not found:
            self.selected = None

        if found:
            # Seach for start and end handle
            found = False
            for i, rect in self.rectStartHandles.items():
                if rect.contains(pos):
                    name = self.fields[i][0]
                    self.selected = i
                    self.dragging = i
                    self.dragMove = False
                    self.dragStartHandle = True
                    found = True
                    break

            if not found:
                for i, rect in self.rectEndHandles.items():
                    if rect.contains(pos):
                        name = self.fields[i][0]
                        self.selected = i
                        self.dragging = i
                        self.dragMove = False
                        self.dragEndHandle = True
                        break

        if self.selected is not None:
            self.draggingOriginal = self.fields[self.selected].copy()

        self.SelectedSignal.emit(self.selected)
        self.update()

    # TODO
    def mouseDoubleClickEvent2(self, e):
        return False
        if self.selected is not None:
            self.DoubleClickField.emit()
        else:
            row, column = self.PosToField(e.x(), e.y())
            pos = int(column + row * self.bitwidth)
            self.newField(pos, pos)
            self.selected = len(self.fields) - 1
            self.SelectedSignal.emit(self.selected)
            self.update()

    # TODO
    def setSelected(self, index):
        return False
        self.selected = index
        self.update()


class RegisterLayoutView(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout()

        self.registerLayout = _RegisterLayout()
#        self.registerLayout.SelectedSignal.connect(self.updateSelected);
#        self.registerLayout.UpdatedData.connect(self.updatedData)

        self.scroll = QtWidgets.QScrollArea()

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.adjustSize()

        self.scroll.setWidget(self.registerLayout)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addWidget(self.scroll)

        viewSettings = QtWidgets.QHBoxLayout()

        byteOrderHorizontalGroup = QtWidgets.QGroupBox("Horizontal Bit Order")
        byteOrderHorizontalLayout = QtWidgets.QVBoxLayout()
        byteOrderHorizontalGroup.setLayout(byteOrderHorizontalLayout)
        self.RadioHorizontalMSB = QtWidgets.QRadioButton("MSB")
        self.RadioHorizontalMSB.clicked.connect(self.updateByteOrder)
        self.RadioHorizontalMSB.setChecked(True)
        self.RadioHorizontalLSB = QtWidgets.QRadioButton("LSB")
        self.RadioHorizontalLSB.clicked.connect(self.updateByteOrder)
        byteOrderHorizontalLayout.addWidget(self.RadioHorizontalMSB)
        byteOrderHorizontalLayout.addWidget(self.RadioHorizontalLSB)
        viewSettings.addWidget(byteOrderHorizontalGroup)

        byteOrderVerticalGroup = QtWidgets.QGroupBox("Vertical Bit Order")
        byteOrderVerticalLayout = QtWidgets.QVBoxLayout()
        byteOrderVerticalGroup.setLayout(byteOrderVerticalLayout)
        self.RadioVerticalMSB = QtWidgets.QRadioButton("MSB")
        self.RadioVerticalMSB.clicked.connect(self.updateByteOrder)
        self.RadioVerticalMSB.setChecked(True)
        self.RadioVerticalLSB = QtWidgets.QRadioButton("LSB")
        self.RadioVerticalLSB.clicked.connect(self.updateByteOrder)
        byteOrderVerticalLayout.addWidget(self.RadioVerticalMSB)
        byteOrderVerticalLayout.addWidget(self.RadioVerticalLSB)
        viewSettings.addWidget(byteOrderVerticalGroup)

        self.updateByteOrder()

        bitwidthGroup = QtWidgets.QGroupBox("Bit Width")
        bitwidthLayout = QtWidgets.QVBoxLayout()
        bitwidthGroup.setLayout(bitwidthLayout)
        self.bitwidthSpin = QtWidgets.QSpinBox()
        self.bitwidthSpin.setMinimumHeight(30)
        self.bitwidthSpin.setMinimum(1)
        self.bitwidthSpin.setValue(8)
#        self.bitwidthSpin.valueChanged.connect(self.updateBitWidth)
        bitwidthLayout.addWidget(self.bitwidthSpin)
        viewSettings.addWidget(bitwidthGroup)
#        self.updateBitWidth()

        leftLayout.addLayout(viewSettings)

        layout.addLayout(leftLayout, 1)  # stretch 1 so it expands

        self.sideBar = QtWidgets.QVBoxLayout()

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self.SaveRequest.emit)
        self.sideBar.addWidget(self.saveButton)

        self.selectedName = QtWidgets.QLineEdit("")
        self.selectedName.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.selectedName.setFont(font)
#        self.selectedName.textChanged.connect(self.updateName)
        self.sideBar.addWidget(self.selectedName)

#        self.registerLayout.DoubleClickField.connect(self.focusName)

        startLabel = QtWidgets.QLabel("Start")
        startLabel.setContentsMargins(0, 10, 0, 0)
        self.sideBar.addWidget(startLabel)
        self.spinStart = QtWidgets.QSpinBox()
        self.spinStart.setEnabled(False)
        self.spinStart.setMinimumSize(QtCore.QSize(0, 40))
        self.spinStart.setMaximum(1000)
#        self.spinStart.valueChanged.connect(self.updateStartData)
        self.sideBar.addWidget(self.spinStart)

        endLabel = QtWidgets.QLabel("End")
        endLabel.setContentsMargins(0, 10, 0, 0)
        self.sideBar.addWidget(endLabel)
        self.spinEnd = QtWidgets.QSpinBox()
        self.spinEnd.setEnabled(False)
        self.spinEnd.setMinimumSize(QtCore.QSize(0, 40))
        self.spinEnd.setMaximum(1000)
#        self.spinEnd.valueChanged.connect(self.updateEndData)
        self.sideBar.addWidget(self.spinEnd)

        widthLabel = QtWidgets.QLabel("Width")
        widthLabel.setContentsMargins(0, 10, 0, 0)
        self.sideBar.addWidget(widthLabel)
        self.spinWidth = QtWidgets.QSpinBox()
        self.spinWidth.setEnabled(False)
        self.spinWidth.setMinimumSize(QtCore.QSize(0, 40))
        self.spinWidth.setMaximum(1000)
#        self.spinWidth.valueChanged.connect(self.updateWidthData)
        self.sideBar.addWidget(self.spinWidth)

        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.sideBar.addSpacerItem(spacer)

        self.fieldlistView = QtWidgets.QListWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.fieldlistView.setSizePolicy(sizePolicy)
#        self.fieldlistView.itemSelectionChanged.connect(self.changedSelected)
#        self.fieldlistView.itemDoubleClicked.connect(self.focusName)
        self.sideBar.addWidget(self.fieldlistView)

        layout.addLayout(self.sideBar)

        self.setLayout(layout)

#        self.updateList()


    SaveRequest = QtCore.pyqtSignal()
    CloseRequest = QtCore.pyqtSignal()

    '''
    def closeEvent(self, event):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        msg.setText("Do you want to save?")
        msg.setWindowTitle("Save")
        msg.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Discard)

        retval = msg.exec_()

        if retval == QtWidgets.QMessageBox.Save:
            self.SaveRequest.emit()
            self.CloseRequest.emit()
            event.accept()
        elif retval == QtWidgets.QMessageBox.Discard:
            self.CloseRequest.emit()
            event.accept()
        elif retval == QtWidgets.QMessageBox.Cancel:
            event.ignore()

    # TODO
    def deleteSelectedField(self):
        self.registerLayout.fields.pop(
            self.registerLayout.selected
        )
        self.registerLayout.selected = None
        self.fieldlistView.clearSelection()
        self.registerLayout.update()
        self.updateList()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Delete:
            self.deleteSelectedField()

    # TODO
    def focusName(self):
        return False
        self.selectedName.setFocus()
        self.selectedName.selectAll()

    # TODO
    def updateName(self):
        return False
        if self.registerLayout.selected is not None:
            self.registerLayout.fields[
                self.registerLayout.selected
            ][0] = self.selectedName.text()
            self.registerLayout.update()
            self.updateList()

    def updateBitWidth(self):
        self.registerLayout.updateBitWidth(self.bitwidthSpin.value())
'''
    def updateByteOrder(self):
        if self.RadioVerticalMSB.isChecked():
            self.registerLayout.VerticalMSB = True
        else:
            self.registerLayout.VerticalMSB = False

        if self.RadioHorizontalMSB.isChecked():
            self.registerLayout.HorizontalMSB = True
        else:
            self.registerLayout.HorizontalMSB = False

        self.registerLayout.update()
    '''
    # TODO
    def updateSelected(self, i):
        return False
        if i is not None:
            self.fieldlistView.setCurrentRow(i)
            self.spinStart.setEnabled(True)
            self.spinEnd.setEnabled(True)
            self.spinWidth.setEnabled(True)
            self.selectedName.setText(self.registerLayout.fields[i][0])
            self.updatedData()
        else:
            self.fieldlistView.clearSelection()
            self.spinStart.setEnabled(False)
            self.spinEnd.setEnabled(False)
            self.spinWidth.setEnabled(False)
            self.selectedName.setText("Select Field")

    # TODO
    def updatedData(self):
        return False
        if self.registerLayout.selected is not None:
            start = self.registerLayout.fields[self.registerLayout.selected][1]
            end = self.registerLayout.fields[self.registerLayout.selected][2]
            self.spinStart.setValue(start)
            self.spinEnd.setValue(end)
            self.spinWidth.setValue(end - start + 1)

    # TODO
    def updateStartData(self):
        return False
        if self.registerLayout.selected is not None:
            self.registerLayout.changeFieldData(
                self.spinStart.value(),
                self.registerLayout.fields[self.registerLayout.selected][2]
            )
            self.updatedData()
            self.registerLayout.update()

    # TODO
    def updateEndData(self):
        return False
        if self.registerLayout.selected is not None:
            self.registerLayout.changeFieldData(
                self.registerLayout.fields[self.registerLayout.selected][1],
                self.spinEnd.value()
            )
            self.updatedData()
            self.registerLayout.update()

    # TODO
    def updateWidthData(self):
        return False
        if self.registerLayout.selected is not None:
            self.spinEnd.setValue(
                self.spinStart.value() + self.spinWidth.value() - 1
            )

    # TODO
    def updateList(self):
        return False
        self.fieldlistView.model().removeRows(0, self.fieldlistView.model().rowCount())
        for field in self.registerLayout.fields:
            self.fieldlistView.addItem(field[0])

        self.updateSelected(self.registerLayout.selected)

    # TODO
    def changedSelected(self):
        return False
        if len(self.fieldlistView.selectedIndexes()):
            i = self.fieldlistView.selectedIndexes()[0].row()
            self.registerLayout.setSelected(i)
            self.updateSelected(i)

    def resizeEvent(self, e):
        self.registerLayout.resize(
            self.scroll.width() - 20,
            self.registerLayout.size().height()
        )

    def __getattr__(self, name):
        if name in self.__dict__:
            return self[name]

        return getattr(self._dial, name)
'''

if __name__ == "__main__":
    from PyQt5 import QtWidgets

    app = QtWidgets.QApplication([])
    exampleView = RegisterLayoutView()
    exampleView.registerLayout.newField(
        "exampleField",
        {
            'bitEnd': 4,
            'bitStart': 15,
            'description': "some bits",
            'readWrite': "R/W",
            'register': "registerA",
            'title': "some Fancy Title",
            'type': "number"
        }
    )

    exampleView.registerLayout.newField(
        "asdf",
        {
            'bitEnd': 17,
            'bitStart': 18,
            'description': "some bits",
            'readWrite': "R/W",
            'register': "registerA",
            'title': "some Fancy Title",
            'type': "number"
        }
    )
    exampleView.show()
    app.exec_()