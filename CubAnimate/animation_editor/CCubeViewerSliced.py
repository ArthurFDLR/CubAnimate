from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor

from ..common.CTypes import CubeSize, Axis


stylesheet = """
QLineEdit, QLabel, QTabWidget {
    font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif;
}
QTabWidget {
    border-radius: 3px;
}
QTabWidget::pane {
    border-radius: 3px;
}
QTabBar::tab {
    padding: 3px 6px;
    color: rgb(100, 100, 100);
    background: white;
    border-radius: 2px;
}
QTabBar::tab:hover {
    color: black;
}
QTabBar::tab:selected {
    color: rgb(139, 173, 228);
    border-bottom: 2px solid rgb(139, 173, 228);
}
QTabBar::tab:!selected {
    border-bottom: 2px solid transparent;
    background : rgb(235,235,235)
}
QScrollBar:horizontal {
    max-height: 10px;
    border: none;
    margin: 0px 0px 0px 0px;
}
QScrollBar:vertical {
    max-width: 10px;
    border: none;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle {
    background: rgb(220, 220, 220);
    border: 1px solid rgb(207, 207, 207);
    border-radius: 5px;
}
QPushButton {
    border: 1px solid rgb(200,200,200);
    border-radius: 10px;
}

QScrollArea {
    border : none;
    border-radius: 3px;
}
"""

