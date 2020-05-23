from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon, QKeySequence

from CustomWidgets.CubeViewer3D import CubeViewer3DInteract
from CustomWidgets.CToolBox.CToolBox import CToolBox
from CustomWidgets.CDrawer import CDrawer
from CustomWidgets.CTypes import Axis, CubeSize, CubeLEDFrame_DATA
from CustomWidgets.CCubeViewerSliced import CCubeViewerSliced
from CustomWidgets.CAnimationTimeline import AnimationList, CubeLEDFrame
from CustomWidgets.CFramelessDialog import NewAnimationDialog, LoadingDialog
from CustomWidgets.CEIWindow import EIWindow
from CustomWidgets.CGradientDesigner import GradientDesigner
#from CustomWidgets.CWaitingSpinnerWidget import QtWaitingSpinner



class Animator(Qtw.QWidget):
    """ Main widget allowing the user to create animations.
    
    Attributes:
        cubeSize (CubeSize)): Number of LEDs along each axis.
        blankIllustration (QPixmap): Default illustration to use when a new frame is created.
        self.currentSelectedFrame (CubeLEDFrame): Currently modified frame.
        colorPicker (ColorPicker): Widget to select the painting color.
        cubeViewer (CubeViewer3DInteract): Widget showing the cube in 3D.
        cubeSliced (CCubeViewerSliced): Widget showing the sliced cube.
        newColorLED_signal (QtCore.pyqtSignal(int,int,int,QColor)): Signal sended when the led at the given position has a new color.
        eraseColorLED_signal (QtCore.pyqtSignal(int,int,int)): Signal sended when the led at the given position is erased.
    """

    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)
    saveAnimation_signal = QtCore.pyqtSignal()

    def __init__(self, parent, cubeSizeInit:CubeSize = CubeSize(8,8,8)):
        super(Qtw.QWidget, self).__init__(parent)

        ## Attributes & Parameters
        self.parent = parent
        self.cubeSize = cubeSizeInit
        self.mainLayout=Qtw.QHBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.animationViewerRatio = 0.15
        self.animatorWidth = self.screen().size().width() * self.animationViewerRatio
        self.animationName = "Animation"
        self.animationSaved = True
        self.noAnimationEdited = True

        ## Widget instantiation
        self.toolBox = CToolBox(False, False, self.saveAnimation_signal, self)
        self.cubeViewer = CubeViewer3DInteract(True, self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
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
        #self.currentSelectedFrame = self.addFrame()
        self.currentSelectedFrame = None

        ## Signal connection
        #self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED)
        #self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
        self.animationViewer.addFrameButton.clicked.connect(self.addFrame)
        self.animationViewer.timeLine.itemSelectionChanged.connect(self.changeCurrentFrame)

        self.newColorLED_signal.connect(self.notSaved)
        self.eraseColorLED_signal.connect(self.notSaved)
        self.animationViewer.addFrameButton.clicked.connect(self.notSaved)

        self.saveAnimation_signal.connect(self.saveAnimation)
        self.SaveShortcut = Qtw.QShortcut(QKeySequence("Ctrl+S"), self)
        self.SaveShortcut.activated.connect(self.saveAnimation)

    def notSaved(self, x=0, y=0, z=0, color = QColor(0,0,0)):
        self.animationSaved = False
    
    def getCurrentColor(self) -> QColor:
        """ Return the color selected in the widget colorPicker(ColorPicker)."""
        return self.toolBox.getColor()
    
    def getCurrentCubePixmap(self) -> QPixmap:
        """ Return the vizualisation of the widget cubeViewer(CubeViewer3DInteract)."""
        illustrationWidth = self.animatorWidth*0.85
        return self.cubeViewer.getCurrentFramePixmap(QtCore.QSize(illustrationWidth,illustrationWidth*0.9))
    
    def changeCurrentFrame(self):
        """ Change the frame being edited."""

        if self.currentSelectedFrame != None:
            self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap()) #Update illustration of the leaved frame
        
        newFrame = self.animationViewer.timeLine.selectedItems()[0] 
        newFrameData = newFrame.getFrameData()
        newSize = newFrameData.getSize()

        if self.currentSelectedFrame != None:
            if self.currentSelectedFrame.getFrameData().getSize() == newSize: #Verify size compatibility
                self.newColorLED_signal.disconnect(self.currentSelectedFrame.getFrameData().setColorLED) #Disconnect old frame
                self.eraseColorLED_signal.disconnect(self.currentSelectedFrame.getFrameData().eraseColorLED)
                for x in range(newSize.getSize(Axis.X)):
                    for y in range(newSize.getSize(Axis.Y)):
                        for z in range(newSize.getSize(Axis.Z)):
                            newColor = newFrameData.getColorLED(x,y,z)
                            if self.cubeViewer.getDisplayedColor(x,y,z) != newColor:  #Great gain in refresh speed if the frames are similare
                                self.newColorLED_signal.emit(x,y,z, newColor)

                self.currentSelectedFrame = newFrame
                self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED) #Connect new frame
                self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
            else:
                print("Cube size incompatibility")
        else:
            for x in range(newSize.getSize(Axis.X)):
                for y in range(newSize.getSize(Axis.Y)):
                    for z in range(newSize.getSize(Axis.Z)):
                        newColor = newFrameData.getColorLED(x,y,z)
                        if self.cubeViewer.getDisplayedColor(x,y,z) != newColor:  #Great gain in refresh speed if the frames are similare
                            self.newColorLED_signal.emit(x,y,z, newColor)
            self.currentSelectedFrame = newFrame
            self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED) #Connect new frame
            self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)

    
    def addFrame(self) -> CubeLEDFrame:
        """ Create and add a new frame to the animation."""
        num = len(self.animationViewer.frameList)
        frameWidth = self.animatorWidth*0.9
        self.animationViewer.frameList.append(CubeLEDFrame('#{}'.format(num+1), self.cubeSize,frameWidth , self.animationViewer.timeLine, self.animationViewer))
        self.animationViewer.changeFrameSelected(self.animationViewer.frameList[num])
        self.animationViewer.frameList[num].setIllustration(self.blankIllustration)
        #self.cubeViewer.newFrameAnimation()
        return self.animationViewer.frameList[num]
    
    def saveAnimation(self):
        fileLocation, fileExtension = Qtw.QFileDialog.getSaveFileName(self, 'Save File',"./{}".format(self.animationName.replace(' ','_')),"Animation Files (*.anim)")

        if len(fileLocation)>0:
            file = open(fileLocation,'w')
            headerLine = "{}-{},{},{}-{}\n".format(self.animationName, self.cubeSize.getSize(Axis.X), self.cubeSize.getSize(Axis.Y), self.cubeSize.getSize(Axis.Z), str(self.toolBox.getFPS()))
            file.write(headerLine)
            for frame in self.animationViewer.frameList:
                frameSTR = frame.encodeData() + '\n'
                file.write(frameSTR)
            file.close()
            self.animationSaved = True
        else:
            print('Saving canceled')
    
    def changeCubeSize(self, cubeSize : CubeSize):
        self.cubeSize = cubeSize
        self.cubeViewer.changeCubeSize(cubeSize)
        self.cubeSliced.changeCubeSize(cubeSize)
    
    def isSaved(self):
        return self.animationSaved
    
    def createAnimation(self, cubeSize : CubeSize, name:str):
        self.animationName = name
        self.changeCubeSize(cubeSize)
        self.noAnimationEdited = False
        self.addFrame()
    
    def isEmpty(self):
        return self.noAnimationEdited
    
    def loadAnimation(self, fileLocation : str):
        file = open(fileLocation,'r')
        for line in file:
            if line[0] == '#':
                self.loadFrame(line[:-1])
        file.close()
    
    def loadFrame(self, dataLine:str):
        self.noAnimationEdited = False
        self.addFrame()
        self.currentSelectedFrame.decodeData(dataLine)
        for x in range(self.cubeSize.getSize(Axis.X)):
            for y in range(self.cubeSize.getSize(Axis.Y)):
                for z in range(self.cubeSize.getSize(Axis.Z)):
                    newColor = self.currentSelectedFrame.getFrameData().getColorLED(x,y,z)
                    if self.cubeViewer.getDisplayedColor(x,y,z) != newColor:  #Great gain in refresh speed if the frames are similare
                        self.newColorLED_signal.emit(x,y,z, newColor)
        self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap())
    
    def setBackgroundColor(self, color:QColor):
        self.cubeViewer.setBackgroundColor(color)
        self.setStyleSheet("background-color: {}".format(color.name()))



