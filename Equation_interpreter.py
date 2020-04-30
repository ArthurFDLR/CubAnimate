### EQUATION INTERPRETER WIDGET ###

## Importations ##
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets as Qtw
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton, QAction, QLineEdit, QMessageBox

from numpy import *
from Equation import *

## Add functions/constants/operators to the list of those that can be displayed ##
'''Already implemented in Equation module : floor, ceil, round, sin, cos, tan, im, re, sqrt
   Already implemented in Equation module : pi, e, Inf, NaN
   Already implemented in Equation module : +, -, *, /, ^, **, &, |, </>, &|, |&, ==, =, ~, !~, <>, ><, <=, >=, <~, >~, ~<, ~>, !'''

from Equation.util import addFn, addConst, addOp

addFn('exp',"exp({0:s})","\\exp\\left({0:s}\\right)",1,exp)
addFn('ln',"ln({0:s})","\\ln\\left({0:s}\\right)",1,log)
addFn('log',"log({0:s})","\\log\\left({0:s}\\right)",1,log10)

## Useful functions ##

def mathTex_to_QPixmap(mathTex, fs):

    #---- set up a mpl figure instance ----

    fig = Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvas(fig))
    
    renderer = fig.canvas.get_renderer()

    #---- plot the mathTex expression ----

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')

    t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize=fs)

    #---- fit figure size to text artist ----
    fwidth, fheight = fig.get_size_inches()

    fig_bbox = fig.get_window_extent(renderer)

    text_bbox = t.get_window_extent(renderer)

    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height

    fig.set_size_inches(tight_fwidth, tight_fheight)

    #---- convert mpl figure to QPixmap ----

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

        self.viewer = Qtw.QLabel("Hello")
        self.viewer.setPixmap(mathTex_to_QPixmap('$ ... $', 15))
        self.mainLayout.addWidget(self.viewer,1,0)

        # Create textbox
        self.textbox = QLineEdit(self)
        self.mainLayout.addWidget(self.textbox,0,0)
        
        # Create a button in the window
        self.button = QPushButton('Display equation', self)
        self.mainLayout.addWidget(self.button,0,1)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
    
    @pyqtSlot()
    def on_click(self):
        f = Expression(self.textbox.text(),["x","y","z","t"])
        self.viewer.setPixmap(mathTex_to_QPixmap('$' + str(f) + '$',25))

## What is actually running ##

if __name__ == '__main__':    
    app = Qtw.QApplication(sys.argv)
    mainWid = MainWindow()
    mainWid.show()
    sys.exit(app.exec_())
