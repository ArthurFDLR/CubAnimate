
from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon
from PyQt5.QtDataVisualization import (Q3DCamera, Q3DTheme, Q3DScatter,
                                       QAbstract3DGraph, QAbstract3DSeries, QScatter3DSeries,
                                       QScatterDataItem, QScatterDataProxy, QCustom3DItem)

from enum import Enum

class Axis(Enum):
    X = 0
    Y = 1
    Z = 2

class ScatterDataModifier(QtCore.QObject):

    def __init__(self, x : int, y : int, z : int, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, scatter, parent):
        super(ScatterDataModifier, self).__init__()

        self.parent = parent
        self.eraseColor_signal = eraseColor_signal
        self.newColor_signal = newColor_signal
        self.eraseColor_signal.connect(self.eraseColor)
        self.newColor_signal.connect(self.changeColor)

        self.nullColor = QColor(255,255,255)
        self.nullColor.setAlpha(100)

        #Graphics
        self.m_graph = scatter
        self.m_fontSize = 40.0
        

        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)
        self.m_graph.activeTheme().setType(Q3DTheme.ThemeDigia)
        font = self.m_graph.activeTheme().font()
        font.setPointSize(self.m_fontSize)
        self.m_graph.activeTheme().setFont(font)
        self.m_graph.activeTheme().setColorStyle(Q3DTheme.ColorStyleUniform)
        self.m_graph.activeTheme().setSingleHighlightColor(self.nullColor)
        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)

        self.m_graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetIsometricRight)
        self.m_graph.scene().activeCamera().setCameraPosition(300,20)
        self.m_graph.scene().activeCamera().setZoomLevel(150)

        self.m_graph.axisX().setTitle("X")
        self.m_graph.axisX().setSegmentCount(x-1)
        self.m_graph.axisY().setTitle("Y")
        self.m_graph.axisY().setSegmentCount(y-1)
        self.m_graph.axisZ().setTitle("Z")
        self.m_graph.axisZ().setSegmentCount(z-1)

        self.matrixLEDserie = []
        
        
        count = 0
        for i in range(x):
            self.matrixLEDserie.append([])
            for j in range(y):
                self.matrixLEDserie[i].append([])
                for k in range(z):
                    
                    item = QScatterDataItem(QVector3D(i,k,j)) # z-axis and y-axis to match representations, purely graphic

                    self.matrixLEDserie[i][j].append(QScatter3DSeries(QScatterDataProxy()))

                    self.matrixLEDserie[i][j][k].setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
                    self.matrixLEDserie[i][j][k].setMeshSmooth(True)
                    self.matrixLEDserie[i][j][k].setName(str(i) + " " + str(j) + " " + str(k))
                    
                    self.m_graph.addSeries(self.matrixLEDserie[i][j][k])
                    
                    self.m_graph.seriesList()[count].dataProxy().addItem(item)
                    self.m_graph.seriesList()[count].setBaseColor(self.nullColor)
                    self.m_graph.seriesList()[count].setItemSize(1.2/max(x,y,z))
                    
                    count = count+1
        
        self.m_graph.selectedSeriesChanged.connect(self.ledClicked)
    

    def ledClicked(self, serie : QAbstract3DSeries): #Colored the led if not already set to the given color, erase it otherwise
        self.m_graph.clearSelection() #Avoid selected item color shifting
        if serie is not None:
            xStr,yStr,zStr = serie.name().split()
            x = int(xStr)
            y = int(yStr)
            z = int(zStr)
            currentColor = self.getCurrentColor()
            if self.matrixLEDserie[x][y][z].baseColor() == currentColor:
                self.eraseColor_signal.emit(int(xStr), int(yStr), int(zStr))
            else:
                self.newColor_signal.emit(int(xStr), int(yStr), int(zStr), currentColor)
        
    def changeColor(self, posX :int, posY :int, posZ :int, color : QColor):
        print(str(posX) + " " + str(posY) + " " + str(posZ))
        self.matrixLEDserie[posX][posY][posZ].setBaseColor(color)
    
    def eraseColor(self, posX :int, posY :int, posZ :int):
        self.matrixLEDserie[posX][posY][posZ].setBaseColor(self.nullColor)

    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()


