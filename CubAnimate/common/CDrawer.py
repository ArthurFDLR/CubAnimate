#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2019年7月24日
@author: Irony
@site: https://pyqt5.com https://github.com/892768447
@email: 892768447@qq.com
@file: CustomWidgets.CDrawer
@description: 
"""
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QPointF, pyqtProperty
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication

__Author__ = 'Irony'
__Copyright__ = 'Copyright (c) 2019'


class CDrawer(QWidget):

    LEFT, TOP, RIGHT, BOTTOM = range(4)

    def __init__(self, *args, stretch=1 / 4, widget=None, **kwargs):
        super(CDrawer, self).__init__(*args, **kwargs)
        
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Drawer | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStretch(stretch)
        
        ## Animation
        self.animIn = QPropertyAnimation(self, duration=500, easingCurve=QEasingCurve.OutCubic)
        self.animIn.setPropertyName(b'pos')

        self.animOut = QPropertyAnimation(self, duration=500, finished=self.onAnimOutEnd,easingCurve=QEasingCurve.OutCubic)
        self.animOut.setPropertyName(b'pos')

        self.animFadeIn = QPropertyAnimation(self, duration=400, easingCurve=QEasingCurve.Linear)
        self.animFadeIn.setPropertyName(b'opacityBG')

        self.animFadeOut = QPropertyAnimation(self, duration=400, easingCurve=QEasingCurve.Linear)
        self.animFadeOut.setPropertyName(b'opacityBG')

        ## Background opacity
        self.opacityBg = 0
        self.stylesheetOpacity = '#CDrawer_alphaWidget{background:rgba(55,55,55,%i);}'
        self.alphaWidget = QWidget(self, objectName='CDrawer_alphaWidget')
        self.alphaWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWidget(widget)          # 子控件

    def resizeEvent(self, event):
        self.alphaWidget.resize(self.size())
        super(CDrawer, self).resizeEvent(event)

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.x() >= 0 and pos.y() >= 0 and self.childAt(pos) == None and self.widget:
            if not self.widget.geometry().contains(pos):
                self.animationOut()
                return
        super(CDrawer, self).mousePressEvent(event)

    def show(self):
        super(CDrawer, self).show()
        parent = self.parent().window() if self.parent() else self.window()
        if not parent or not self.widget:
            return
        # 设置Drawer大小和主窗口一致
        self.setGeometry(parent.geometry())
        geometry = self.geometry()
        self.animationIn(geometry)

    def animationIn(self, geometry):
        """进入动画
        :param geometry:
        """

        self.widget.setGeometry(
            0, 0, int(geometry.width() * self.stretch), geometry.height())
        self.widget.hide()
        self.animIn.setStartValue(QPoint(-self.widget.width(), 0))
        self.animIn.setEndValue(QPoint(0, 0))

        self.opacityBg = 0
        self.animFadeIn.setStartValue(0)
        self.animFadeIn.setEndValue(100)
        self.animFadeIn.start()
        self.animIn.start()

        self.widget.show()
        
    def animationOut(self):
        """离开动画
        """
        self.animIn.stop()
        self.animFadeIn.stop()
        self.opacityBg = 100
        self.animFadeOut.setStartValue(100)
        self.animFadeOut.setEndValue(0)
        self.animFadeOut.start()

        geometry = self.widget.geometry()

        self.animOut.setStartValue(geometry.topLeft())
        self.animOut.setEndValue(QPoint(-self.widget.width(), 0))
        self.animOut.start()

    def onAnimOutEnd(self):
        """离开动画结束
        """
        # 模拟点击外侧关闭
        QApplication.sendEvent(self, QMouseEvent(
            QMouseEvent.MouseButtonPress, QPointF(-1, -1), Qt.LeftButton, Qt.NoButton, Qt.NoModifier))
        self.close()

    def setWidget(self, widget):
        """设置子控件
        :param widget:
        """
        self.widget = widget
        if widget:
            widget.setParent(self)
            self.animIn.setTargetObject(widget)
            self.animOut.setTargetObject(widget)
            self.animFadeIn.setTargetObject(self)
            self.animFadeOut.setTargetObject(self)

    def setEasingCurve(self, easingCurve):
        """设置动画曲线
        :param easingCurve:
        """
        self.animIn.setEasingCurve(easingCurve)

    def getStretch(self):
        """获取占比
        """
        return self.stretch

    def setStretch(self, stretch):
        """设置占比
        :param stretch:
        """
        self.stretch = max(0.1, min(stretch, 0.9))
    
    def getOpacityBG(self):
        return self.opacityBg

    def setOpacityBG(self, value):
        self.opacityBg = value
        self.alphaWidget.setStyleSheet(self.stylesheetOpacity % (self.opacityBg))

    opacityBG = pyqtProperty(int, getOpacityBG, setOpacityBG)
    