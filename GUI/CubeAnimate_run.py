from CubeAnimate_mainWindow import MainWindow
from PyQt5 import QtWidgets
import sys
import qdarkstyle


Stylesheet = """
QLineEdit, QSpinBox {
    border: 1px solid #cbcbcb;
    border-radius: 2px;
    background: white;
    min-width: 31px;
    min-height: 21px;
}
QLineEdit:focus, QSpinBox:focus {
    border-color: rgb(139, 173, 228);
}
QLabel {
    color: #a9a9a9;
}
QPushButton {
    border: 1px solid #cbcbcb;
    border-radius: 2px;
    min-width: 21px;
    max-width: 21px;
    min-height: 21px;
    max-height: 21px;
    font-size: 14px;
    background: white;
}
QToolButton {
    border: 1px solid #cbcbcb;
    border-radius: 2px;
    min-width: 21px;
    max-width: 21px;
    min-height: 21px;
    max-height: 21px;
    font-size: 14px;
    background: white;
}
QPushButton:hover {
    border-color: rgb(139, 173, 228);
}
QPushButton:pressed {
    border-color: #cbcbcb;
}

CColorStraw {
    border: none;
    font-size: 18px;
    border-radius: 0px;
}
QPushButton:hover {
    color: rgb(139, 173, 228);
}
QPushButton:pressed {
    color: #cbcbcb;
}

#confirmButton, #cancelButton {
    min-width: 70px;
    min-height: 30px;
}
#cancelButton:hover {
    border-color: rgb(255, 133, 0);
}

QTabWidget::pane {
    border: none;
}
QTabBar::tab {
    padding: 3px 6px;
    color: rgb(100, 100, 100);
    background: transparent;
}
QTabBar::tab:hover {
    color: black;
}
QTabBar::tab:selected {
    color: rgb(139, 173, 228);
    border-bottom: 2px solid rgb(139, 173, 228);
}

QTabBar::tab:!selected {
    border-bottom: 2px solid transparent;
}

QScrollBar:vertical {
    max-width: 10px;
    border: none;
    margin: 0px 0px 0px 0px;
}

QScrollBar::handle:vertical {
    background: rgb(220, 220, 220);
    border: 1px solid rgb(207, 207, 207);
    border-radius: 5px;
}
"""


if __name__ == '__main__':    
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    #app.setStyleSheet(Stylesheet)
    mainWid = MainWindow()
    mainWid.showMaximized()
    sys.exit(app.exec_())