class CubeViewer3D(Qtw.QWidget):
    def __init__(self, x : int, y : int, z : int, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
        super(Qtw.QWidget, self).__init__(parent)
        
        self.parent = parent
        self.graph = Q3DScatter()

        self.graph.setAspectRatio(1.0)

        self.currentColor = self.parent.getCurrentColor()

        self.onWidget = False

        self.imageZoom = 180

        self.container = Qtw.QWidget.createWindowContainer(self.graph)

        self.screenSize = self.graph.screen().size()
        self.container.setMinimumSize(QtCore.QSize(self.screenSize.width() /5, self.screenSize.height() / 5))
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.layout = Qtw.QGridLayout(self)
        self.layout.addWidget(self.container, 0,0)

        self.modifier = ScatterDataModifier(x, y, z, newColor_signal, eraseColor_signal, self.graph, self)
    
    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()
    
    def getCurrentFramePixmap(self, size : QtCore.QSize) -> QPixmap :
        zoom = self.graph.scene().activeCamera().zoomLevel()
        self.graph.scene().activeCamera().setZoomLevel(self.imageZoom)
        image = self.graph.renderToImage(2,size)
        self.graph.scene().activeCamera().setZoomLevel(zoom)
        return QPixmap.fromImage(image)


class CubeLEDFrame_DATA:
    def __init__(self, sizeX :int, sizeY :int, sizeZ :int):
        
        self.cubeSize = {}
        self.cubeSize[Axis.X] = sizeX
        self.cubeSize[Axis.Y] = sizeY
        self.cubeSize[Axis.Z] = sizeZ

        self.nullColor = QColor(255,255,255)

        self.LEDcolors = []
        for i in range(self.cubeSize[Axis.X]):
            self.LEDcolors.append([])
            for j in range(self.cubeSize[Axis.Y]):
                self.LEDcolors[i].append([])
                for k in range(self.cubeSize[Axis.Z]):
                    self.LEDcolors[i][j].append(self.nullColor)
    
    #@pyqtSlot(int, int, int, QColor)
    def setColorLED(self, x :int, y :int, z :int, color : QColor):
        if x<self.cubeSize[Axis.X] and y<self.cubeSize[Axis.Y] and z<self.cubeSize[Axis.Z]:
            self.LEDcolors[x][y][z] = color
        else:
            print("No matching LED")
    
    #@pyqtSlot(int, int, int)
    def eraseColorLED(self, x :int, y :int, z :int):
        if x<self.cubeSize[Axis.X] and y<self.cubeSize[Axis.Y] and z<self.cubeSize[Axis.Z]:
            self.LEDcolors[x][y][z] = self.nullColor
        else:
            print("No matching LED")
    
    def getColorLED(self, x :int, y :int, z :int) -> QColor:
        if x<self.cubeSize[Axis.X] and y<self.cubeSize[Axis.Y] and z<self.cubeSize[Axis.Z]:
            return self.LEDcolors[x][y][z]
        else:
            print("No matching LED")
            return self.nullColor
    
    def getColorLED_HEX(self, x :int, y :int, z :int) -> str:
        if x<self.cubeSize[Axis.X] and y<self.cubeSize[Axis.Y] and z<self.cubeSize[Axis.Z]:
            return self.LEDcolors[x][y][z].name()
        else:
            print("No matching LED")
            return self.nullColor.name()
    
    def getSizeX(self) -> int:
        return self.cubeSize[Axis.X]
    
    def getSizeY(self) -> int:
        return self.cubeSize[Axis.Y]
    
    def getSizeZ(self) -> int:
        return self.cubeSize[Axis.Z]


class QColorDialog_noESC(Qtw.QColorDialog):
    """ QColorDialog that cannot be closed (especially through ESC-key)."""
    def __init__(self, parent=None):
        super(Qtw.QColorDialog, self).__init__(parent)
    def reject(self): 
        pass


class ColorPicker(Qtw.QGroupBox):
    """ Turn a QColorDialog in a permanent QWidget displayable."""

    def __init__(self, parent=None):
        super(Qtw.QGroupBox, self).__init__("Color picker", parent)

        policy = Qtw.QSizePolicy(Qtw.QSizePolicy.Minimum, Qtw.QSizePolicy.Minimum)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

        self.layout=Qtw.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.colorDialog = QColorDialog_noESC(self)
        self.colorDialog.setWindowFlags(QtCore.Qt.Widget)
        self.colorDialog.setOptions(Qtw.QColorDialog.DontUseNativeDialog | Qtw.QColorDialog.NoButtons)
        self.layout.addWidget(self.colorDialog)


    def getColor(self) -> QColor:
        """
        Returns:
            QColor: Currently selected color.
        """
        color = self.colorDialog.currentColor()
        if color.isValid():
            return color
        else:
            return QColor(255,255,255) #White


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
        super(Qtw.QPushButton, self).__init__(parent)
        self._parent = parent

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
        self.styleStr = "background-color: {}; border: 0px"
        policy = Qtw.QSizePolicy(Qtw.QSizePolicy.Preferred, Qtw.QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

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
        self.LEDcolor = self._parent.getCurrentColor()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            #Write new color
            self.newColor_signal.emit(self.x, self.y, self.z, self._parent.getCurrentColor())
        elif ev.button() == QtCore.Qt.RightButton:
            #Erase LED
            self.eraseColor_signal.emit(self.x, self.y, self.z)
    
    def changeColor(self, posX :int, posY :int, posZ :int, color : QColor):
        if posX == self.x and posY == self.y and posZ == self.z:
            self.LEDcolor = color
            self.setStyleSheet(self.styleStr.format(self.LEDcolor.name()))
    
    def eraseColor(self, posX :int, posY :int, posZ :int):
        if posX == self.x and posY == self.y and posZ == self.z:
            self.LEDcolor = self.nullColor
            self.setStyleSheet(self.styleStr.format(self.LEDcolor.name()))


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
        self.nbrColumn = cubeSize[columnAxis]
        self.nbrRow = cubeSize[rowAxis]

        self.aspectRatio = self.nbrRow/self.nbrColumn

        self.styleStr = "background-color: {}; border: 0px"
        policy = Qtw.QSizePolicy(Qtw.QSizePolicy.Preferred, Qtw.QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

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
        

    def resizeEvent(self, event):
        #self.aspectRatio = nbrRow
        self.spacerRatioInvert = 60

        h = event.size().height()
        w = event.size().width()
        if w > self.aspectRatio*h:
            w = int(self.aspectRatio*h)
        else:
            h = int(w/self.aspectRatio)
        self.resize(w, h)
        #self.layout.setSpacing(max(w,h)/self.spacerRatioInvert)
        self.layout.setSpacing(4)


    def getCurrentColor(self) -> QColor :
        return self._parent.getCurrentColor()
    

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

        self.layersWidget = Qtw.QWidget(self)
        self.layout=Qtw.QHBoxLayout(self)
        self.layersWidget.setLayout(self.layout)
        self.layout.setSpacing(10)

        self.ledLayers = []

        for i in range(self._parent.cubeSize[slicingAxis]):
            self.ledLayers.append(CubeLayerView(self._parent.cubeSize, i, 
                                                columnAxis, rowAxis, slicingAxis,
                                                newColor_signal, eraseColor_signal, self))
            self.layout.addWidget(self.ledLayers[i])
        
        self.setWidget(self.layersWidget)
        self.setWidgetResizable(True)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMaximumHeight(400)
    
    def resizeEvent(self, event):
        self.setMinimumHeight(self.ledLayers[0].height()*1.2)
        self.setMaximumHeight(400)
    
    def getCurrentColor(self) -> QColor :
        return self._parent.getCurrentColor()


class CubeFullView(Qtw.QTabWidget):
    """ 3 tabs containing a representation of the cube sliced along each axis.
    
    Attributes:
        cubeSize (dict[Axis,int]): Number of LEDs along each axis of the cube.
    """

    def __init__(self, x : int, y : int, z : int, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
        """
        Args:
            x, y, z (int)): Number of LEDs along each axis.
            parent (QWidget): Need a method getCurrentColor()->QColor.
        """
        super(Qtw.QTabWidget, self).__init__(parent)
        self._parent = parent

        self.newColor_signal = newColor_signal
        self.eraseColor_signal = eraseColor_signal

        self.cubeSize = {}
        self.createTabs(x,y,z)
    
    def getCurrentColor(self) -> QColor :
        return self._parent.getCurrentColor()
    
    def erase(self):
        """Clean up all widgets and tabs."""
        self.cube_BottomView.setParent(None)
        self.cube_LeftView.setParent(None)
        self.cube_BackView.setParent(None)
        self.clear()
    
    def createTabs(self, x,y,z):
        """Creates three representations along each axis in different tabs.

        Args:
            x, y, z (int)): Number of LEDs along each axis.
        """
        self.cubeSize[Axis.X] = x
        self.cubeSize[Axis.Y] = y
        self.cubeSize[Axis.Z] = z

        self.cube_BottomView = Cube3DView(Axis.X, Axis.Y, Axis.Z, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_LeftView = Cube3DView(Axis.Z, Axis.X, Axis.Y, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_BackView = Cube3DView(Axis.Z, Axis.Y, Axis.X, self.newColor_signal, self.eraseColor_signal, self)
        
        self.addTab(self.cube_BackView, "Back to front")
        self.addTab(self.cube_LeftView, "Left to right")
        self.addTab(self.cube_BottomView, "Bottom to top")
    
    def changeSize(self, x,y,z):
        """Change sizes of the cube."""
        self.erase()
        self.createTabs(x,y,z)


class FrameCreator(Qtw.QWidget):
        
    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self._parent = parent

        self.frame = CubeLEDFrame_DATA(8,8,8)

        self.layout=Qtw.QGridLayout(self)
        self.setLayout(self.layout)

        self.colorPicker = ColorPicker(self)
        self.layout.addWidget(self.colorPicker,0,0)

        self.view = CubeViewer3D(self.frame.getSizeX(),self.frame.getSizeY(),self.frame.getSizeZ(), self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.view,0,1)
        
        self.cube = CubeFullView(self.frame.getSizeX(),self.frame.getSizeY(),self.frame.getSizeZ(), self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cube,1,0,1,3)

        self.newColorLED_signal.connect(self.frame.setColorLED)
        self.eraseColorLED_signal.connect(self.frame.eraseColorLED)

        #self.upperRightSpacer = Qtw.QSpacerItem(20, 40, Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Minimum)
        #self.layout.addItem(self.upperRightSpacer,0,2)

        self.image = Qtw.QLabel()
        self.layout.addWidget(self.image,0,2)
        self.image.setPixmap(self.view.getCurrentFramePixmap(QtCore.QSize(200,200)))
    
    def getCurrentColor(self) -> QColor :
        return self.colorPicker.getColor()


class CubeLEDFrame(Qtw.QListWidgetItem):
    def __init__(self, parentList):
        super(Qtw.QListWidgetItem, self).__init__(None,parentList)


class AnimationList(Qtw.QWidget):
    def __init__(self, icon : QIcon, parent=None):
        super(Qtw.QWidget, self).__init__(parent)

        self.widget_layout = Qtw.QVBoxLayout()

        # Create ListWidget and add 10 items to move around.
        self.list_widget = Qtw.QListWidget()
        self.list_widget.setFlow(Qtw.QListView.LeftToRight)
        #self.list_widget.setViewMode(Qtw.QListView.IconMode)

        for x in range(1, 10):
            self.list_widget.addItem(Qtw.QListWidgetItem("hey {}".format(x)))
    
        itm2 = Qtw.QListWidgetItem(icon, "name", self.list_widget )
        itm1 = Qtw.QListWidgetItem(None, self.list_widget)
        itm1.setSizeHint(QtCore.QSize(200,200))
        #self.list_widget.addItem(itm1)
        #self.list_widget.addItem(itm2)
        self.list_widget.setItemWidget(itm1, Qtw.QPushButton("Hello there!"))

        # Enable drag & drop ordering of items.
        self.list_widget.setDragDropMode(Qtw.QAbstractItemView.InternalMove)

        self.widget_layout.addWidget(self.list_widget)
        self.setLayout(self.widget_layout)



class Animator(Qtw.QWidget):
    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self._parent = parent

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.frameCreator = FrameCreator(self)
        self.mainLayout.addWidget(self.frameCreator,0,0)

        self.anim = AnimationList(QIcon(self.frameCreator.view.getCurrentFramePixmap(QtCore.QSize(200,200))), self)
        self.mainLayout.addWidget(self.anim,1,0)
    


    
class MainWindow(Qtw.QWidget):
    def __init__(self):
        super().__init__()
        

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.animator = Animator(self)
        self.mainLayout.addWidget(self.animator,0,0)

        #SPACERS
        self.lowSpacer = Qtw.QSpacerItem(20, 40, Qtw.QSizePolicy.Minimum, Qtw.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.lowSpacer,1,0)

