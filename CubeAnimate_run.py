from CubeAnimate_mainWindow import MainWindow
from PyQt5 import QtCore,QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
#app.setStyleSheet(open("./design_GUI.css").read())

mainWin = QtWidgets.QMainWindow()
mainWin.setWindowTitle("AnimCube")
mainWid = MainWindow()
mainWin.setCentralWidget(mainWid)
mainWin.showMaximized()
sys.exit(app.exec_())