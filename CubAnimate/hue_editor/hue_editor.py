from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor

from ..common.CTypes import Axis, CubeSize
from ..common.CubeViewer3D import CubeViewer3DInteract
from ..common.CToolBox.CToolBox import CToolBox_HUE
from .CGradientDesigner import GradientDesigner

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
        self.toolBox = CToolBox_HUE(False, False, self)
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
        self.verticalSpliter.setStretchFactor(1,1)

        self.mainLayout.addWidget(self.verticalSpliter)
    
    def setBackgroundColor(self, color:QColor):
        self.setStyleSheet(self.stylesheet % {'bgColor': color.name()})
        self.cubeViewer.setBackgroundColor(color)
    
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

    def saveAnimation(self):
        print('Save HUE')
        return True
    
    def isSaved(self):
        print('File is saved')
        return True
    
    def openAnimation(self):
        print("Open HUE")