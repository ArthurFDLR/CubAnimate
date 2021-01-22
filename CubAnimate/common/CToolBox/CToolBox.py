#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2019年4月19日
@author: Irony
@site: https://pyqt5.com https://github.com/892768447
@email: 892768447@qq.com
@file: CustomWidgets.CColorPicker.CColorPicker
@description: 
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget,\
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy,\
    QHBoxLayout, QPushButton, QGridLayout, QLabel, QSlider

from .CColorControl import CColorControl
from .CColorInfos import CColorInfos
from .CColorPalettes import CColorPalettes
from .CColorPanel import CColorPanel
from .CColorSlider import CColorSlider
from .CColorStraw import CColorStraw


__Author__ = "Irony"
__Copyright__ = 'Copyright (c) 2019 Irony'
__Version__ = 1.0

Stylesheet = """
QLineEdit, QLabel, QTabWidget {
    font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif;
}
#Custom_Color_View {
    background: white;
    border-radius: 3px;
}
#Custom_ToolBox {
    background: white;
}
CColorPalettes {
    min-width: 322px;
    max-width: 322px;
    max-height: 120px;
}
CColorPanel {
    min-height: 160px;
    max-height: 160px;
}
CColorControl {
    min-width: 50px;
    max-width: 50px;
    min-height: 50px;
    max-height: 50px;
}

#editHex {
    min-width: 75px;
}

#splitLine {
    min-height: 1px;
    max-height: 1px;
    background: #e2e2e2;
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
QLabel {
    color: #a9a9a9;
}
QPushButton {
    border: 1px solid #cbcbcb;
    border-radius: 2px;
    font-size: 16px;
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
QToolButton:hover {
    color: rgb(139, 173, 228);
}
QPushButton:pressed {
    color: #cbcbcb;
}
QToolButton:pressed {
    border-color: #cbcbcb;
}

CColorStraw {
    border: none;
    font-size: 18px;
    border-radius: 0px;
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


class ColorPickerWidget(QWidget):
    selectedColor = QColor(255,0,0)

    def __init__(self, alphaSelection : bool, movableWindow : bool, *args, **kwargs):
        super(ColorPickerWidget, self).__init__(*args, **kwargs)

        self.alphaON = alphaSelection

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        self.colorPanel = CColorPanel(self)
        layout.addWidget(self.colorPanel)

        self.controlWidget = QWidget(self)
        layout.addWidget(self.controlWidget)
        clayout = QHBoxLayout(self.controlWidget)

        self.colorStraw = CColorStraw(self)
        clayout.addWidget(self.colorStraw)

        self.colorControl = CColorControl(self)
        clayout.addWidget(self.colorControl)

        self.sliderWidget = QWidget(self)
        clayout.addWidget(self.sliderWidget)
        slayout = QVBoxLayout(self.sliderWidget)
        slayout.setContentsMargins(0, 0, 0, 0)

        self.rainbowSlider = CColorSlider(
            CColorSlider.TypeRainbow, self)
        slayout.addWidget(self.rainbowSlider)
        if self.alphaON:
            self.alphaSlider = CColorSlider(CColorSlider.TypeAlpha, self)
            slayout.addWidget(self.alphaSlider)

        self.colorInfos = CColorInfos(self.alphaON, ColorPickerWidget.selectedColor,self)
        layout.addWidget(self.colorInfos)

        ## Color palette
        layout.addWidget(QWidget(self, objectName='splitLine'))

        self.colorPalettes = CColorPalettes()
        layout.addWidget(self.colorPalettes)

        self.initSignals()
    
    def initSignals(self):
        # 彩虹slider->面板->rgb文字->小圆
        self.rainbowSlider.colorChanged.connect(self.colorPanel.createImage)
        self.colorPanel.colorChanged.connect(self.colorInfos.updateColor)
        self.colorInfos.colorChanged.connect(self.colorControl.updateColor)

        # 透明slider->alpha文字->小圆
        if self.alphaON:
            self.alphaSlider.colorChanged.connect(self.colorInfos.updateAlpha)

        # alpha文字->透明slider
#         self.colorInfos.colorChanged.connect(self.alphaSlider.updateAlpha)

        # 底部多颜色卡
        self.colorPalettes.colorChanged.connect(self.colorInfos.updateColor)
        #self.colorPalettes.colorChanged.connect(self.colorPanel.createImage)
        self.colorInfos.colorAdded.connect(self.colorPalettes.addColor)

        # 取色器
        self.colorStraw.colorChanged.connect(self.colorInfos.updateColor)

        # 颜色结果
        self.colorInfos.colorChanged.connect(self.setColor)

    def setColor(self, color, alpha):
        color = color
        color.setAlpha(alpha)
        ColorPickerWidget.selectedColor = color



class CToolBox_Animator(QWidget):

    def __init__(self, alphaSelection : bool, movableWindow : bool, saveAnimation_signal:pyqtSignal, playAnimation_signal:pyqtSignal, *args, **kwargs):
        super(CToolBox_Animator, self).__init__(*args, **kwargs)

        self.alphaON = alphaSelection
        self.movableON = movableWindow

        self.saveAnimation_signal = saveAnimation_signal
        self.playAnimation_signal = playAnimation_signal

        self.animationFPS = 24

        self.setObjectName('Custom_Color_Dialog')
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(Stylesheet)
        self.mPos = None
        self.initUi()
        # 添加阴影
        
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setOffset(0, 0)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)
        
    def initUi(self):
        layout = QVBoxLayout(self)
        self.colorView = QWidget(self)
        self.colorView.setObjectName('Custom_Color_View')
        layout.addWidget(self.colorView)

        layout = QVBoxLayout(self.colorView)
        layout.setContentsMargins(1, 1, 1, 1)

        ## Upper part
        self.upperWidget = QWidget(self.colorView)
        layout.addWidget(self.upperWidget)
        self.upperLayout = QGridLayout(self.upperWidget)

        self.labelName = QLabel('FPS', self)
        self.labelValue = QLabel('{}'.format(self.animationFPS), self)
        self.sliderFPS = QSlider(Qt.Horizontal, valueChanged=lambda v: self.labelValue.setText(str(v)))
        self.sliderFPS.setValue(self.animationFPS)

        self.upperLayout.addWidget(self.sliderFPS,0,1)
        self.upperLayout.addWidget(self.labelValue,0,2)
        self.upperLayout.addWidget(self.labelName,0,0)

        #self.playButton = QPushButton('', self, objectName='playButton', cursor=Qt.PointingHandCursor, toolTip='Play animation on screen',clicked= lambda :self.playAnimation_signal.emit())
        #self.upperLayout.addWidget(self.playButton,2,1)
        layout.addWidget(QWidget(self.colorView, objectName='splitLine'))

        self.colorPicker = ColorPickerWidget(self.alphaON, self.movableON)
        layout.addWidget(self.colorPicker)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.movableON:
            if event.button() == Qt.LeftButton:
                self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        if self.movableON:
            self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if self.movableON:
            if event.buttons() == Qt.LeftButton and self.mPos:
                if not self.colorPanel.geometry().contains(self.mPos):
                    self.move(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def getColor(self) -> QColor:
        return ColorPickerWidget.selectedColor
    
    def getFPS(self) -> int:
        return self.animationFPS
    
    def changeFPS(self, value):
        self.animationFPS = value
        self.labelValue.setText(str(self.animationFPS))
        self.sliderFPS.setValue(self.animationFPS)


class CToolBox_HUE(QWidget):

    def __init__(self, alphaSelection : bool, movableWindow : bool, saveAnimation_signal:pyqtSignal, *args, **kwargs):
        super(CToolBox_HUE, self).__init__(*args, **kwargs)

        self.alphaON = alphaSelection
        self.movableON = movableWindow

        self.saveAnimation_signal = saveAnimation_signal

        self.loopDuration = 1000 #ms

        self.setObjectName('Custom_Color_Dialog')
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(Stylesheet)
        self.mPos = None
        self.initUi()
        # 添加阴影
        
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setOffset(0, 0)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)
        
    def initUi(self):
        layout = QVBoxLayout(self)
        self.colorView = QWidget(self)
        self.colorView.setObjectName('Custom_Color_View')
        layout.addWidget(self.colorView)

        layout = QVBoxLayout(self.colorView)
        layout.setContentsMargins(1, 1, 1, 1)

        ## Upper part
        self.upperWidget = QWidget(self.colorView)
        layout.addWidget(self.upperWidget)
        self.upperLayout = QGridLayout(self.upperWidget)

        self.labelName = QLabel('Loop duration', self)
        self.labelValue = QLabel('{}'.format(int(self.loopDuration/1000)), self)
        self.sliderFPS = QSlider(Qt.Horizontal, valueChanged=lambda v: self.labelValue.setText(str(v)))
        self.sliderFPS.setValue(int(self.loopDuration/1000))

        self.upperLayout.addWidget(self.sliderFPS,0,1)
        self.upperLayout.addWidget(self.labelValue,0,2)
        self.upperLayout.addWidget(self.labelName,0,0)

        self.saveButton = QPushButton("Save", self, cursor=Qt.PointingHandCursor, toolTip='Export animation',clicked= lambda :self.saveAnimation_signal.emit())
        self.upperLayout.addWidget(self.saveButton,2,0)
        layout.addWidget(QWidget(self.colorView, objectName='splitLine'))

        self.colorPicker = ColorPickerWidget(self.alphaON, self.movableON)
        layout.addWidget(self.colorPicker)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.movableON:
            if event.button() == Qt.LeftButton:
                self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        if self.movableON:
            self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if self.movableON:
            if event.buttons() == Qt.LeftButton and self.mPos:
                if not self.colorPanel.geometry().contains(self.mPos):
                    self.move(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()

    def getColor(self) -> QColor:
        return ColorPickerWidget.selectedColor
    
    def getLoopDuration(self) -> int:
        return self.loopDuration
    
    def changeLoopDuration(self, value):
        self.loopDuration = value
        self.labelValue.setText(str(int(self.loopDuration/1000)))
        self.sliderFPS.setValue(int(self.loopDuration/1000))
