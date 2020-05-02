### EQUATION INTERPRETER WIDGET ###

## Importations ##
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets as Qtw
from PyQt5.QtCore import pyqtSlot, QSize, QObject
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton, QAction, QLineEdit, QMessageBox, QHBoxLayout
from PyQt5.QtDataVisualization import Q3DSurface, QSurface3DSeries, QSurfaceDataItem, QSurfaceDataProxy, QValue3DAxis

from numpy import *
from Equation import *

## Add functions/constants/operators to the list of those that can be displayed using the Equation module ##
'''Already implemented functions : floor, ceil, round, sin, cos, tan, im, re, sqrt
   Already implemented constants : pi, e, Inf, NaN
   Already implemented operators : +, -, *, /, ^, **, &, |, </>, &|, |&, ==, =, ~, !~, <>, ><, <=, >=, <~, >~, ~<, ~>, !'''

from Equation.util import addFn, addConst, addOp

addFn('exp',"exp({0:s})","\\exp\\left({0:s}\\right)",1,exp)
addFn('ln',"ln({0:s})","\\ln\\left({0:s}\\right)",1,log)
addFn('log',"log({0:s})","\\log\\left({0:s}\\right)",1,log10)
addFn('arccos',"arccos({0:s})","\\arccos\\left({0:s}\\right)",1,arccos)
addFn('arcsin',"arcsin({0:s})","\\arcsin\\left({0:s}\\right)",1,arcsin)

## Useful functions ##

def mathTex_to_QPixmap(mathTex, fs):
    ''' E/ mathTEx : The formula to be displayed on screen in LaTeX
        E/ fs : The desired font size 
        S/ qpixmap : The image to be displayed in Qpixmap format '''
    # Set up a mpl figure instance #
    fig = Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvas(fig))
    renderer = fig.canvas.get_renderer()

    # Plot the mathTex expression #
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')
    t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize=fs)

    # Fit figure size to text artist #
    fwidth, fheight = fig.get_size_inches()
    fig_bbox = fig.get_window_extent(renderer)
    text_bbox = t.get_window_extent(renderer)
    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height
    fig.set_size_inches(tight_fwidth, tight_fheight)

    # Convert mpl figure to QPixmap #
    buf, size = fig.canvas.print_to_buffer()
    qimage = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, size[0], size[1],
                                                  QtGui.QImage.Format_ARGB32))
    qpixmap = QtGui.QPixmap(qimage)

    return qpixmap

    
## Useful classes ## 

class MainWindow(Qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Equation interpreter")

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.viewer = Qtw.QLabel()
        self.viewer.setPixmap(mathTex_to_QPixmap('$ ... $', 15))
        self.mainLayout.addWidget(self.viewer,2,0)

        # Create label #
        self.mainlabel = Qtw.QLabel("Type your equation here:")
        self.mainLayout.addWidget(self.mainlabel,0,0)

        # Create textbox #
        self.textbox = QLineEdit(self)
        self.mainLayout.addWidget(self.textbox,1,0)

        # Create graph visualizer #
        self.cubesize:list = [8, 8, 8]
        self.graph = Q3DSurface()
        self.screenSize = self.graph.screen().size()
        self.graph.setAxisX(QValue3DAxis())
        self.graph.setAxisY(QValue3DAxis())
        self.graph.setAxisZ(QValue3DAxis())
        self.graph.axisX().setTitle("X - Depth")
        self.graph.axisY().setTitle("Y - Width")
        self.graph.axisZ().setTitle("Z - Height")
        self.functionProxy = QSurfaceDataProxy()
        self.functionSeries = QSurface3DSeries(self.functionProxy)
        self.graphvisualizer = Qtw.QWidget.createWindowContainer(self.graph)
        self.graphvisualizer.setMinimumSize(QSize(self.screenSize.width()/3, self.screenSize.height()/2))
        self.mainLayout.addWidget(self.graphvisualizer,3,0)
        
        # Create a button in the window #
        self.button = QPushButton('Display equation', self)
        self.mainLayout.addWidget(self.button,1,1)

        # Connect button to function on_click #
        self.button.clicked.connect(self.on_click)

        # Connect the enter key to funtion on_click #
        ''' a faire'''

    
    @pyqtSlot()
    def on_click(self):
        # Displays the function as LaTeX #
        f = Expression(self.textbox.text(),["x","y","t"])
        self.viewer.setPixmap(mathTex_to_QPixmap('$' + str(f) + '$',15))
        # Displays the graph #
        self.plot3D(f,self.cubesize)
        self.graph.addSeries(self.functionSeries)

    def plot3D(self,func,csize:list,nbsamples=[50,50,50]):
        ''' E/ func: funtion to be diplayed on screen ; takes 3 parameters (x,y,t) with t optional (static animation)
            E/ csize: list containing 3 integers (sizeX,sizeY,sizeZ) to know the boundaries 
            E/ nbsamples (OPTIONAL) : list containing 3 integers (sampleX,sampleY,sampleZ) to define the resolution of the graph
            S/ No output, gives the command to display the graph '''
        valuesArray = []
        XArray = linspace(0., csize[0]-1, nbsamples[0])
        YArray = linspace(0., csize[1]-1, nbsamples[1])
        graphHeight = csize[2]
        for i in range(nbsamples[1]):
            currentRow=[]
            for j in range(nbsamples[0]):
                z=func(XArray[i],YArray[j])
                currentRow.append(QSurfaceDataItem(QVector3D(XArray[i],YArray[j],z)))
            valuesArray.append(currentRow)
        self.functionProxy.resetArray(valuesArray)
        self.graph.addSeries(self.functionSeries)

        


## What is actually running ##

if __name__ == '__main__':    
    app = Qtw.QApplication(sys.argv)
    mainWid = MainWindow()
    mainWid.show()
    sys.exit(app.exec_())
