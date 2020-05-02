from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon

from CustomWidgets.CubeViewer3D import CubeViewer3D
from CustomWidgets.CColorPicker.CColorPicker import CColorPicker
from CustomWidgets.CDrawer import CDrawer
from CustomWidgets.CTypes import *

class CubeLEDFrame_DATA:
    def __init__(self, cubeSize:CubeSize):

        self.illustration = None
        
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
        self.parent = parent

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
        #policy = Qtw.QSizePolicy(Qtw.QSizePolicy.Preferred, Qtw.QSizePolicy.Preferred)
        #policy.setHeightForWidth(True)
        #self.setSizePolicy(policy)

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
        #policy = Qtw.QSizePolicy(Qtw.QSizePolicy.Preferred, Qtw.QSizePolicy.Preferred)
        #policy.setHeightForWidth(True)
        #self.setSizePolicy(policy)

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
        self.layout.setSpacing(20)
        

        self.ledLayers = []

        for i in range(self._parent.cubeSize.getSize(slicingAxis)):
            self.ledLayers.append(CubeLayerView(self._parent.cubeSize, i, 
                                                columnAxis, rowAxis, slicingAxis,
                                                newColor_signal, eraseColor_signal, self))
            self.layout.addWidget(self.ledLayers[i])
            self.layout.setAlignment(self.ledLayers[i], QtCore.Qt.AlignVCenter)
        
        self.setWidget(self.layersWidget)
        self.setWidgetResizable(True)
    
    def resizeEvent(self, event):
        screenHeight = self.screen().size().height()
        layerHeight = self.ledLayers[0].height()
        if screenHeight * 0.2 > layerHeight:
            self.setMinimumHeight(layerHeight*1.2)
    
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



