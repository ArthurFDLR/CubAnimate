from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QMimeData, QRect
from PyQt5.QtGui import QPalette, QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget,\
    QGraphicsDropShadowEffect, QPushButton, QGridLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog
from PyQt5.QtSvg import QSvgWidget



class DropArea(QPushButton):
    Stylesheet = """
    QLineEdit, QLabel, QTabWidget {
        font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif;
    }

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
    QPushButton {
        border: 1px solid #cbcbcb;
        border-radius: 10px;
        font-size: 16px;
        background: white;
    }
    QPushButton:hover {
        border-color: rgb(139, 173, 228);
    }
    QPushButton:pressed {
        color: #cbcbcb;
    }
    """

    changed = pyqtSignal(QMimeData)

    def __init__(self, loadNewAnimation_signal:pyqtSignal, parent = None):
        super(DropArea, self).__init__(parent, cursor=Qt.PointingHandCursor, toolTip='Import animation', clicked= self.searchFile)

        self.loadNewAnimation_signal = loadNewAnimation_signal

        self.setMinimumSize(self.screen().size() / 4)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.clear()
        self.setStyleSheet(self.Stylesheet)

        layout = QGridLayout(self)
        self.setLayout(layout)
        
        self.svgWidget = QSvgWidget('drop.svg')
        self.svgWidget.setFixedSize(200,200)
        layout.addWidget(self.svgWidget)
        

    def dragEnterEvent(self, event):
        self.setBackgroundRole(QPalette.Highlight)

        if self.isAnimation(event.mimeData()):
            event.acceptProposedAction()
        self.changed.emit(event.mimeData())

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if self.isAnimation(mimeData):
            self.loadNewAnimation_signal.emit(mimeData.text()[8:])
        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()
        
    def dragLeaveEvent(self, event):
        self.clear()
        event.accept()

    def clear(self):
        self.setBackgroundRole(QPalette.Dark)
        self.changed.emit(None)
    
    def isAnimation(self, file:QMimeData):
        if file.hasText():
            return file.text()[-5:] == '.anim'
        return False

    def resizeEvent(self, event):
        h = self.size().height()
        w = self.size().width()
        self.svgWidget.setFixedSize(min(h,w)*0.8,min(h,w)*0.8)
    
    def searchFile(self):
        directoryName, fileExtension = QFileDialog.getOpenFileName(self, 'Load animation',"./","Animation Files (*.anim)")
        self.loadNewAnimation_signal.emit(directoryName)



class NewAnimationDialog(QDialog):
    
    Stylesheet = """
    #Custom_Widget {
        background: white;
        border-radius: 10px;
    }
    #closeButton {
        min-width: 36px;
        min-height: 36px;
        font-family: "Webdings";
        qproperty-text: "r";
        border-radius: 10px;
    }
    #closeButton:hover {
        color: white;
        background: red;
    }
    QLabel {
        color: #a9a9a9;
        font-size: 20px;
    }
    """
    loadNewAnimation_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(NewAnimationDialog, self).__init__(*args, **kwargs)

        self.fileLocation = ''
        self.createAnimation = True

        self.loadNewAnimation_signal.connect(self.setFileLocation)

        self.setObjectName('Custom_Dialog')
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(self.Stylesheet)
        self.initUi()

        # 添加阴影
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setOffset(0, 0)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)

    def initUi(self):
        layout = QVBoxLayout(self)
        # 重点： 这个widget作为背景和圆角
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')
        layout.addWidget(self.widget)

        # 在widget中添加ui
        layout = QGridLayout(self.widget)
        layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 0)
        layout.addWidget(QLabel('Load animation', self), 0, 1)
        layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)
        layout.addWidget(QPushButton(
            'r', self, clicked=self.reject, objectName='closeButton'), 0, 3)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding), 2, 0)
        
        self.dropZone = DropArea(self.loadNewAnimation_signal, self)
        layout.addWidget(self.dropZone, 1, 0, 1, 4)

        layout.addWidget(QPushButton('Create animation', self, clicked=self.accept,cursor=Qt.PointingHandCursor, toolTip='Create animation'), 2, 0, 1, 4)
    
    def sizeHint(self):
        return self.screen().size() / 3
    
    def getFileLocation(self) -> str:
        return self.fileLocation
    
    def setFileLocation(self, loc:str):
        self.fileLocation = loc
        self.createAnimation = False
        self.accept()
    
    def createNewAnimation(self) -> bool:
        return self.createAnimation
    
    def loadAnimation(self) -> bool:
        return len(self.fileLocation)>0
    