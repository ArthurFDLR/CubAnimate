from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QMimeData, QRect, QThread
from PyQt5.QtGui import QPalette, QPixmap, QIcon, QColor, QPainter
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget,\
    QGraphicsDropShadowEffect, QPushButton, QGridLayout, QSpacerItem, QSizePolicy, QLabel, QFileDialog
from PyQt5.QtSvg import QSvgWidget

import sys
from math import ceil


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
        border: 2px solid #cbcbcb;
        border-radius: 10px;
        border-style: dashed;
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
        
        self.svgWidget = QSvgWidget(':/icons/DropZone.svg')
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

    #Custom_Button {
    border: 1px solid rgb(200,200,200);
    border-radius: 10px;
    }
    #Custom_Button:hover {
        border-color: rgb(139, 173, 228);
    }
    #Custom_Button:pressed {
        color: #cbcbcb;
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
        self.layout = QVBoxLayout(self)
        # 重点： 这个widget作为背景和圆角
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')
        self.layout.addWidget(self.widget)

        # 在widget中添加ui
        self.layout = QGridLayout(self.widget)
        self.layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 0)
        self.layout.addWidget(QLabel('Load animation', self), 0, 1)
        self.layout.addItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 2)
        self.layout.addWidget(QPushButton(
            'r', self, clicked=self.reject, objectName='closeButton'), 0, 3)
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum,
                                   QSizePolicy.Expanding), 2, 0)
        
        self.dropZone = DropArea(self.loadNewAnimation_signal, self)
        self.layout.addWidget(self.dropZone, 1, 0, 1, 4)

        self.createButton = QPushButton('Create animation', self, clicked=self.accept, cursor=Qt.PointingHandCursor, toolTip='Create animation')
        self.createButton.setMinimumHeight(self.dropZone.height() / 2)
        self.createButton.setObjectName('Custom_Button')
        self.layout.addWidget(self.createButton, 2, 0, 1, 4)
        

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

    

class LoadingDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(LoadingDialog, self).__init__(*args, **kwargs)

        self.fileLocation = ''
        self.createAnimation = True

        self.setObjectName('Custom_Dialog')
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.setStyleSheet(self.Stylesheet)
        self.initUi()


    def initUi(self):
        layout = QVBoxLayout(self)
        # 重点： 这个widget作为背景和圆角
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')
        layout.addWidget(self.widget)

        self.spinner = QtWaitingSpinner(self)

        layout = QGridLayout(self.widget)
        layout.addWidget(self.spinner)
    
    def sizeHint(self):
        return self.screen().size() / 3
    
    def start(self):
        print('Start loading')
        self.spinner.start()
        self.show()
    
    def stop(self):
        self.setVisible(False)
        print('Stop loading')

class QtWaitingSpinner(QWidget):
    mColor = QColor(Qt.blue)
    mRoundness = 100.0
    mMinimumTrailOpacity = 31.4159265358979323846
    mTrailFadePercentage = 50.0
    mRevolutionsPerSecond = 1.57079632679489661923
    mNumberOfLines = 20
    mLineLength = 20
    mLineWidth = 5
    mInnerRadius = 100
    mCurrentCounter = 0
    mIsSpinning = False

    def __init__(self, centerOnParent=True, disableParentWhenSpinning=True, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.mCenterOnParent = centerOnParent
        self.mDisableParentWhenSpinning = disableParentWhenSpinning
        self.initialize()

    def initialize(self):
        #self.timerThread = QThread()
        #self.timerThread.start()
        self.timer = QTimer()
        #self.timer.moveToThread(self.timerThread)
        self.timer.timeout.connect(self.rotate)
        self.timer.stop()
        self.updateSize()
        self.updateTimer()
        self.hide()

    def rotate(self):
        self.mCurrentCounter += 1
        print('rotate')
        if self.mCurrentCounter > self.numberOfLines():
            self.mCurrentCounter = 0
        self.update()

    def updateSize(self):
        size = (self.mInnerRadius + self.mLineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self.timer.setInterval(1000 / (self.mNumberOfLines * self.mRevolutionsPerSecond))

    def updatePosition(self):
        if self.parentWidget() and self.mCenterOnParent:
            self.move(self.parentWidget().width() / 2 - self.width() / 2,
                      self.parentWidget().height() / 2 - self.height() / 2)

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, color):
        if countDistance == 0:
            return color

        minAlphaF = minOpacity / 100.0

        distanceThreshold = ceil((totalNrOfLines - 1) * trailFadePerc / 100.0)
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)

        else:
            alphaDiff = self.mColor.alphaF() - minAlphaF
            gradient = alphaDiff / distanceThreshold + 1.0
            resultAlpha = color.alphaF() - gradient * countDistance
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color

    def paintEvent(self, event):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.mCurrentCounter > self.mNumberOfLines:
            self.mCurrentCounter = 0
        painter.setPen(Qt.NoPen)

        for i in range(self.mNumberOfLines):
            painter.save()
            painter.translate(self.mInnerRadius + self.mLineLength,
                              self.mInnerRadius + self.mLineLength)
            rotateAngle = 360.0 * i / self.mNumberOfLines
            painter.rotate(rotateAngle)
            painter.translate(self.mInnerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(i, self.mCurrentCounter,
                                                         self.mNumberOfLines)
            color = self.currentLineColor(distance, self.mNumberOfLines,
                                          self.mTrailFadePercentage, self.mMinimumTrailOpacity, self.mColor)
            painter.setBrush(color)
            painter.drawRoundedRect(QRect(0, -self.mLineWidth // 2, self.mLineLength, self.mLineLength),
                                    self.mRoundness, Qt.RelativeSize)
            painter.restore()

    def start(self):
        self.updatePosition()
        self.mIsSpinning = True
        self.show()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self.timer.isActive():
            self.timer.start()
            self.mCurrentCounter = 0

    def stop(self):
        self.mIsSpinning = False
        self.hide()

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self.timer.isActive():
            self.timer.stop()
            self.mCurrentCounter = 0

    def setNumberOfLines(self, lines):
        self.mNumberOfLines = lines
        self.updateTimer()

    def setLineLength(self, length):
        self.mLineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self.mLineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self.mInnerRadius = radius
        self.updateSize()

    def color(self):
        return self.mColor

    def roundness(self):
        return self.mRoundness

    def minimumTrailOpacity(self):
        return self.mMinimumTrailOpacity

    def trailFadePercentage(self):
        return self.mTrailFadePercentage

    def revolutionsPersSecond(self):
        return self.mRevolutionsPerSecond

    def numberOfLines(self):
        return self.mNumberOfLines

    def lineLength(self):
        return self.mLineLength

    def lineWidth(self):
        return self.mLineWidth

    def innerRadius(self):
        return self.mInnerRadius

    def isSpinning(self):
        return self.mIsSpinning

    def setRoundness(self, roundness):
        self.mRoundness = min(0.0, max(100, roundness))

    def setColor(self, color):
        self.mColor = color

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self.mRevolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self.mTrailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self.mMinimumTrailOpacity = minimumTrailOpacity

if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = LoadingDialog()
    window.start()
    QTimer.singleShot(5000, window.stop)
    sys.exit(app.exec_())