class CubeLEDFrame(Qtw.QListWidgetItem):
    """ Item to use in an AnimationList object. Represent a frame in the timeline.
    
    Attributes:
        name (str): Name of the frame.
        frameDate (CubeLEDFrame_DATA): Currently modified frame.
        cubeSize (CubeSize): Number of LEDs along each axis.
        illustration (QLabel): Consist of a representation (QPixmap) of the frame associated.
    """

    def __init__(self, name : str, cubeSize:CubeSize, width:int, parentList, parent):
        super(Qtw.QListWidgetItem, self).__init__(None,parentList)
        self.parentList = parentList
        self.parent = parent
        self.name = name
        
        self.frameData = CubeLEDFrame_DATA(cubeSize)
        self.setSizeHint(QtCore.QSize(width,width*0.9))
 
        self.frame =  Qtw.QGroupBox(self.name)
        self.layout = Qtw.QHBoxLayout()
        self.frame.setLayout(self.layout)

        self.illustration = QPixmap()
        self.illustrationViewer = Qtw.QLabel()

        self.leftSpacer = Qtw.QSpacerItem(1, 1, Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding) # Spacers for centering
        self.rightSpacer = Qtw.QSpacerItem(1, 1, Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
        self.layout.addItem(self.leftSpacer)
        self.layout.addWidget(self.illustrationViewer)
        self.layout.addItem(self.rightSpacer)

        self.parentList.setItemWidget(self,self.frame)
    
    def setIllustration(self, image : QPixmap):
        self.illustration = image
        self.illustrationViewer.setPixmap(self.illustration)
    
    def getIllustration(self):
        return self.illustration

    def getFrameData(self) -> CubeLEDFrame_DATA:
        return self.frameData
        


class ratioPushButton(Qtw.QPushButton):
    def __init__(self, label:str, aspectRatio : float, parent):
        super(Qtw.QPushButton, self).__init__(label, parent)
        self.aspectRatio = aspectRatio
        self.parent = parent
        #self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)

    def resizeEvent(self, event):
        w = int(self.parent.listWidth * 0.94)
        h = int(w*self.aspectRatio)
        self.setFixedSize(QtCore.QSize(w,h))
        #self.resize(w, h)



class AnimationList(Qtw.QWidget):
    """ Widget allowing the user to create a new frame, select the currently modified frame and reorganize them.
    
    Attributes:
        frameList (List[CubeLEDFrame]): Store all frames of the animation.
    """
    def __init__(self, cubeSize:CubeSize, size : int, horizontalDisplay : bool = False, parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.listWidth = size

        self.timeLine = Qtw.QListWidget()
        if horizontalDisplay:
            self.layout = Qtw.QHBoxLayout()
            self.timeLine.setFlow(Qtw.QListView.LeftToRight)
            self.addFrameButton = ratioPushButton("Add frame !", 1.0,self)
            self.setFixedHeight(self.listWidth)
            self.timeLine.setHorizontalScrollMode(Qtw.QAbstractItemView.ScrollPerPixel)
        else:
            self.layout = Qtw.QVBoxLayout()
            self.addFrameButton = ratioPushButton("Add frame !",0.3 ,self)
            self.setFixedWidth(self.listWidth)
            self.timeLine.setVerticalScrollMode(Qtw.QAbstractItemView.ScrollPerPixel)
        self.setLayout(self.layout)

        self.timeLine.setDragDropMode(Qtw.QAbstractItemView.InternalMove)
        self.layout.addWidget(self.timeLine)
        self.layout.setStretchFactor(self.timeLine,1)

        self.layout.addWidget(self.addFrameButton)

        self.frameList = [] #Store all frames
    
    def changeFrameSelected(self, frame : CubeLEDFrame):
        self.timeLine.setCurrentItem(frame)



class Animator(Qtw.QWidget):
    """ Main widget allowing the user to create animations.
    
    Attributes:
        cubeSize (CubeSize)): Number of LEDs along each axis.
        blankIllustration (QPixmap): Default illustration to use when a new frame is created.
        self.currentSelectedFrame (CubeLEDFrame): Currently modified frame.
        colorPicker (ColorPicker): Widget to select the painting color.
        cubeViewer (CubeViewer3D): Widget showing the cube in 3D.
        cubeSliced (CubeFullView): Widget showing the sliced cube.
        newColorLED_signal (QtCore.pyqtSignal(int,int,int,QColor)): Signal sended when the led at the given position has a new color.
        eraseColorLED_signal (QtCore.pyqtSignal(int,int,int)): Signal sended when the led at the given position is erased.
    """

    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        
        ## Attributes & Parameters
        self.parent = parent
        self.cubeSize = CubeSize(8,8,8)
        self.mainLayout=Qtw.QHBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.animationViewerRatio = 0.15
        self.animatorWidth = self.screen().size().width() * self.animationViewerRatio

        ## Widget instantiation
        self.colorPicker = CColorPicker(self)
        self.cubeViewer = CubeViewer3D(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.cubeSliced = CubeFullView(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.animationViewer = AnimationList(self.cubeSize, self.animatorWidth)

        ## Window layout
        self.horizontlSpliter = Qtw.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSpliter = Qtw.QSplitter(QtCore.Qt.Vertical)

        self.horizontlSpliter.addWidget(self.colorPicker)
        self.horizontlSpliter.addWidget(self.cubeViewer)
        self.horizontlSpliter.addWidget(self.animationViewer)
        self.horizontlSpliter.setStretchFactor(0,0)
        self.horizontlSpliter.setStretchFactor(1,1)
        self.horizontlSpliter.setStretchFactor(2,0)

        self.verticalSpliter.addWidget(self.horizontlSpliter)
        self.verticalSpliter.addWidget(self.cubeSliced)
        self.verticalSpliter.setStretchFactor(0,1)
        self.verticalSpliter.setStretchFactor(1,0)

        self.mainLayout.addWidget(self.verticalSpliter)
        
        ## Other
        self.blankIllustration = self.getCurrentCubePixmap()
        self.currentSelectedFrame = self.addFrame()

        ## Signal connection
        self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED)
        self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
        self.animationViewer.addFrameButton.clicked.connect(self.addFrame)
        self.animationViewer.timeLine.itemSelectionChanged.connect(self.changeCurrentFrame)
    
    def getCurrentColor(self) -> QColor:
        """ Return the color selected in the widget colorPicker(ColorPicker)."""
        return self.colorPicker.getColor()
    
    def getCurrentCubePixmap(self) -> QPixmap:
        """ Return the vizualisation of the widget cubeViewer(CubeViewer3D)."""
        illustrationWidth = self.animatorWidth*0.85
        return self.cubeViewer.getCurrentFramePixmap(QtCore.QSize(illustrationWidth,illustrationWidth*0.9))
    
    def changeCurrentFrame(self):
        """ Change the frame being edited."""
        self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap()) #Update illustration of the leaved frame
        newFrame = self.animationViewer.timeLine.selectedItems()[0] 
        newFrameData = newFrame.getFrameData()
        newSize = newFrameData.getSize()

        if self.currentSelectedFrame.getFrameData().getSize() == newSize: #Verify size compatibility
            self.newColorLED_signal.disconnect(self.currentSelectedFrame.getFrameData().setColorLED) #Disconnect old frame
            self.eraseColorLED_signal.disconnect(self.currentSelectedFrame.getFrameData().eraseColorLED)
            for x in range(newSize.getSize(Axis.X)):
                for y in range(newSize.getSize(Axis.Y)):
                    for z in range(newSize.getSize(Axis.Z)):
                        newColor = newFrameData.getColorLED(x,y,z)
                        if self.currentSelectedFrame.getFrameData().getColorLED(x,y,z) != newColor:  #Great gain in refresh speed if the frames are similare
                            self.newColorLED_signal.emit(x,y,z, newColor)

            self.currentSelectedFrame = newFrame
            self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED) #Connect new frame
            self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
        else:
            print("Cube size incompatibility")
    
    def addFrame(self):
        """ Create and add a new frame to the animation."""
        num = len(self.animationViewer.frameList)
        frameWidth = self.animatorWidth*0.9
        self.animationViewer.frameList.append(CubeLEDFrame('#{}'.format(num+1), self.cubeSize,frameWidth , self.animationViewer.timeLine, self.animationViewer))
        self.animationViewer.changeFrameSelected(self.animationViewer.frameList[num])
        self.animationViewer.frameList[num].setIllustration(self.blankIllustration)
        return self.animationViewer.frameList[num]


class MainMenu(Qtw.QWidget):
    def __init__(self, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('MainMenu{background:white;}')
        layout = Qtw.QVBoxLayout(self)
        layout.addWidget(Qtw.QLineEdit(self))

        self.animatorButton = Qtw.QPushButton('Animator', self, clicked=self.displayAnimator)
        layout.addWidget(self.animatorButton)

        self.labelButton = Qtw.QPushButton('Label', self, clicked=self.displayLabel)
        layout.addWidget(self.labelButton)

    def displayAnimator(self):
        self.parent.changeWindow(0)
    
    def displayLabel(self):
        self.parent.changeWindow(1)


class MainWindow(Qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CubAnimate")

        ## Windows instantiation
        self.animator = Animator(self)
        self.widgetExample = Qtw.QLabel("Hello there!")

        ## Main menu
        self.drawerMenu = CDrawer(self, direction=CDrawer.LEFT)
        self.mainMenu = MainMenu(self)
        self.drawerMenu.setWidget(self.mainMenu)

        ## Windows manager
        self.leftlist = Qtw.QListWidget()
        self.leftlist.insertItem(0, 'Animator' )
        self.leftlist.insertItem(1, 'Label' )
        self.Stack = Qtw.QStackedWidget(self)
        self.Stack.addWidget(self.animator)
        self.Stack.addWidget(self.widgetExample)

        ## MainWindow layout
        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.Stack,0,1)        
        self.mainLayout.addWidget(Qtw.QPushButton('Open menu', self, clicked=self.openMainMenu), 0, 0)

        self.resize(self.screen().size()*0.8) #Do not delete if you want the window to maximized ... damn bug
    
    def openMainMenu(self):
        self.drawerMenu.show()
    
    def changeWindow(self,i):
        self.Stack.setCurrentIndex(i)