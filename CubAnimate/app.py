from .CubeAnimate_mainWindow import MainWindow
from PyQt5 import QtWidgets
import sys
from .resources import resources

def run():
    app = QtWidgets.QApplication(sys.argv)
    mainWid = MainWindow(app)
    mainWid.showMaximized()
    sys.exit(app.exec_())