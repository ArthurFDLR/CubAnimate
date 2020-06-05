from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon, QKeySequence

from CustomWidgets.CubeViewer3D import CubeViewer3DInteract
from CustomWidgets.CToolBox.CToolBox import CToolBox_Animator, CToolBox_HUE
from CustomWidgets.CDrawer import CDrawer
from CustomWidgets.CTypes import Axis, CubeSize, CubeLEDFrame_DATA
from CustomWidgets.CCubeViewerSliced import CCubeViewerSliced
from CustomWidgets.CAnimationTimeline import AnimationList, CubeLEDFrame
from CustomWidgets.CFramelessDialog import NewAnimationDialog, LoadingDialog
from CustomWidgets.CEIWindow import EIWindow
from CustomWidgets.CGradientDesigner import GradientDesigner
#from CustomWidgets.CWaitingSpinnerWidget import QtWaitingSpinner

#import resources

class DimmingLayerWidget(Qtw.QWidget):
    stylesheetOpacity = """
    #CD_alphaWidget {
        background:rgba(55,55,55,%i);
        }
    #closeButton {
        min-width: 50px;
        min-height: 50px;
        font-family: "Webdings";
        qproperty-text: "r";
        border-radius: 10px;
        color: white;
        background: red;
    }
    #closeButton:hover {
        color: white;
        background: rgb(190, 0, 0);
    }
    """

    def __init__(self, dimmedWidget:Qtw.QWidget, focusedWidget:Qtw.QWidget):
        super(DimmingLayerWidget, self).__init__(dimmedWidget, objectName='CD_alphaWidget')
        self.focusedWidget = focusedWidget
        self.dimmedWidget = dimmedWidget
        self.opacity = 0
        self.isOn = False

        ## Configuration
        self.setAttribute(QtCore.Qt.WA_StyledBackground) # Needed to apply style sheet
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.resize(self.screen().size())
        self.setStyleSheet(self.stylesheetOpacity % (self.opacityDim))
        self.lower()
        self.exitButton = Qtw.QPushButton('r', self, clicked=lambda:self.dimOut(False), objectName='closeButton')
        self.exitButton.hide()

        ## Animations
        self.animFadeIn = QtCore.QPropertyAnimation(self, duration=50, easingCurve=QtCore.QEasingCurve.Linear)
        self.animFadeIn.setPropertyName(b'opacityDim')
        self.animFadeIn.setTargetObject(self)

        self.animFadeOut = QtCore.QPropertyAnimation(self, duration=50, easingCurve=QtCore.QEasingCurve.Linear, finished=lambda:self.lower())
        self.animFadeOut.setPropertyName(b'opacityDim')
        self.animFadeOut.setTargetObject(self)

    
    def dimOut(self, on:bool):
        if on:
            if not self.isOn:
                self.isOn = True
                self.raise_()

                self.opacity = 0
                self.animFadeIn.setStartValue(0)
                self.animFadeIn.setEndValue(100)
                self.animFadeIn.start()
                self.exitButton.show()

        else:
            if self.isOn:
                self.isOn = False
                self.animFadeIn.stop()
                self.opacity = 100
                self.animFadeOut.setStartValue(100)
                self.animFadeOut.setEndValue(0)
                self.animFadeOut.start()
                #self.lower()
                self.exitButton.hide()

    def getOpacityDim(self):
        return self.opacity

    def setOpacityDim(self, value):
        self.opacity = value
        self.setStyleSheet(self.stylesheetOpacity % (self.opacity))

    opacityDim = QtCore.pyqtProperty(int, getOpacityDim, setOpacityDim)

    def moveButton(self, upRightWindowX:int, upRightWindowY:int):
        self.exitButton.move(upRightWindowX + 20, upRightWindowY)

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
    playAnimation_signal = QtCore.pyqtSignal()

    stylesheet = """
    QSplitter::handle:vertical {
        image: url(:/UI/SplitterHandleHorizontal.svg);
        margin-top: 0px;
        margin-bottom: 0px;
    }
    QSplitter::handle:horizontal {
        image: url(:/UI/SplitterHandleVertical.svg);
    }
    """

    def __init__(self, parent, openMenu_signal:QtCore.pyqtSignal, cubeSizeInit:CubeSize = CubeSize(8,8,8)):
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
        self.setObjectName('Animator_Widget')
        self.setStyleSheet(self.stylesheet)

        ## Widget instantiation
        self.toolBox = CToolBox_Animator(False, False, self.saveAnimation_signal, self.playAnimation_signal, self)
        self.cubeViewer = CubeViewer3DInteract(True, self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.cubeSliced = CCubeViewerSliced(self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.animationViewer = AnimationList(self.cubeSize, self.animatorWidth)

        ## Window layout
        self.setContentsMargins(0,0,0,0)
        self.horizontlSpliter = Qtw.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSpliter = Qtw.QSplitter(QtCore.Qt.Vertical)

        self.horizontlSpliter.setHandleWidth(6)
        self.verticalSpliter.setHandleWidth(6)

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
        
        ## Dim out layer
        self.alphaWidget = DimmingLayerWidget(self, self.cubeViewer)

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
        self.playAnimation_signal.connect(self.playAnimation)
        self.SaveShortcut = Qtw.QShortcut(QKeySequence("Ctrl+S"), self)
        self.SaveShortcut.activated.connect(self.saveAnimation)

        self.openMenu_signal = openMenu_signal

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

        self.openMenu_signal.emit(True)

        if self.currentSelectedFrame != None:
            self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap()) #Update illustration of the leaved frame
        
        if len(self.animationViewer.timeLine.selectedItems()) > 0:
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
                                if self.cubeViewer.getDisplayedColor(x,y,z).name() != newColor.name():  #Great gain in refresh speed if the frames are similare
                                    self.newColorLED_signal.emit(x,y,z, newColor)

                    self.currentSelectedFrame = newFrame
                    self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED) #Connect new frame
                    self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
                else:
                    print("Cube size incompatibility")
            else:
                print('enter')
                for x in range(newSize.getSize(Axis.X)):
                    for y in range(newSize.getSize(Axis.Y)):
                        for z in range(newSize.getSize(Axis.Z)):
                            newColor = newFrameData.getColorLED(x,y,z)
                            #print(newColor.name() + ' ' + self.cubeViewer.getDisplayedColor(x,y,z).name())
                            if self.cubeViewer.getDisplayedColor(x,y,z).name() != newColor.name():  #Great gain in refresh speed if the frames are similare
                                self.newColorLED_signal.emit(x,y,z, newColor)
                self.currentSelectedFrame = newFrame
                self.newColorLED_signal.connect(self.currentSelectedFrame.getFrameData().setColorLED) #Connect new frame
                self.eraseColorLED_signal.connect(self.currentSelectedFrame.getFrameData().eraseColorLED)
        
        self.openMenu_signal.emit(False)

    
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
        self.animationViewer.clearAllFrames()
        self.animationName = name
        self.changeCubeSize(cubeSize)
        self.noAnimationEdited = False
        self.addFrame()
    
    def isEmpty(self):
        return self.noAnimationEdited
    
    def loadAnimation(self, fileLocation : str):
        self.animationViewer.clearAllFrames()
        file = open(fileLocation,'r')
        for line in file:
            if line[0] == '#':
                self.loadFrame(line[:-1])
        file.close()
        self.noAnimationEdited = False
    
    def loadFrame(self, dataLine:str):
        self.addFrame()
        self.currentSelectedFrame.decodeData(dataLine)
        for x in range(self.cubeSize.getSize(Axis.X)):
            for y in range(self.cubeSize.getSize(Axis.Y)):
                for z in range(self.cubeSize.getSize(Axis.Z)):
                    newColor = self.currentSelectedFrame.getFrameData().getColorLED(x,y,z)
                    if self.cubeViewer.getDisplayedColor(x,y,z).name() != newColor.name():  #Great gain in refresh speed if the frames are similare, compare name to avoid alpha comparison
                        self.newColorLED_signal.emit(x,y,z, newColor)
        self.currentSelectedFrame.setIllustration(self.getCurrentCubePixmap())
    
    def resizeEvent(self,e):
        self.alphaWidget.moveButton(self.cubeViewer.pos().x() + self.cubeViewer.size().width(), self.cubeViewer.pos().y())
        super(Animator, self).resizeEvent(e)
    
    def setBackgroundColor(self, color:QColor):
        self.cubeViewer.setBackgroundColor(color)

    def playAnimation(self):
        self.alphaWidget.dimOut(True)


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

    stylesheet = """
    #HUE_Editor_Window {
        background-color: %(bgColor)s;
    }
    QSplitter::handle:vertical {
        image: url(:/UI/SplitterHandleHorizontal.svg);
        margin-bottom: 10px;
    }
    QSplitter::handle:horizontal {
        image: url(:/UI/SplitterHandleVertical.svg);
    }
    """

    def __init__(self, cubeSizeInit:CubeSize, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = cubeSizeInit
        self.mainLayout=Qtw.QHBoxLayout(self)
        self.setLayout(self.mainLayout)
        self.setObjectName('HUE_Editor_Window')
        self.setStyleSheet(self.stylesheet % {'bgColor': QColor(255,255,255).name()})
        self.animationOn = False

        ## Update test
        self.anim_signal.connect(self.cubeViewerUpdate)
        self.timer = TimerThread(self.anim_signal, int(1000/24))
        self.timer.start()
        self.i=0

        ## Widget instantiation
        self.toolBox = CToolBox_HUE(False, False, self.saveHUE_signal, self)
        self.cubeViewer = CubeViewer3DInteract(False, self.cubeSize, None, None, self)
        self.gradientViewer = GradientDesigner()

        ## Window layout
        self.horizontlSpliter = Qtw.QSplitter(QtCore.Qt.Horizontal)
        self.verticalSpliter = Qtw.QSplitter(QtCore.Qt.Vertical)
        self.horizontlSpliter.setHandleWidth(6)
        self.verticalSpliter.setHandleWidth(6)
        
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
        self.setStyleSheet(self.stylesheet % {'bgColor': color.name()})
    
    def cubeViewerUpdate(self):
        if self.animationOn :
            self.i += 1
            if self.i > 100:
                self.i = 0
            for x in range(self.cubeSize.getSize(Axis.X)):
                for y in range(self.cubeSize.getSize(Axis.Y)):
                    for z in range(self.cubeSize.getSize(Axis.Z)):
                        self.cubeViewer.modifier.changeColor(x,y,z, self.gradientViewer.getColorAt(self.i/100))
    
    def getCurrentColor(self):
        return QColor(250,250,250)
    
    def activeAnimation(self, active:bool):
        self.animationOn = active



class MainMenu(Qtw.QWidget):
    def __init__(self, newWindow_signal:QtCore.pyqtSignal, parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.newWindow_signal = newWindow_signal

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('MainMenu{background:white;}')
        layout = Qtw.QVBoxLayout(self)

        #self.startButton = WindowSelectionButton('Start', self.newWindow_signal, Editors_MainWidget.STARTER, self)
        #layout.addWidget(self.startButton)

        self.animatorButton = WindowSelectionButton('Animation', self.newWindow_signal, EditorIndex.ANIMATOR, self)
        layout.addWidget(self.animatorButton)

        self.equationButton = WindowSelectionButton('Equation mode', self.newWindow_signal, EditorIndex.EQUATION_INTERPRETER, self)
        layout.addWidget(self.equationButton)

        self.hueEditorButton = WindowSelectionButton('HUE mode', self.newWindow_signal, EditorIndex.HUE_EDITOR, self)
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


class OpenMenuButton(Qtw.QPushButton):
    def __init__(self, width:int, onClick, bgColor: QColor, parent=None):
        super().__init__(parent, clicked=onClick)

        self.setMinimumSize(60, 60)

        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
        self.setFixedWidth(width)

        self.bgColor = bgColor
        self.menuColor = QColor(255, 255, 255)
        self.shadowColor = QColor(200, 200, 220)
        self.shadowSize = 0.7

        self._animation = QtCore.QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.001,
            endValue=min(0.25, 1.0 - self.shadowSize),
            duration=500
        )
        self._animation.setEasingCurve(QtCore.QEasingCurve.OutElastic)

    def _animate(self, value):
        qss = """
            font: 75 14pt "Microsoft YaHei UI";
            font-weight: bold;
            text-align: left;
            color: rgb(255, 255, 255);
            border: 0px solid rgb(255, 255, 255);
        """
        grad = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {menuColor}, stop:{value1} {menuColor}, stop:{value2} {shadowColor}, stop: {value3} {bgColor}, stop: 1.0 {bgColor});".format(
            bgColor=self.bgColor.name(), menuColor=self.menuColor.name(), shadowColor=self.shadowColor.name(), value1=value-0.0001, value2=value, value3=value+self.shadowSize
        )
        qss += grad
        self.setStyleSheet(qss)

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class EditorIndex():
    ANIMATOR, EQUATION_INTERPRETER, HUE_EDITOR = range(3)

