from CubeAnimate_mainWindow import MainWindow
from PyQt5 import QtWidgets
import sys
import qdarkstyle

#app.setStyleSheet(open("./design_GUI.css").read())


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    mainWid = MainWindow()
    mainWid.showMaximized()
    sys.exit(app.exec_())