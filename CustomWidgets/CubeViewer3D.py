from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon
from PyQt5.QtDataVisualization import (Q3DCamera, Q3DTheme, Q3DScatter,
                                       QAbstract3DGraph, QAbstract3DSeries, QScatter3DSeries,
                                       QScatterDataItem, QScatterDataProxy, QCustom3DItem)

from CustomWidgets.CTypes import CubeSize, Axis

class ScatterDataModifierInteract(QtCore.QObject):
    def __init__(self, interactive, cubeSize : CubeSize, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, scatter, parent):
        super(ScatterDataModifierInteract, self).__init__()

        self.parent = parent
        self.cubeSize = cubeSize
        self.interactive = interactive

        if self.interactive :
            self.eraseColor_signal = eraseColor_signal
            self.newColor_signal = newColor_signal
            self.eraseColor_signal.connect(self.eraseColor)
            self.newColor_signal.connect(self.changeColor)

        self.nullColor = QColor(255,255,255)
        self.nullColor.setAlpha(100)

        ## Graphics
        self.m_graph = scatter
        self.m_fontSize = 40.0
        
        self.m_graph.setSelectionMode(QAbstract3DGraph.SelectionItem)
        self.m_graph.activeTheme().setType(Q3DTheme.ThemeDigia)
        font = self.m_graph.activeTheme().font()
        font.setPointSize(self.m_fontSize)
        self.m_graph.activeTheme().setFont(font)
        self.m_graph.activeTheme().setColorStyle(Q3DTheme.ColorStyleUniform)
        self.m_graph.activeTheme().setSingleHighlightColor(self.nullColor)
        self.m_graph.activeTheme().setBackgroundEnabled(False)
        self.m_graph.setShadowQuality(QAbstract3DGraph.ShadowQualitySoftLow)

        ## Camera
        self.m_graph.scene().activeCamera().setCameraPreset(Q3DCamera.CameraPresetIsometricRight)
        self.m_graph.scene().activeCamera().setCameraPosition(300,20)
        self.m_graph.scene().activeCamera().setZoomLevel(110)

        ## Axis
        self.m_graph.axisX().setTitle("Depth") # x-axis
        self.m_graph.axisX().setTitleVisible(True)
        self.m_graph.axisX().setSegmentCount(self.cubeSize.getSize(Axis.X)-1)
        self.m_graph.axisX().setLabelFormat("%i")

        self.m_graph.axisY().setTitle("Height")  # z-axis (z-axis and y-axis reversed to match representations)
        self.m_graph.axisY().setTitleVisible(True)
        self.m_graph.axisY().setSegmentCount(self.cubeSize.getSize(Axis.Y)-1)
        self.m_graph.axisY().setLabelFormat("%i")

        self.m_graph.axisZ().setTitle("Width")  # y-axis (z-axis and y-axis reversed to match representations)
        self.m_graph.axisZ().setTitleVisible(True)
        self.m_graph.axisZ().setSegmentCount(self.cubeSize.getSize(Axis.Z)-1)
        self.m_graph.axisZ().setLabelFormat("%i")

        ## Instantiate LED representation
        self.m_graph.selectedSeriesChanged.connect(self.ledClicked)
        self.matrixLEDserie = []
        self.instantiateLED()
    
    def instantiateLED(self):
        self.matrixLEDserie.clear()
        count = 0
        for i in range(self.cubeSize.getSize(Axis.X)):
            self.matrixLEDserie.append([])
            for j in range(self.cubeSize.getSize(Axis.Y)):
                self.matrixLEDserie[i].append([])
                for k in range(self.cubeSize.getSize(Axis.Z)):
                    
                    item = QScatterDataItem(QVector3D(i+1,k+1,j+1)) # z-axis and y-axis reversed to match representations, purely graphic

                    self.matrixLEDserie[i][j].append(QScatter3DSeries(QScatterDataProxy()))

                    #self.matrixLEDserie[i][j][k].setItemLabelFormat("@xTitle: @xLabel @yTitle: @yLabel @zTitle: @zLabel")
                    self.matrixLEDserie[i][j][k].setMeshSmooth(True)
                    self.matrixLEDserie[i][j][k].setName(str(i) + " " + str(j) + " " + str(k))
                    
                    self.m_graph.addSeries(self.matrixLEDserie[i][j][k])
                    
                    self.m_graph.seriesList()[count].dataProxy().addItem(item)
                    self.m_graph.seriesList()[count].setBaseColor(self.nullColor)
                    self.m_graph.seriesList()[count].setItemSize(1.2/self.cubeSize.max())
                    
                    count = count+1
    
    def changeCubeSize(self, cubeSize : CubeSize):
        self.cubeSize = cubeSize
        for dataSeries in self.m_graph.seriesList():
            self.m_graph.removeSeries(dataSeries)
        self.m_graph.axisX().setSegmentCount(self.cubeSize.getSize(Axis.X)-1)
        self.m_graph.axisY().setSegmentCount(self.cubeSize.getSize(Axis.Y)-1)
        self.m_graph.axisZ().setSegmentCount(self.cubeSize.getSize(Axis.Z)-1)
        self.instantiateLED()

    def ledClicked(self, serie : QAbstract3DSeries): #Colored the led if not already set to the given color, erase it otherwise
        if self.interactive :
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
        self.matrixLEDserie[posX][posY][posZ].setBaseColor(color)
    
    def eraseColor(self, posX :int, posY :int, posZ :int):
        self.matrixLEDserie[posX][posY][posZ].setBaseColor(self.nullColor)

    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()



