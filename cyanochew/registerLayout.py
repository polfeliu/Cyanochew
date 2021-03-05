from _tracemalloc import start

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class _RegisterLayout(QtWidgets.QWidget):

    selected = QtCore.pyqtSignal()

    # Key value store of the fields. First item is bitStart, second item is bitEnd
    fields =  [
        ["Field1", 1,2],
        ["Field2", 3,4],
        ["Field3", 6,12],
        ["Field4", 12, 50]
    ]

    overlapping = {}
    selected = None

    # Key of fields with list of splitfields with a list of:
    # #Row, #ColumnStart, #ColumnEnd, #BitStart # BitEnd #StartHandle, #EndHandle, Overlapping
    splitFields = {}

    rectFields = {}
    rectStartHandles = {}
    rectStopHandles = {}

    bitwidth = 8

    nrows = 0

    def calculateOverlapping(self):
        self.overlapping = {}
        for i, field in enumerate(self.fields):
            overlapped = False
            ran = range(field[1], field[2] + 1)
            name = field[0]
            for j, field2 in enumerate(self.fields):
                if i == j: #Same element, ignore and continue searching
                    continue

                # Find if start element or stop element is inside the range
                if field2[1] in ran or field2[2] in ran:
                    overlapped = True
                    break

            self.overlapping[i] = overlapped

    def updateSplitFields(self):
        self.calculateOverlapping()
        self.splitFields = {}

        for i, field in enumerate(self.fields):
            name = field[0]
            columnstart = field[1] % self.bitwidth
            rowstart = field[1] // self.bitwidth

            columnend = field[2] % self.bitwidth
            rowstop = field[2] // self.bitwidth

            row = rowstart
            self.splitFields[i] = []

            bitstart = 0
            bitend = 0

            while row <= rowstop:
                #Not the first row: Expand Left to the start
                if row != rowstart:
                    start = 0
                    LeftHandle = False
                else:
                    start = columnstart
                    LeftHandle = True

                #Not the last row: Expand Right to the end
                if row != rowstop:
                    end = self.bitwidth - 1
                    RightHandle = False
                else:
                    end = columnend
                    RightHandle = True


                width = end - start
                bitend = bitstart + width

                self.splitFields[i].append(
                    [row,start, end, bitstart, bitend, LeftHandle, RightHandle]
                )

                bitstart = bitend + 1

                row = row + 1
                if not self.dragging:
                    self.nrows = max(self.nrows, row)
                    self.resize(
                        self.size().width(),
                        self._padding + self.nrows * self.height_bitbox +2
                    )



    HorizontalMSB = True
    VerticalMSB = True


    #Translate rows and columns of fields according to the MSB settings
    def translateField(self, row, column):
        if self.HorizontalMSB:
            column = self.bitwidth - column - 1

        if self.VerticalMSB:
            row = self.nrows - row - 1

        return row, column

    def postoXY(self, pos):
        return pos%self.bitwidth,pos//self.bitwidth

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        self._padding = 4  # n-pixel gap around edge.


    height_bitbox = 60

    def paintEvent(self, e):
        #For now we will update the split fields every time
        self.updateSplitFields()

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

        self.width_bitbox = d_width/self.bitwidth

        # Grid
        brush.setColor(QtGui.QColor('gray'))

        #Vertical
        for i in range(0, self.bitwidth + 1):
            rect = QtCore.QRect(
                self._padding + i * self.width_bitbox - 1,  # X
                0,  # Y
                2,  # W
                d_height  # H
            )
            painter.fillRect(rect, brush)

        self.rectFields = {}

        #Fields
        for i, splitFields in self.splitFields.items():
            name = self.fields[i][0]
            self.rectFields[i] = []
            for field in splitFields:

                row = field[0]

                columnstart = field[1]
                columnstop = field[2]
                bitstart = field[3]
                bitstop = field[4]
    
                row, x1 = self.translateField(row, columnstart)
                _, x2 = self.translateField(row, columnstop)

                start = min(x1, x2)
                width = abs(x1-x2) + 1

                if self.overlapping[i]: #Overlapping
                    brush.setColor(QtGui.QColor(0xEF, 0x83, 0x54 ,128))
                else:
                    brush.setColor(QtGui.QColor(0xEF, 0x83, 0x54, 255))

                rect = QtCore.QRect(
                           self._padding + start * self.width_bitbox + 2, #X
                           self._padding + row * self.height_bitbox +2,   #Y
                           width*self.width_bitbox - 4,                   #W
                           self.height_bitbox - 4                         #H
                       )

                self.rectFields[i].append(rect)

                painter.fillRect(rect, brush)

                #Handles
                if self.selected == i:
                    brush.setColor(QtGui.QColor(0,0,0))
                else:
                    brush.setColor(QtGui.QColor(70,70,70))

                if self.HorizontalMSB:
                    leftHandle = field[6]
                    rightHandle = field[5]
                else:
                    leftHandle = field[5]
                    rightHandle = field[6]

                if leftHandle:
                    #Draw Left Handle
                    handlerect = QtCore.QRect(
                        self._padding + start*self.width_bitbox + 5,
                        self._padding + row * self.height_bitbox + 17,
                        7,
                        self.height_bitbox - 22
                    )
                    painter.fillRect(handlerect, brush)
                    if not self.HorizontalMSB:
                        self.rectStartHandles[i] = handlerect
                    else:
                        self.rectStopHandles[i] = handlerect

                if rightHandle:

                    #Draw Right Handle
                    handlerect = QtCore.QRect(
                        self._padding + (start + width) * self.width_bitbox - 12,
                        self._padding + row * self.height_bitbox + 17,
                        7,
                        self.height_bitbox - 22
                    )
                    painter.fillRect(handlerect, brush)

                    if self.HorizontalMSB:
                        self.rectStartHandles[i] = handlerect
                    else:
                        self.rectStopHandles[i] = handlerect


                font = painter.font()
                if self.selected == i:
                    font.setBold(True)
                    painter.setFont(font)

                painter.drawText(
                    rect, Qt.AlignCenter,
                    "%s\r\n[%i:%i]" % (name, bitstop, bitstart)
                )

                font.setBold(False)
                painter.setFont(font)

        #Numbers
        for pos in range(0,self.bitwidth*self.nrows):
            column, row = self.postoXY(pos)
            row, column = self.translateField(row, column)
            painter.drawText(
                column * self.width_bitbox+9,
                row * self.height_bitbox + 17,
                str(pos)
            )

        painter.end()


    def PosToField(self, x,y):
        #self.translateField()
        column = min((x - 2 - self._padding) // self.width_bitbox, self.bitwidth - 1)
        row = min((y - 2 - self._padding) // self.height_bitbox, self.nrows - 1)

        column = max(0, min(column, self.bitwidth-1))
        row = max(0, min(row, self.nrows - 1))

        row, column = self.translateField(row, column)

        return row, column

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def _trigger_refresh(self):
        self.update()

    def mouseMoveEvent(self, e):
        if self.dragging is not None:
            row, column = self.PosToField(e.x(), e.y())
            #print(row,column)
            displacement = int((column - self.draggingOriginColumn) + (row - self.draggingOriginRow)*self.bitwidth)

            start = self.fields[self.dragging][1]
            stop = self.fields[self.dragging][2]

            if self.dragMove or self.dragStartHandle:
                start = self.draggingOriginal[1] + displacement

            if self.dragMove or self.dragStopHandle:
                stop = self.draggingOriginal[2] + displacement

            self.fields[self.dragging][1] = min(start,stop)
            self.fields[self.dragging][2] = max(start, stop)

        self.update()

    def mouseReleaseEvent(self, e):
        self.dragging = None
        self.dragMove = False
        self.dragStartHandle = False
        self.dragStopHandle = False
        self.update()

    dragging = None
    draggingOriginRow = None
    draggingOriginColumn = None
    dragMove = False
    dragStartHandle = False
    dragStopHandle = False
    draggingOriginal = None

    def mousePressEvent(self, e):
        pos = e.pos()
        self.draggingOriginRow,self.draggingOriginColumn = self.PosToField(pos.x(), pos.y())
        print(pos)
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
            self.selected=None

        if found:
            #Seach for start and stop handle
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
                for i, rect in self.rectStopHandles.items():
                    if rect.contains(pos):
                        name = self.fields[i][0]
                        self.selected = i
                        self.dragging = i
                        self.dragMove = False
                        self.dragStopHandle = True
                        break

        if self.selected is not None:
            self.draggingOriginal = self.fields[self.selected].copy()

        self.update()



class RegisterLayoutView(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout()

        self.registerLayout = _RegisterLayout()
        self.scroll = QtWidgets.QScrollArea()

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.adjustSize()

        self.scroll.setWidget(self.registerLayout)

        layout.addWidget(self.scroll)

        self.sideBar = QtWidgets.QVBoxLayout()

        self.selectedLabel = QtWidgets.QLabel("Select Field")
        self.selectedLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.selectedLabel.setFont(font)
        self.sideBar.addWidget(self.selectedLabel)

        startLabel = QtWidgets.QLabel("Start")
        startLabel.setContentsMargins(0,10,0,0)
        self.sideBar.addWidget(startLabel)
        self.spinStart = QtWidgets.QSpinBox()
        self.spinStart.setEnabled(False)
        self.spinStart.setMinimumSize(QtCore.QSize(0, 40))
        self.sideBar.addWidget(self.spinStart)

        endLabel = QtWidgets.QLabel("End")
        endLabel.setContentsMargins(0, 10, 0, 0)
        self.sideBar.addWidget(endLabel)
        self.spinEnd = QtWidgets.QSpinBox()
        self.spinEnd.setEnabled(False)
        self.spinEnd.setMinimumSize(QtCore.QSize(0, 40))
        self.sideBar.addWidget(self.spinEnd)

        widthLabel = QtWidgets.QLabel("Width")
        widthLabel.setContentsMargins(0, 10, 0, 0)
        self.sideBar.addWidget(widthLabel)
        self.spinWidth = QtWidgets.QSpinBox()
        self.spinWidth.setEnabled(False)
        self.spinWidth.setMinimumSize(QtCore.QSize(0, 40))
        self.sideBar.addWidget(self.spinWidth)


        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.sideBar.addSpacerItem(spacer)

        self.fieldlistView = QtWidgets.QListWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.fieldlistView.setSizePolicy(sizePolicy)
        self.fieldlistView.itemSelectionChanged.connect(self.asdf)
        self.sideBar.addWidget(self.fieldlistView)

        layout.addLayout(self.sideBar)

        self.setLayout(layout)

        self.updateList()

    def updateList(self):
        #self.fieldlistView.addItems(self.registerLayout.fields)
        pass

    def asdf(self):
        print("dfsaasdfafsd")

    def resizeEvent(self, e):
        self.registerLayout.resize(
            self.scroll.width() - 20,
            self.registerLayout.size().height()
        )

    def __getattr__(self, name):
        if name in self.__dict__:
            return self[name]

        return getattr(self._dial, name)