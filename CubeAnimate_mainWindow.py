
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



class CubeSize:
    def __init__(self, x: int = 0, y: int = 0, z: int = 0):
        self.size = {}
        self.size[Axis.X] = max(0,x)
        self.size[Axis.Y] = max(0,y)
        self.size[Axis.Z] = max(0,z)
    
    def getSize(self, axis : Axis) -> int:
        return self.size[axis]

    def setSize(self, axis : Axis, size : int):
        self.size[axis] = max(0,size)
    
    def pointDefined(self, x:int, y:int, z:int) -> bool:
        return x < self.size[Axis.X] and y < self.size[Axis.Y] and z < self.size[Axis.Z]



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
    def __init__(self, size : CubeSize, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
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

        self.modifier = ScatterDataModifier(size.getSize(Axis.X), size.getSize(Axis.Y), size.getSize(Axis.Z), newColor_signal, eraseColor_signal, self.graph, self)
    
    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()
    
    def getCurrentFramePixmap(self, size : QtCore.QSize) -> QPixmap :

        xRot = self.graph.scene().activeCamera().xRotation()
        yRot = self.graph.scene().activeCamera().yRotation()
        zoom = self.graph.scene().activeCamera().zoomLevel()
        self.graph.scene().activeCamera().setCameraPosition(300,20)
        self.graph.scene().activeCamera().setZoomLevel(self.imageZoom)

        image = self.graph.renderToImage(2,size)

        self.graph.scene().activeCamera().setCameraPosition(xRot,yRot)
        self.graph.scene().activeCamera().setZoomLevel(zoom)

        return QPixmap.fromImage(image)



class CubeLEDFrame_DATA:
    def __init__(self, cubeSize:CubeSize):
        
        self.cubeSize = cubeSize

        self.nullColor = QColor(255,255,255)

        self.LEDcolors = []
        for i in range(self.cubeSize.getSize(Axis.X)):
            self.LEDcolors.append([])
            for j in range(self.cubeSize.getSize(Axis.Y)):
                self.LEDcolors[i].append([])
                for k in range(self.cubeSize.getSize(Axis.Z)):
                    self.LEDcolors[i][j].append(self.nullColor)
    
    def setColorLED(self, x:int, y:int, z:int, color : QColor):
        if self.cubeSize.pointDefined(x,y,z):
            self.LEDcolors[x][y][z] = color
        else:
            print("No matching LED")
    
    def eraseColorLED(self, x:int, y :int, z :int):
        if self.cubeSize.pointDefined(x,y,z):
            self.LEDcolors[x][y][z] = self.nullColor
        else:
            print("No matching LED")
    
    def getColorLED(self, x :int, y :int, z :int) -> QColor:
        if self.cubeSize.pointDefined(x,y,z):
            return self.LEDcolors[x][y][z]
        else:
            print("No matching LED")
            return self.nullColor
    
    def getColorLED_HEX(self, x :int, y :int, z :int) -> str:
        if self.cubeSize.pointDefined(x,y,z):
            return self.LEDcolors[x][y][z].name()
        else:
            print("No matching LED")
            return self.nullColor.name()
    
    def getSize(self) -> CubeSize:
        return self.cubeSize
    
    def getSizeAxis(self, axis : Axis) -> int:
        return self.cubeSize.getSize(axis)



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
        self.nbrColumn = cubeSize.getSize(columnAxis)
        self.nbrRow = cubeSize.getSize(rowAxis)

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

        for i in range(self._parent.cubeSize.getSize(slicingAxis)):
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
        super(Qtw.QTabWidget, self).__init__(parent)
        self.parent = parent

        self.newColor_signal = newColor_signal
        self.eraseColor_signal = eraseColor_signal

        self.cubeSize = cubeSize
        self.createTabs(self.cubeSize)
    
    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()
    
    def erase(self):
        """Clean up all widgets and tabs."""
        self.cube_BottomView.setParent(None)
        self.cube_LeftView.setParent(None)
        self.cube_BackView.setParent(None)
        self.clear()
    
    def createTabs(self, cubeSize : CubeSize):
        """Creates three representations along each axis in different tabs.

        Args:
            cubeSize (CubeSize)): Number of LEDs along each axis.
        """
        self.cubeSize = cubeSize

        self.cube_BottomView = Cube3DView(Axis.X, Axis.Y, Axis.Z, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_LeftView = Cube3DView(Axis.Z, Axis.X, Axis.Y, self.newColor_signal, self.eraseColor_signal, self)
        self.cube_BackView = Cube3DView(Axis.Z, Axis.Y, Axis.X, self.newColor_signal, self.eraseColor_signal, self)
        
        self.addTab(self.cube_BackView, "Back to front")
        self.addTab(self.cube_LeftView, "Left to right")
        self.addTab(self.cube_BottomView, "Bottom to top")
    
    def changeSize(self, cubeSize:CubeSize):
        """Change sizes of the cube."""
        self.erase()
        self.createTabs(cubeSize)



class FrameCreator(Qtw.QWidget):
    """ Widget alowing the user to modify the currently selected frame.
    
    Attributes:
        frame (CubeLEDFrame_DATA): Currently modified frame.
        cubeSize (CubeSize): Number of LEDs along each axis.
        colorPicker (ColorPicker): Widget to select the painting color.
        cubeViewer (CubeViewer3D): Widget showing the cube in 3D.
        cubeSliced (CubeFullView): Widget showing the sliced cube.
        newColor_signal (QtCore.pyqtSignal(int,int,int,QColor)): Signal sended when the led at the given position has a new color.
        eraseColor_signal (QtCore.pyqtSignal(int,int,int)): Signal sended when the led at the given position is erased.
    """
    
    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self, frame : CubeLEDFrame_DATA, cubeSize : CubeSize, parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.frame = frame
        self.cubeSize = cubeSize

        self.layout=Qtw.QGridLayout(self)
        self.setLayout(self.layout)

        self.colorPicker = ColorPicker(self)
        self.layout.addWidget(self.colorPicker,0,0)

        self.cubeViewer = CubeViewer3D(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cubeViewer,0,1)
        
        self.cubeSliced = CubeFullView(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cubeSliced,1,0,1,3)

        self.newColorLED_signal.connect(self.frame.setColorLED)
        self.eraseColorLED_signal.connect(self.frame.eraseColorLED)

    
    def getCurrentColor(self) -> QColor :
        return self.colorPicker.getColor()
    
    def changeCurrentFrame(self, newFrameData : CubeLEDFrame_DATA):
        """ Change the modified frame."""
        size = newFrameData.getSize()
        if self.frame.getSize() == size:
            self.frame
            self.newColorLED_signal.disconnect(self.frame.setColorLED)
            self.eraseColorLED_signal.disconnect(self.frame.eraseColorLED)

            for x in range(size.getSize(Axis.X)):
                for y in range(size.getSize(Axis.Y)):
                    for z in range(size.getSize(Axis.Z)):
                        newColor = newFrameData.getColorLED(x,y,z)
                        if self.frame.getColorLED(x,y,z) != newColor:  #Great gain in refresh speed if the frames are similare
                            self.newColorLED_signal.emit(x,y,z, newColor)

            self.frame = newFrameData

            self.newColorLED_signal.connect(self.frame.setColorLED)
            self.eraseColorLED_signal.connect(self.frame.eraseColorLED)
        else:
            print("Cube size incompatibility")



class CubeLEDFrame(Qtw.QListWidgetItem):
    """ Item to use in an AnimationList object. Represent a frame in the timeline.
    
    Attributes:
        name (str): Name of the frame.
        frameDate (CubeLEDFrame_DATA): Currently modified frame.
        cubeSize (CubeSize): Number of LEDs along each axis.
        illustration (QLabel): Consist of a representation (QPixmap) of the frame associated.
    """

    def __init__(self, name : str, cubeSize:CubeSize, parentList, parent):
        super(Qtw.QListWidgetItem, self).__init__(None,parentList)
        self.parentList = parentList
        self.parent = parent
        self.name = name
        
        self.frameData = CubeLEDFrame_DATA(cubeSize)
        self.setSizeHint(QtCore.QSize(200,200))
 
        self.frame =  Qtw.QGroupBox(self.name)
        self.layout = Qtw.QVBoxLayout()
        self.frame.setLayout(self.layout)

        self.illustration = Qtw.QLabel()
        self.layout.addWidget(self.illustration)

        self.parentList.setItemWidget(self,self.frame)
    
    def setIllustration(self, image : QPixmap):
        self.illustration.setPixmap(image) 

    def getFrameData(self) -> CubeLEDFrame_DATA:
        return self.frameData


class SquarePushButton(Qtw.QPushButton):
    def __init__(self, label:str, parent):
        super(Qtw.QPushButton, self).__init__(label, parent)
        self.parent = parent
        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)

    def resizeEvent(self, event):
        aspectRatio = 1.0
        h = self.parent.size().height()
        w = int(aspectRatio*h)
        self.setMinimumSize(QtCore.QSize(h,w))
        self.resize(w, h)


class AnimationList(Qtw.QWidget):
    """ Widget allowing the user to create a new frame, select the currently modified frame and reorganize them.
    
    Attributes:
        frameList (List[CubeLEDFrame]): Store all frames of the animation.
    """
    def __init__(self, cubeSize:CubeSize,parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.layout = Qtw.QHBoxLayout()
        self.setLayout(self.layout)

        self.timeLine = Qtw.QListWidget()

        self.timeLine.setFlow(Qtw.QListView.LeftToRight)
        self.timeLine.setDragDropMode(Qtw.QAbstractItemView.InternalMove)
        self.layout.addWidget(self.timeLine)
        self.layout.setStretchFactor(self.timeLine,1)

        self.addFrameButton = SquarePushButton("Add frame !", self)
        self.layout.addWidget(self.addFrameButton)

        self.frameList = [] #Store all frames
    
    def changeFrameSelected(self, frame : CubeLEDFrame):
        self.timeLine.setCurrentItem(frame)



class Animator(Qtw.QWidget):
    """ Main widget allowing the user to create animations.
    
    Attributes:
        cubeSize (CubeSize)): Number of LEDs along each axis.
        blankIllustration (QPixmap): Default illustration to use when a new frame is created.
    """
    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = CubeSize(8,16,8)

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.animationViewer = AnimationList(self.cubeSize, self)
        
        self.currentSelectedFrame = self.addFrame()
        
        self.frameCreator = FrameCreator(self.currentSelectedFrame.getFrameData(), self.cubeSize, self)
        self.blankIllustration = self.getCurrentCubePixmap()
        self.animationViewer.frameList[0].setIllustration(self.blankIllustration)
        
        self.mainLayout.addWidget(self.frameCreator,0,0)
        self.mainLayout.addWidget(self.animationViewer,1,0)

        self.animationViewer.addFrameButton.clicked.connect(self.addFrame)
        self.animationViewer.timeLine.itemSelectionChanged.connect(self.changeCurrentFrame)
    
    def getCurrentCubePixmap(self) -> QPixmap:
        return self.frameCreator.cubeViewer.getCurrentFramePixmap(QtCore.QSize(200,200))
    
    def changeCurrentFrame(self):
        print(self.animationViewer.timeLine.currentRow())

        selectionList = self.animationViewer.timeLine.selectedItems()
        self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap()) #Update illustration of the leaved frame
        self.currentSelectedFrame = selectionList[0]
        self.frameCreator.changeCurrentFrame(self.currentSelectedFrame.getFrameData())
    
    def addFrame(self):
        num = len(self.animationViewer.frameList)
        self.animationViewer.frameList.append(CubeLEDFrame('#{}'.format(num+1), self.cubeSize, self.animationViewer.timeLine, self.animationViewer))
        self.animationViewer.changeFrameSelected(self.animationViewer.frameList[num])

        try: #Do not work on first layer bc frameCreator is not instantiated yet.
            self.animationViewer.frameList[num].setIllustration(self.blankIllustration)
        except:
            pass
        return self.animationViewer.frameList[num] #Return data of the added frame.
    


class MainWindow(Qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CubAnimate")

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.animator = Animator(self)
        self.mainLayout.addWidget(self.animator,0,0)
        
        self.resize(self.screen().size()*0.9) #Do not delete if you want the window to maximized ... damn bug

        
        #SPACERS
        self.lowSpacer = Qtw.QSpacerItem(20, 40, Qtw.QSizePolicy.Minimum, Qtw.QSizePolicy.Expanding)
        self.mainLayout.addItem(self.lowSpacer,1,0)