class StatusBar_Widget(Qtw.QWidget):
    def __init__(self, openMenu_signal:QtCore.pyqtSignal):
        super().__init__()
        self.openMenu_signal = openMenu_signal
        self.layout=Qtw.QHBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.addWidget(Qtw.QPushButton('Menu', self, clicked=lambda:self.openMenu_signal.emit(), objectName='menuButton'))
        self.layout.addWidget(Qtw.QLabel('ComPort cube'))


class Editors_MainWidget(Qtw.QWidget):
    newWindow_signal = QtCore.pyqtSignal(int)
    waitingCursor_signal = QtCore.pyqtSignal(bool)
    #ANIMATOR, EQUATION_INTERPRETER, HUE_EDITOR = range(3)

    def __init__(self, openMenu_signal:QtCore.pyqtSignal, mainApplication : Qtw.QApplication):
        super().__init__()
        self.cubeSize = CubeSize(8,8,8)
        self.mainApplication = mainApplication
        self.setObjectName('Custom_Main_Widget')
        self.backgroundColor = QColor(250,250,255)
        self.openMenu_signal = openMenu_signal

        ## Windows instantiation
        self.animator = Animator(self, self.waitingCursor_signal, self.cubeSize)
        #self.startBackground = StartingMenuBackground(self)
        self.equationInterpreter = EIWindow(self)
        self.hueEditor = HueEditor(self.cubeSize, self)

        ## Main menu
        self.drawerMenu = CDrawer(self)
        self.mainMenu = MainMenu(self.newWindow_signal, self)
        self.drawerMenu.setWidget(self.mainMenu)

        ## Windows manager
        '''
        self.windowList = Qtw.QListWidget()
        self.windowList.insertItem(self.STARTER, 'StarterBackground' )
        self.windowList.insertItem(self.ANIMATOR, 'Animator' )
        self.windowList.insertItem(self.EQUATION_INTERPRETER, 'EquationInterpreter')
        self.windowList.insertItem(self.HUE_EDITOR, 'HueEditor')
        '''
        self.windowStack = Qtw.QStackedWidget(self)
        self.windowStack.addWidget(self.animator)
        self.windowStack.addWidget(self.equationInterpreter)
        self.windowStack.addWidget(self.hueEditor)

        self.newWindow_signal.connect(self.changeWindow)
        self.waitingCursor_signal.connect(self.setWaitingCursor)

        self.statusBar = StatusBar_Widget(self.openMenu_signal)

        ## MainWidget layout
        self.mainLayout=Qtw.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.statusBar)
        self.mainLayout.addWidget(self.windowStack)      
        #self.mainLayout.addWidget(OpenMenuButton(max(30,self.screen().size().width()*0.03), self.openMainMenu, self.backgroundColor), 0, 0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)

        #self.waitingIcon = LoadingDialog(self)
        #self.waitingIcon.start()
        #self.waitingIcon.stop()

    def setWaitingCursor(self, activate : bool):
        
        if activate:
            self.mainApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            #self.waitingIcon.start()
        else:
            self.mainApplication.restoreOverrideCursor()
            #self.waitingIcon.stop()
    
    def openMainMenu(self):
        self.drawerMenu.show()
    
    def changeWindow(self, newIndexWindow):
        oldIndexWindow = self.windowStack.currentIndex()

        if oldIndexWindow == EditorIndex.HUE_EDITOR:                      ## HUE WINDOW OUT
            self.hueEditor.activeAnimation(False)

        if newIndexWindow == EditorIndex.ANIMATOR:                        ## ANIMATION WINDOW IN
            if not self.animator.isEmpty():
                self.windowStack.setCurrentIndex(newIndexWindow)
    
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
                self.windowStack.setCurrentIndex(newIndexWindow)
            self.animator.resizeEvent(None) #update positions

        if newIndexWindow == EditorIndex.EQUATION_INTERPRETER:            ## EQUATION WINDOW IN
            self.windowStack.setCurrentIndex(newIndexWindow)
        
        if newIndexWindow == EditorIndex.HUE_EDITOR:                      ## HUE WINDOW IN
            self.hueEditor.activeAnimation(True)
            self.windowStack.setCurrentIndex(newIndexWindow)

        self.drawerMenu.animationOut()
    
    def changeBackgroundColor(self, color:QColor):
        self.setStyleSheet("#Custom_Main_Widget {background: %s;}"%(color.name()))
        #self.startBackground.setBackgroundColor(color)
        self.animator.setBackgroundColor(color)
        self.hueEditor.setBackgroundColor(color)
        self.backgroundColor = color