class StartingMenuBackground(Qtw.QWidget):
    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = CubeSize(8,8,8)

        self.layout = Qtw.QVBoxLayout(self)
        self.cubeViewer = CubeViewer3DInteract(False, self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cubeViewer)
    
    def getCurrentColor(self) -> QColor :
        return QColor(255,0,0)
    
    def setBackgroundColor(self, color:QColor):
        self.cubeViewer.setBackgroundColor(color)


class TimerThread(QtCore.QThread):
    ''' Begin with start(), end with terminate() '''
    def __init__(self, signal:QtCore.pyqtSignal, timeout:int, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.timeout = timeout
        self.signal = signal
        self.dataCollectionTimer = QtCore.QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.dataCollectionTimer.timeout.connect(lambda: self.signal.emit())

    def run(self):
        self.dataCollectionTimer.start(self.timeout)
        loop = QtCore.QEventLoop()
        loop.exec_()

class HueEditor(Qtw.QWidget):
    
    saveHUE_signal = QtCore.pyqtSignal()
    anim_signal = QtCore.pyqtSignal()

    def __init__(self, cubeSizeInit:CubeSize, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = cubeSizeInit
        self.mainLayout=Qtw.QHBoxLayout(self)
        self.setLayout(self.mainLayout)

        ## Update test
        self.anim_signal.connect(self.cubeViewerUpdate)
        timer = TimerThread(self.anim_signal, int(1000/30))
        timer.start()
        self.i=0

        ## Widget instantiation
        self.toolBox = CToolBox(False, False, self.saveHUE_signal, self)
        self.cubeViewer = CubeViewer3DInteract(False, self.cubeSize, None, None, self)
        self.gradientViewer = GradientDesigner()

        ## Window layout
        self.horizontlSpliter = Qtw.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSpliter = Qtw.QSplitter(QtCore.Qt.Vertical)

        self.horizontlSpliter.addWidget(self.toolBox)
        self.horizontlSpliter.addWidget(self.cubeViewer)
        self.horizontlSpliter.setStretchFactor(0,0)
        self.horizontlSpliter.setStretchFactor(1,1)

        self.verticalSpliter.addWidget(self.horizontlSpliter)
        self.verticalSpliter.addWidget(self.gradientViewer)
        self.verticalSpliter.setStretchFactor(0,1)
        self.verticalSpliter.setStretchFactor(1,0)

        self.mainLayout.addWidget(self.verticalSpliter)

        self.saveHUE_signal.connect(lambda: print('Save HUE'))
    
    def setBackgroundColor(self, color:QColor):
        self.setStyleSheet("background-color: {}".format(color.name()))
    
    def cubeViewerUpdate(self):
        self.i += 1
        if self.i > 100:
            self.i = 0
        for x in range(self.cubeSize.getSize(Axis.X)):
            for y in range(self.cubeSize.getSize(Axis.Y)):
                for z in range(self.cubeSize.getSize(Axis.Z)):
                    self.cubeViewer.modifier.changeColor(x,y,z, self.gradientViewer.getColorAt(self.i/100) )
    
    def getCurrentColor(self):
        return QColor(250,250,250)


class MainMenu(Qtw.QWidget):
    def __init__(self, newWindow_signal:QtCore.pyqtSignal, parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.newWindow_signal = newWindow_signal

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('MainMenu{background:white;}')
        layout = Qtw.QVBoxLayout(self)
        layout.addWidget(Qtw.QLineEdit(self))

        self.animatorButton = WindowSelectionButton('Animation', self.newWindow_signal, MainWindow.ANIMATOR, self)
        layout.addWidget(self.animatorButton)

        self.startButton = WindowSelectionButton('Start', self.newWindow_signal, MainWindow.STARTER, self)
        layout.addWidget(self.startButton)

        self.equationButton = WindowSelectionButton('Equation mode', self.newWindow_signal, MainWindow.EQUATION_INTERPRETER, self)
        layout.addWidget(self.equationButton)

        self.hueEditorButton = WindowSelectionButton('HUE mode', self.newWindow_signal, MainWindow.HUE_EDITOR, self)
        layout.addWidget(self.hueEditorButton)



class WindowSelectionButton(Qtw.QPushButton):

    stylesheet = """
    #Custom_Window_Button {
        border: 1px solid #cbcbcb;
        border-radius: 5px;
        font-size: 16px;
        background: white;
    }
    #Custom_Window_Button:hover {
        border-color: rgb(139, 173, 228);
        color: rgb(139, 173, 228);
    }
    #Custom_Window_Button:pressed {
        color: #cbcbcb;
        border-color: #cbcbcb;
    }
    """
    def __init__(self, text : str, newWindow_signal:QtCore.pyqtSignal, menuIndex : int, parent=None):
        super(Qtw.QPushButton, self).__init__(text, parent, cursor=QtCore.Qt.PointingHandCursor, toolTip='Change current editor', clicked=lambda: newWindow_signal.emit(menuIndex))
        self.newWindow_signal = newWindow_signal
        self.menuIndex = menuIndex

        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Preferred)
        self.setObjectName('Custom_Window_Button')
        self.setStyleSheet(self.stylesheet)


class MainWindow(Qtw.QWidget):
    newWindow_signal = QtCore.pyqtSignal(int)
    waitingCursor_signal = QtCore.pyqtSignal(bool)
    STARTER, ANIMATOR, EQUATION_INTERPRETER, HUE_EDITOR = range(4)

    def __init__(self, mainApplication : Qtw.QApplication):
        super().__init__()
        self.setWindowTitle("CubAnimate")
        self.cubeSize = CubeSize(8,8,8)
        self.mainApplication = mainApplication
        self.setObjectName('Custom_Main_Window')
        self.backgroundColor = QColor(250,250,255)

        ## Windows instantiation
        self.animator = Animator(self, self.cubeSize)
        self.startBackground = StartingMenuBackground(self)
        self.equationInterpreter = EIWindow(self)
        self.hueEditor = HueEditor(self.cubeSize, self)

        ## Main menu
        self.drawerMenu = CDrawer(self)
        self.mainMenu = MainMenu(self.newWindow_signal, self)
        self.drawerMenu.setWidget(self.mainMenu)

        ## Windows manager
        self.windowList = Qtw.QListWidget()
        self.windowList.insertItem(self.STARTER, 'StarterBackground' )
        self.windowList.insertItem(self.ANIMATOR, 'Animator' )
        self.windowList.insertItem(self.EQUATION_INTERPRETER, 'EquationInterpreter')
        self.windowList.insertItem(self.HUE_EDITOR, 'HueEditor')
        self.windowStack = Qtw.QStackedWidget(self)
        self.windowStack.addWidget(self.startBackground)
        self.windowStack.addWidget(self.animator)
        self.windowStack.addWidget(self.equationInterpreter)
        self.windowStack.addWidget(self.hueEditor)

        self.newWindow_signal.connect(self.changeWindow)
        self.waitingCursor_signal.connect(self.setWaitingCursor)

        ## MainWindow layout
        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.windowStack,0,1)      
        self.mainLayout.addWidget(Qtw.QPushButton('>', self, clicked=self.openMainMenu), 0, 0)

        self.resize(self.screen().size()*0.8) #Do not delete if you want the window to maximized correctly...
        self.changeBackgorundColor(self.backgroundColor)
        #self.waitingIcon = LoadingDialog(self)
        #self.waitingIcon.start()
        #self.waitingIcon.stop()

    def setWaitingCursor(self, activate : bool):
        
        if activate:
            self.mainApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            #self.waitingIcon.start()
            print('On')
        else:
            self.mainApplication.restoreOverrideCursor()
            #self.waitingIcon.stop()
            print('Off')
    
    def openMainMenu(self):
        self.drawerMenu.show()
    
    def changeWindow(self, indexWindow):
        if indexWindow == self.STARTER:                         ## STARTING WINDOW
            self.windowStack.setCurrentIndex(indexWindow)

        if indexWindow == self.ANIMATOR:                        ## ANIMATION WINDOW
            if not self.animator.isEmpty():
                self.windowStack.setCurrentIndex(indexWindow)
    
            newAnimDialog = NewAnimationDialog(self)
            if newAnimDialog.exec_(): #If pop-up not exited
                self.waitingCursor_signal.emit(True)
                if newAnimDialog.createNewAnimation(): #Create a new animation
                    print('Create new animation')
                    self.animator.createAnimation(self.cubeSize,'New animation')
                elif newAnimDialog.loadAnimation(): #Load an existing animation
                    print('Load animation: ' + newAnimDialog.getFileLocation())
                    self.animator.changeCubeSize(self.cubeSize)
                    self.animator.loadAnimation(newAnimDialog.getFileLocation())
                self.waitingCursor_signal.emit(False)
                self.windowStack.setCurrentIndex(indexWindow)
            
        if indexWindow == self.EQUATION_INTERPRETER:            ## EQUATION WINDOW
            self.windowStack.setCurrentIndex(indexWindow)
        
        if indexWindow == self.HUE_EDITOR:                      ## HUE WINDOW
            self.windowStack.setCurrentIndex(indexWindow)

        self.drawerMenu.animationOut()
    
    def changeBackgorundColor(self, color:QColor):
        self.setStyleSheet("#Custom_Main_Window {background: %s;}"%(self.backgroundColor.name()))
        self.startBackground.setBackgroundColor(self.backgroundColor)
        self.animator.setBackgroundColor(self.backgroundColor)