class CubeViewer3DInteract(Qtw.QWidget):
    def __init__(self, interactive, cubeSize : CubeSize, newColor_signal:QtCore.pyqtSignal, eraseColor_signal:QtCore.pyqtSignal, parent):
        super(Qtw.QWidget, self).__init__(parent)
        
        self.parent = parent
        self.graph = Q3DScatter()
        self.graph.setAspectRatio(1.0)
        self.currentColor = self.parent.getCurrentColor()
        self.onWidget = False
        self.imageZoom = 160
        self.screenSize = self.graph.screen().size()
        
        self.container = Qtw.QWidget.createWindowContainer(self.graph)
        self.container.setMinimumSize(QtCore.QSize(self.screenSize.width() /5, self.screenSize.height() / 5))
        self.container.setMaximumSize(self.screenSize)
        self.container.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
        self.container.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.layout = Qtw.QGridLayout(self)
        self.layout.addWidget(self.container, 0,0)

        self.modifier = ScatterDataModifierInteract(interactive, cubeSize, newColor_signal, eraseColor_signal, self.graph, self)
    
    def getCurrentColor(self) -> QColor :
        return self.parent.getCurrentColor()
    
    def getCurrentFramePixmap(self, size : QtCore.QSize) -> QPixmap :

        xRot = self.graph.scene().activeCamera().xRotation()
        yRot = self.graph.scene().activeCamera().yRotation()
        zoom = self.graph.scene().activeCamera().zoomLevel()
        self.graph.scene().activeCamera().setCameraPosition(300,10)
        self.graph.scene().activeCamera().setZoomLevel(self.imageZoom)

        image = self.graph.renderToImage(2,size)

        self.graph.scene().activeCamera().setCameraPosition(xRot,yRot)
        self.graph.scene().activeCamera().setZoomLevel(zoom)

        return QPixmap.fromImage(image)
    
    def newFrameAnimation(self):
        self.anim = QtCore.QPropertyAnimation(self.graph.scene().activeCamera(), b"xRotation")
        self.anim.setDuration(2500)
        self.anim.setStartValue(float(0))
        self.anim.setEndValue(float(100))
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutExpo)
        self.anim.start()

    def changeCubeSize(self, cubeSize : CubeSize):
        self.modifier.changeCubeSize(cubeSize)
    
    def getDisplayedColor(self, x:int, y:int, z:int) -> QColor:
        return self.modifier.matrixLEDserie[x][y][z].baseColor()
    
    def setBackgroundColor(self, color:QColor):
        self.graph.activeTheme().setWindowColor(color)

