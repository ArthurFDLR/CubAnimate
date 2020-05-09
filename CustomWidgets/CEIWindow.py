### EQUATION INTERPRETER WIDGET ###


## Importations ##
# Imports modules available for download on the web #
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets as Qtw
from PyQt5.QtCore import pyqtSlot, QSize, QObject
from PyQt5.QtGui import QVector3D, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton, QAction, QLineEdit, QMessageBox, QHBoxLayout, QShortcut
from PyQt5.QtDataVisualization import Q3DSurface, QSurface3DSeries, QSurfaceDataItem, QSurfaceDataProxy, QValue3DAxis

from numpy import *
from Equation import *
 
# Imports homemade modules #
try:
    from CustomWidgets.CTypes import * 
except: 
    from CTypes import *


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

class EIWindow(Qtw.QWidget):
    def __init__(self,parent=None):
        super(Qtw.QWidget, self).__init__(parent)

        self.setWindowTitle("Equation interpreter")

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        # Create label #
        self.mainlabel = Qtw.QLabel("Type your equation here, must be a function of (x,y):")
        self.mainLayout.addWidget(self.mainlabel,0,0)

        # Create textbox #
        self.textbox = QLineEdit(self)
        self.mainLayout.addWidget(self.textbox,1,0)

        # Create LaTeX viewer # 
        self.viewer = Qtw.QLabel()
        self.viewer.setPixmap(mathTex_to_QPixmap('$ ... $', 15))
        self.mainLayout.addWidget(self.viewer,2,0)

        # Create graph visualizer #
        self.cubesize = CubeSize(4,8,8)
        self.graph = Q3DSurface()
        self.screenSize = self.graph.screen().size()
        self.graph.setAspectRatio(2.0)
        self.graph.setAxisX(QValue3DAxis())
        self.graph.setAxisY(QValue3DAxis())
        self.graph.setAxisZ(QValue3DAxis())
        self.graph.axisX().setTitle("Depth")
        self.graph.axisY().setTitle("Height")
        self.graph.axisZ().setTitle("Width")
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

        # Connect the enter key to button #
        self.buttonShortcut = QShortcut(QKeySequence(QtCore.Qt.Key_Return), self.button)
        self.buttonShortcut.activated.connect(self.on_click)

    
    @pyqtSlot()
    def on_click(self):
        try: 
        # Displays the function as LaTeX  #
            f = Expression(self.textbox.text(),["x","y","t"])
            self.viewer.setPixmap(mathTex_to_QPixmap('$' + str(f) + '$',15))
        # Displays the graph #
            self.plot3D(f,self.cubesize)
            self.graph.addSeries(self.functionSeries)
        except:
        # If the function is not a valid function, let the user know and reset the graph [TO DO] # 
            self.viewer.setPixmap(mathTex_to_QPixmap('Invalid function',10))
            self.graph.removeSeries(self.functionSeries)

    def plot3D(self,func,csize:CubeSize,nbsamples:list=[50,50]):
        ''' E/ func: funtion to be diplayed on screen ; takes 3 parameters (x,y,t) with t optional (static animation)
            E/ csize: list containing 3 integers (sizeX,sizeY,sizeZ) to know the boundaries 
            E/ nbsamples (OPTIONAL) : list containing 2 integers (sampleX,sampleZ) to define the resolution of the graph
            S/ No output, sets the right data in the functionProxy to display the graph '''
        valuesArray = []
        stepX=csize.getSize(Axis.X)/(nbsamples[0]-2)
        stepZ=csize.getSize(Axis.Z)/(nbsamples[1]-2)
        for i in range(nbsamples[1]):
            currentRow=[]
            z=min(csize.getSize(Axis.Z)-1,i*stepZ)
            for j in range(nbsamples[0]):
                x=min(csize.getSize(Axis.X)-1,j*stepX)
                y=func(x,z)
                currentRow.append(QSurfaceDataItem(QVector3D(x,y,z)))
            valuesArray.append(currentRow)
        self.functionProxy.resetArray(valuesArray)      
           


## What is actually running ##

if __name__ == '__main__':    
    app = Qtw.QApplication(sys.argv)
    mainWid = EIWindow()
    mainWid.showMaximized()
    sys.exit(app.exec_())

## TO-DO list ##
# Allow functions of time : display a graph evolving in time
# Add a "toolbox" that allows to increase graph resolution / adapt function to cube / input the cube size manually (??s)
# Export function to discrete LED configuration
# Enable color settings (choose a palette)
# Layout coherent with the rest of the app