class Menu_MainWidget(Qtw.QWidget):
    def __init__(self, mainApplication : Qtw.QApplication, newWindow_signal:QtCore.pyqtSignal):
        super().__init__()
        self.mainApplication = mainApplication
        self.setObjectName('Custom_Menu_Widget')
        self.backgroundColor = QColor(250,250,255)
        self.newWindow_signal = newWindow_signal

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)
        #self.mainLayout.addWidget(Qtw.QPushButton('Animator', self, clicked=lambda:print('Anim'), objectName='AnimationButton'),0,0)
        #self.mainLayout.addWidget(Qtw.QPushButton('HUE', self, clicked=lambda:print('HUE'), objectName='HUEButton'),0,1)
        #self.mainLayout.addWidget(Qtw.QPushButton('Equation', self, clicked=lambda:print('Equation'), objectName='EquationButton'),0,2)

        self.mainLayout.addWidget(WindowSelectionButton('Animator',self.newWindow_signal, EditorIndex.ANIMATOR),0,0)
        self.mainLayout.addWidget(WindowSelectionButton('HUE',self.newWindow_signal, EditorIndex.HUE_EDITOR),0,1)
        self.mainLayout.addWidget(WindowSelectionButton('Equation',self.newWindow_signal, EditorIndex.EQUATION_INTERPRETER),0,2)


