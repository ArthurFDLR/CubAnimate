from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QPixmap, QKeySequence

from ..common.CubeViewer3D import CubeViewer3DInteract
from ..common.CToolBox.CToolBox import CToolBox_Animator
from ..common.CTypes import Axis, CubeSize
from .CCubeViewerSliced import CCubeViewerSliced
from .CAnimationTimeline import AnimationList, CubeLEDFrame
from .CFramelessDialog import NewAnimationDialog


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

    def __init__(self, parent, waitingCursor_signal:QtCore.pyqtSignal, cubeSizeInit:CubeSize = CubeSize(8,8,8)):
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

        self.waitingCursor_signal = waitingCursor_signal

    def notSaved(self):
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

        self.waitingCursor_signal.emit(True)

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
        
        self.waitingCursor_signal.emit(False)

    
    def addFrame(self) -> CubeLEDFrame:
        """ Create and add a new frame to the animation."""
        num = len(self.animationViewer.frameList)
        frameWidth = self.animatorWidth*0.9
        self.animationViewer.frameList.append(CubeLEDFrame('#{}'.format(num+1), self.cubeSize,frameWidth , self.animationViewer.timeLine, self.animationViewer))
        self.animationViewer.changeFrameSelected(self.animationViewer.frameList[num])
        self.animationViewer.frameList[num].setIllustration(self.blankIllustration)
        #self.cubeViewer.newFrameAnimation()
        self.animationSaved = False
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
        
        return self.animationSaved
    
    def changeCubeSize(self, cubeSize : CubeSize):
        self.cubeSize = cubeSize
        self.cubeViewer.changeCubeSize(cubeSize)
        self.cubeSliced.changeCubeSize(cubeSize)
    
    def isSaved(self) -> bool:
        return self.animationSaved
    
    def createAnimation(self, cubeSize : CubeSize, name:str):
        self.animationViewer.clearAllFrames()
        self.animationName = name
        self.changeCubeSize(cubeSize)
        self.noAnimationEdited = False
        self.addFrame()
        self.animationSaved = True
    
    def isEmpty(self):
        return self.noAnimationEdited
    
    def openAnimation(self):
        newAnimDialog = NewAnimationDialog(self)
        if newAnimDialog.exec_(): #If pop-up not exited
            #self.waitingCursor_signal.emit(True)
            '''
            if newAnimDialog.createNewAnimation(): #Create a new animation
                print('Create new animation')
                self.animator.createAnimation(self.cubeSize,'New animation')
            '''
            if newAnimDialog.loadAnimation(): #Load an existing animation
                print('Load animation: ' + newAnimDialog.getFileLocation())
                self.animator.changeCubeSize(self.cubeSize)
                self.animator.loadAnimation(newAnimDialog.getFileLocation())
            #self.waitingCursor_signal.emit(False)
            #self.windowStack.setCurrentIndex(newIndexWindow)
        #self.animator.resizeEvent(None) #update positions
    
    def loadAnimation(self, fileLocation : str):
        self.animationViewer.clearAllFrames()
        file = open(fileLocation,'r')
        for line in file:
            if line[0] == '#':
                self.loadFrame(line[:-1])
        file.close()
        self.noAnimationEdited = False
        self.animationSaved = True
    
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