from math import ceil
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class QtWaitingSpinner(QWidget):
    mColor = QColor(Qt.red)
    mRoundness = 100.0
    mMinimumTrailOpacity = 31.4159265358979323846
    mTrailFadePercentage = 50.0
    mRevolutionsPerSecond = 1.57079632679489661923
    mNumberOfLines = 20
    mLineLength = 10
    mLineWidth = 2
    mInnerRadius = 20
    mCurrentCounter = 0
    mIsSpinning = False

    def __init__(self, parent, centerOnParent=True, disableParentWhenSpinning=False, *args, **kwargs):
        QWidget.__init__(self, parent)

        
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
        
        self.mCenterOnParent = centerOnParent
        self.mDisableParentWhenSpinning = disableParentWhenSpinning
        self.initialize()

    def initialize(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()

    @pyqtSlot()
    def rotate(self):
        self.mCurrentCounter += 1
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
        self.setVisible(True)

        if self.parentWidget() and self.mDisableParentWhenSpinning:
            self.parentWidget().setEnabled(False)

        if not self.timer.isActive():
            self.timer.start()
            self.mCurrentCounter = 0
        
        #QTimer.singleShot(3000, self.stop)
        print('start')

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

    class MainWindow(QMainWindow):

        def __init__(self, parent = None):
        
            QMainWindow.__init__(self, parent)
            
            widget = QWidget(self)
            self.editor = QTextEdit()
            self.editor.setPlainText("0123456789"*100)
            layout = QGridLayout(widget)
            layout.addWidget(self.editor, 0, 0, 1, 3)
            button = QPushButton("Wait")
            layout.addWidget(button, 1, 1, 1, 1)
            self.setCentralWidget(widget)
            
            self.overlay = QtWaitingSpinner(self.editor)
            self.overlay.hide()
            button.clicked.connect(self.overlay.start)

            
        def resizeEvent(self, event):
        
            self.overlay.resize(event.size())
            event.accept()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
    
'''
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    dial = QDialog()
    w = QtWaitingSpinner(dial)
    dial.show()
    w.start()
    QTimer.singleShot(3000, w.stop)
    sys.exit(app.exec_())


import math, sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPainter, QBrush, QColor, QPen

class Overlay(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
    
    def paintEvent(self, event):
    
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))
        
        for i in range(6):
            if (self.counter / 5) % 6 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,
                20, 20)
        
        painter.end()
    
    def showEvent(self, event):
    
        self.timer = self.startTimer(50)
        self.counter = 0
    
    def timerEvent(self, event):
    
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()


class MainWindow(QMainWindow):

    def __init__(self, parent = None):
    
        QMainWindow.__init__(self, parent)
        
        widget = QWidget(self)
        self.editor = QTextEdit()
        self.editor.setPlainText("0123456789"*100)
        layout = QGridLayout(widget)
        layout.addWidget(self.editor, 0, 0, 1, 3)
        button = QPushButton("Wait")
        layout.addWidget(button, 1, 1, 1, 1)
        
        self.setCentralWidget(widget)
        self.overlay = Overlay(self.centralWidget())
        self.overlay.hide()
        button.clicked.connect(self.overlay.show)
    
    def resizeEvent(self, event):
    
        self.overlay.resize(event.size())
        event.accept()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

'''