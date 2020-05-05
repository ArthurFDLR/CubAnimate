from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon, QKeySequence

from CustomWidgets.CubeViewer3D import CubeViewer3D
from CustomWidgets.CToolBox.CToolBox import CToolBox
from CustomWidgets.CDrawer import CDrawer
from CustomWidgets.CTypes import Axis, CubeSize, CubeLEDFrame_DATA
from CustomWidgets.CCubeViewerSliced import CCubeViewerSliced
from CustomWidgets.CAnimationTimeline import AnimationList, CubeLEDFrame



class Animator(Qtw.QWidget):
    """ Main widget allowing the user to create animations.
    
    Attributes:
        cubeSize (CubeSize)): Number of LEDs along each axis.
        blankIllustration (QPixmap): Default illustration to use when a new frame is created.
        self.currentSelectedFrame (CubeLEDFrame): Currently modified frame.
        colorPicker (ColorPicker): Widget to select the painting color.
        cubeViewer (CubeViewer3D): Widget showing the cube in 3D.
        cubeSliced (CCubeViewerSliced): Widget showing the sliced cube.
        newColorLED_signal (QtCore.pyqtSignal(int,int,int,QColor)): Signal sended when the led at the given position has a new color.
        eraseColorLED_signal (QtCore.pyqtSignal(int,int,int)): Signal sended when the led at the given position is erased.
    """

    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)
    saveAnimation_signal = QtCore.pyqtSignal()

    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)

        ## Attributes & Parameters
        self.parent = parent
        self.cubeSize = CubeSize(8,8,8)
        self.mainLayout=Qtw.QHBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.animationViewerRatio = 0.15
        self.animatorWidth = self.screen().size().width() * self.animationViewerRatio
        self.animationName = "Animation"

        ## Widget instantiation
        self.toolBox = CToolBox(False, False, self.saveAnimation_signal, self)
        self.cubeViewer = CubeViewer3D(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.cubeSliced = CCubeViewerSliced(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.animationViewer = AnimationList(self.cubeSize, self.animatorWidth)

        ## Window layout
        self.horizontlSpliter = Qtw.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSpliter = Qtw.QSplitter(QtCore.Qt.Vertical)

        self.horizontlSpliter.addWidget(self.toolBox)
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

        self.saveAnimation_signal.connect(self.saveAnimation)
        self.SaveShortcut = Qtw.QShortcut(QKeySequence("Ctrl+S"), self)
        self.SaveShortcut.activated.connect(self.saveAnimation)

    
    def getCurrentColor(self) -> QColor:
        """ Return the color selected in the widget colorPicker(ColorPicker)."""
        return self.toolBox.getColor()
    
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
        #self.cubeViewer.newFrameAnimation()
        return self.animationViewer.frameList[num]
    
    def saveAnimation(self):
        directoryName, fileExtension = Qtw.QFileDialog.getSaveFileName(self, 'Save File',"./{}".format(self.animationName),"Animation Files (*.anim)")

        if len(directoryName)>0:
            file = open(directoryName,'w')
            headerLine = "{}-{},{},{}-{}\n".format(self.animationName, self.cubeSize.getSize(Axis.X), self.cubeSize.getSize(Axis.Y), self.cubeSize.getSize(Axis.Z), str(self.toolBox.getFPS()))
            file.write(headerLine)
            for frame in self.animationViewer.frameList:
                frameSTR = frame.encodeData() + '\n'
                file.write(frameSTR)
            file.close()



class StartingMenuBackground(Qtw.QWidget):
    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = CubeSize(8,8,8)

        self.layout = Qtw.QVBoxLayout(self)
        self.cubeViewer = CubeViewer3D(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cubeViewer)
    
    def getCurrentColor(self) -> QColor :
        return QColor(255,0,0)



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
        self.startBackground = StartingMenuBackground(self)

        ## Main menu
        self.drawerMenu = CDrawer(self, direction=CDrawer.LEFT)
        self.mainMenu = MainMenu(self)
        self.drawerMenu.setWidget(self.mainMenu)

        ## Windows manager
        self.leftlist = Qtw.QListWidget()
        self.leftlist.insertItem(0, 'StarterBackground' )
        self.leftlist.insertItem(1, 'Animator' )
        self.Stack = Qtw.QStackedWidget(self)
        self.Stack.addWidget(self.animator)
        self.Stack.addWidget(self.startBackground)

        ## MainWindow layout
        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.Stack,0,1)      
        self.mainLayout.addWidget(Qtw.QPushButton('>', self, clicked=self.openMainMenu), 0, 0)

        self.resize(self.screen().size()*0.8) #Do not delete if you want the window to maximized. I know it works, I just don't know WHY it works.
    
    def openMainMenu(self):
        self.drawerMenu.show()
    
    def changeWindow(self,i):
        self.Stack.setCurrentIndex(i)