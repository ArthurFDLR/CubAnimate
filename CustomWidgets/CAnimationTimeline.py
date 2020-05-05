
from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap

from CustomWidgets.CTypes import Axis, CubeSize, CubeLEDFrame_DATA

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
    
    def encodeData(self) -> str:
        """ Generate data line representing the frame for creating .anim file """
        return self.frameData.encode()
    
    def decodeData(self, dataLine : str):
        """ Generate data line representing the frame for creating .anim file """
        self.frameData.decode(dataLine)
        


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
        self.cubeSize = cubeSize
        self.listWidth = size
        self.timeLine = Qtw.QListWidget()
        #self.copyCache = CubeLEDFrame("null",self.cubeSize,self.listWidth,None,self)
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

        ## Menu
        self._contextMenu = Qtw.QMenu(self)
        self._contextMenu.addAction('Delete', self.menuDeleteFrame)
        #self._animation = QtCore.QPropertyAnimation(self._contextMenu, b'geometry', self, easingCurve=QtCore.QEasingCurve.Linear, duration=100)
        
    def changeFrameSelected(self, frame : CubeLEDFrame):
        self.timeLine.setCurrentItem(frame)
    
    def contextMenuEvent(self, event):
        '''
        pos = event.globalPos()
        size = self._contextMenu.sizeHint()
        x, y, w, h = pos.x(), pos.y(), size.width(), size.height()
        self._animation.stop()
        self._animation.setStartValue(QtCore.QRect(x, y, 0, h))
        self._animation.setEndValue(QtCore.QRect(x, y, w, h))
        self._animation.start()
        '''
        self._contextMenu.popup(event.globalPos())
    
    def menuDeleteFrame(self):
        if len(self.frameList) > 1:
            index = self.frameList.index(self.timeLine.selectedItems()[0])
            self.frameList.pop(index)
            self.timeLine.takeItem(index)
            self.timeLine.setCurrentItem(self.frameList[min(index,len(self.frameList)-1)])
            for i in range(index,len(self.frameList)):
                print(i)
                self.frameList[i].frame.setTitle("#{}".format(i+1))