class MainWindow(Qtw.QMainWindow):
    openMenu_signal = QtCore.pyqtSignal()

    def __init__(self, mainApplication : Qtw.QApplication, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("CubAnimate")
        self.setObjectName('Custom_Main_Window')
        self.mainWidget = Editors_MainWidget(self.openMenu_signal, mainApplication)
        self.mainWidget.newWindow_signal.connect(lambda i: self.closeMenu())
        self.menuWidget = Menu_MainWidget(mainApplication, self.mainWidget.newWindow_signal)
        self.windowStack = Qtw.QStackedWidget(self)
        self.windowStack.addWidget(self.mainWidget)
        self.windowStack.addWidget(self.menuWidget)
        self.setCentralWidget(self.windowStack)
    
        self.editorsIndex = self.windowStack.indexOf(self.mainWidget)
        self.menuIndex = self.windowStack.indexOf(self.menuWidget)

        self.backgroundColor = QColor(250,250,255)
        self.changeBackgroundColor(self.backgroundColor)
        self.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.centralWidget().setContentsMargins(0,0,0,0)

        self.openMenu_signal.connect(self.openMenu)
        self.openMenu()
        self.setBaseSize(self.screen().size())
    
    def openMenu(self):
        self.windowStack.setCurrentIndex(self.menuIndex)
    
    def closeMenu(self):
        self.windowStack.setCurrentIndex(self.editorsIndex)

    def changeBackgroundColor(self, color : QColor):
        self.setStyleSheet("#Custom_Main_Window {background:%s;}"%(color.name()))
        self.mainWidget.changeBackgroundColor(color)
