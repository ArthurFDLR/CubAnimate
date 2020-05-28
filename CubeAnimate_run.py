from CubeAnimate_mainWindow import MainWindow
from PyQt5 import QtWidgets
import sys
import src.resources

if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)
    mainWid = MainWindow(app)
    mainWid.showMaximized()
    sys.exit(app.exec_())