class LEDbutton(Qtw.QPushButton):
    """Representation of an LED, get the color given by the parent when clicked.
    
    Attributes:
        x, y, z (int): Position of the LED in the cube
        LEDcolor (QColor): current color of the LED associated.
        nullColor (QColor): Color displayed when an LED is erased.
    """

    def __init__(self, coordinates, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
        """
        Args:
            coordinates (dict[Axis,int]): Position of the LED associated in the cube.
            newColor_signal, eraseColor_signal (pyqtSignal): Signal emited when an LED color is changed or erased.
            parent (QWidget): Need a method getCurrentColor()->QColor.
        """
        super(Qtw.QPushButton, self).__init__(parent, cursor=QtCore.Qt.PointingHandCursor, toolTip='({},{},{})'.format(coordinates[Axis.X], coordinates[Axis.Y], coordinates[Axis.Z]))
        self.parent = parent

        self.effect = Qtw.QGraphicsDropShadowEffect(self)
        self.effect.setBlurRadius(1)
        self.effect.setOffset(0, 0)
        self.effect.setColor(QtCore.Qt.gray)
        self.setGraphicsEffect(self.effect)


        self.eraseColor_signal = eraseColor_signal
        self.newColor_signal = newColor_signal
        self.eraseColor_signal.connect(self.eraseColor)
        self.newColor_signal.connect(self.changeColor)

        self.nullColor = QColor(255,255,255)

        self.x = coordinates[Axis.X]
        self.y = coordinates[Axis.Y]
        self.z = coordinates[Axis.Z]
        self.LEDcolor = QColor(255,255,255) #White

        self.setMinimumSize(20,20)
        self.aspectRatio = 1.0
        self.styleStr = "background-color: {}"

        self.setStyleSheet(self.styleStr.format(self.LEDcolor.name()))

        
    def resizeEvent(self, event):
        h = event.size().height()
        w = event.size().width()
        if w > self.aspectRatio*h:
            w = int(self.aspectRatio*h)
        else:
            h = int(w/self.aspectRatio)
        self.resize(w, h)
    
    def updateCurrentColor(self):
        self.LEDcolor = self.parent.getCurrentColor()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            newColor = self.parent.getCurrentColor()
            if newColor == self.LEDcolor:
                self.eraseColor_signal.emit(self.x, self.y, self.z)
            else:
                self.newColor_signal.emit(self.x, self.y, self.z, self.parent.getCurrentColor()) #Write new color
            
        elif ev.button() == QtCore.Qt.RightButton:
            #Erase LED
            self.eraseColor_signal.emit(self.x, self.y, self.z)
            self.effect.setBlurRadius(1)
    
    def changeColor(self, posX :int, posY :int, posZ :int, color : QColor):
        if posX == self.x and posY == self.y and posZ == self.z:
            self.LEDcolor = color
            self.setStyleSheet(self.styleStr.format(self.LEDcolor.name()))
            self.effect.setBlurRadius(20)
            self.effect.setColor(self.LEDcolor)
    
    def eraseColor(self, posX :int, posY :int, posZ :int):
        if posX == self.x and posY == self.y and posZ == self.z:
            self.LEDcolor = self.nullColor
            self.setStyleSheet(self.styleStr.format(self.LEDcolor.name()))
            self.effect.setBlurRadius(1)




class CubeLayerView(Qtw.QWidget):
    """ One layer of a cube.

    Attributes:
        nbrColumn, nbrRow (int): Number of row and column of LEDs.
        matrixLED (list[[LEDbutton]]): Store the representation of the LEDs in the layer.
    """


    def __init__(self, cubeSize, layerID, 
                 columnAxis : Axis, rowAxis : Axis, normalAxis : Axis, 
                 newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal,
                 parent):
        """
        Args:
            cubeSize (dict[Axis,int]): Number of LEDs in the cube along each axis.
            columnAxis, rowAxis, normalAxis (Axis): Axis associated to each direction to match nominal representation.
            layerID (int): Position of the layer along the slicing axis.
            newColor_signal, eraseColor_signal (pyqtSignal): Signal emited when an LED color is changed or erased.
            parent (QWidget): Need a method getCurrentColor()->QColor.
        """
        super(Qtw.QWidget, self).__init__(parent)
        self._parent = parent
        self.nbrColumn = cubeSize.getSize(columnAxis)
        self.nbrRow = cubeSize.getSize(rowAxis)

        self.aspectRatio = self.nbrRow/self.nbrColumn

        self.layout=Qtw.QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(4)

        self.matrixLED = []
        self.LEDcoordinate = {}
        self.LEDcoordinate[Axis.X] = 0
        self.LEDcoordinate[Axis.Y] = 0
        self.LEDcoordinate[Axis.Z] = 0
        self.LEDcoordinate[normalAxis] = layerID

        for i in range(self.nbrColumn):
            self.matrixLED.append([])
            
            if columnAxis == Axis.X: # To set bottom on the last layer 
                self.LEDcoordinate[columnAxis] = i
            else:
                self.LEDcoordinate[columnAxis] = self.nbrColumn - 1 - i

            for j in range(self.nbrRow):
                self.LEDcoordinate[rowAxis] = j

                self.matrixLED[i].append(LEDbutton(self.LEDcoordinate, newColor_signal, eraseColor_signal, self))
                self.layout.addWidget(self.matrixLED[i][j],i,j)

    def getCurrentColor(self) -> QColor :
        return self._parent.getCurrentColor()

    def resizeEvent(self, event):
        h = event.size().height()
        w = event.size().width()
        if w > self.aspectRatio*h:
            w = int(self.aspectRatio*h)
        else:
            h = int(w/self.aspectRatio)
        self.resize(w, h)




class Cube3DView(Qtw.QScrollArea):
    """ Representation of the cube sliced along a given axis."""

    def __init__(self, columnAxis : Axis, rowAxis : Axis, slicingAxis : Axis, 
                 newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, 
                 parent):
        """
        Args:
            columnAxis, rowAxis, slicingAxis (Axis): Axis associated to each direction to match nominal representation.
            newColor_signal, eraseColor_signal (pyqtSignal): Signal emited when an LED color is changed or erased.
            parent (QWidget): Need a method getCurrentColor()->QColor and attribute cubeSize (dict[Axis,int])
        """

        super(Qtw.QScrollArea, self).__init__(parent)
        self._parent = parent
        self.setObjectName('Custom_Slice_View')
        self.setStyleSheet("#Custom_Slice_View {background: white}")

        
        self.layersWidget = Qtw.QWidget(self)
        self.layersWidget.setObjectName('Custom_Slice_View_In')
        self.layersWidget.setStyleSheet("#Custom_Slice_View_In {background: white}")
        self.layout=Qtw.QHBoxLayout(self)
        self.layersWidget.setLayout(self.layout)
        self.layout.setSpacing(0)

        self.layout.setContentsMargins(1, 1, 1, 1)

        self.ledLayers = []

        for i in range(self._parent.cubeSize.getSize(slicingAxis)):
            self.ledLayers.append(CubeLayerView(self._parent.cubeSize, i, 
                                                columnAxis, rowAxis, slicingAxis,
                                                newColor_signal, eraseColor_signal, self))
            self.layout.addWidget(self.ledLayers[i])
        
        self.setWidget(self.layersWidget)
    
    def resizeEvent(self, event):
        screenHeight = self.screen().size().height()
        layerHeight = self.ledLayers[0].height()
        layerWidth = self.ledLayers[0].width()
        if screenHeight * 0.2 > layerHeight:
            self.setMinimumHeight(layerHeight*1.1)
        self.layersWidget.setMaximumWidth(layerWidth*len(self.ledLayers)*1.05)
        
        for layer in self.ledLayers: # Update scroll bar
            layer.updateGeometry()
    
    def getCurrentColor(self) -> QColor :
        return self._parent.getCurrentColor()



class CCubeViewerSliced(Qtw.QWidget):
    """ 3 tabs containing a representation of the cube sliced along each axis.
    
    Attributes:
        cubeSize (CubeSize)): Number of LEDs along each axis.
    """

    def __init__(self, cubeSize:CubeSize, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
        """
        Args:
            cubeSize (CubeSize)): Number of LEDs along each axis.
            newColor_signal (QtCore.pyqtSignal(int,int,int,QColor)): Signal sended when the led at the given position has a new color.
            eraseColor_signal (QtCore.pyqtSignal(int,int,int)): Signal sended when the led at the given position is erased.
            parent (QWidget): Need a method getCurrentColor()->QColor.
        """
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.setObjectName('Custom_CubeSliced_Window')
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(stylesheet)

        layout = Qtw.QVBoxLayout(self)
        self.colorView = Qtw.QWidget(self)
        self.colorView.setObjectName('Custom_CubeSliced_View')
        layout.addWidget(self.colorView)

        layout = Qtw.QVBoxLayout(self.colorView)
        layout.setContentsMargins(1, 1, 1, 1)

        self.tabWidget = Qtw.QTabWidget()
        layout.addWidget(self.tabWidget)

        self.newColor_signal = newColor_signal
        self.eraseColor_signal = eraseColor_signal

        self.cubeSize = cubeSize
        self.createTabs(self.cubeSize)
        
        effect = Qtw.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setOffset(0, 0)
        effect.setColor(QtCore.Qt.gray)
        self.setGraphicsEffect(effect)
        
    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()
    
    def erase(self):
        """Clean up all widgets and tabs."""
        self.cube_BottomView.setParent(None)
        self.cube_LeftView.setParent(None)
        self.cube_BackView.setParent(None)
        self.tabWidget.clear()
    
    def createTabs(self, cubeSize : CubeSize):
        """Creates three representations along each axis in different tabs.

        Args:
            cubeSize (CubeSize)): Number of LEDs along each axis.
        """
        self.cubeSize = cubeSize

        self.cube_BottomView = Cube3DView(Axis.X, Axis.Y, Axis.Z, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_LeftView = Cube3DView(Axis.Z, Axis.X, Axis.Y, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_BackView = Cube3DView(Axis.Z, Axis.Y, Axis.X, self.newColor_signal, self.eraseColor_signal, self)
        
        self.tabWidget.addTab(self.cube_BackView, "Back to front")
        self.tabWidget.addTab(self.cube_LeftView, "Left to right")
        self.tabWidget.addTab(self.cube_BottomView, "Bottom to top")
    
    def changeCubeSize(self, cubeSize:CubeSize):
        """Change sizes of the cube."""
        self.erase()
        self.createTabs(cubeSize)
    