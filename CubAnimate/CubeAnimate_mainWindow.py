from PyQt5 import QtWidgets as Qtw
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QFont, QVector3D, QPixmap, QIcon, QKeySequence

from .common.CDrawer import CDrawer
from .common.CTypes import Axis, CubeSize, CubeLEDFrame_DATA

from .equation_editor.equation_editor import EIWindow
from .animation_editor.animation_editor import Animator
from .hue_editor.hue_editor import HueEditor


'''
from .common.CubeViewer3D import CubeViewer3DInteract
class StartingMenuBackground(Qtw.QWidget):
    newColorLED_signal = QtCore.pyqtSignal(int,int,int, QColor)
    eraseColorLED_signal = QtCore.pyqtSignal(int,int,int)

    def __init__(self, parent):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.cubeSize = CubeSize(8,8,8)

        self.layout = Qtw.QVBoxLayout(self)
        self.cubeViewer = CubeViewer3DInteract(False, self.cubeSize, self.newColorLED_signal, self.eraseColorLED_signal, self)
        self.layout.addWidget(self.cubeViewer)
    
    def getCurrentColor(self) -> QColor :
        return QColor(255,0,0)
    
    def setBackgroundColor(self, color:QColor):
        self.cubeViewer.setBackgroundColor(color)
'''


class MainMenu(Qtw.QWidget):
    def __init__(self, newWindow_signal:QtCore.pyqtSignal, parent=None):
        super(Qtw.QWidget, self).__init__(parent)
        self.parent = parent
        self.newWindow_signal = newWindow_signal

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('MainMenu{background:white;}')
        layout = Qtw.QVBoxLayout(self)

        #self.startButton = WindowSelectionButton('Start', self.newWindow_signal, Editors_MainWidget.STARTER, self)
        #layout.addWidget(self.startButton)

        self.animatorButton = WindowSelectionButton('Animation', self.newWindow_signal, EditorIndex.ANIMATOR, self)
        layout.addWidget(self.animatorButton)

        self.equationButton = WindowSelectionButton('Equation mode', self.newWindow_signal, EditorIndex.EQUATION_INTERPRETER, self)
        layout.addWidget(self.equationButton)

        self.hueEditorButton = WindowSelectionButton('HUE mode', self.newWindow_signal, EditorIndex.HUE_EDITOR, self)
        layout.addWidget(self.hueEditorButton)



class WindowSelectionButton(Qtw.QPushButton):

    stylesheet = """
    #Custom_Window_Button {
        border: 1px solid #cbcbcb;
        border-radius: 5px;
        font-size: 16px;
        background: white;
    }
    #Custom_Window_Button:hover {
        border-color: rgb(139, 173, 228);
        color: rgb(139, 173, 228);
    }
    #Custom_Window_Button:pressed {
        color: #cbcbcb;
        border-color: #cbcbcb;
    }
    """
    def __init__(self, text : str, newWindow_signal:QtCore.pyqtSignal, menuIndex : int, parent=None):
        super(Qtw.QPushButton, self).__init__(text, parent, cursor=QtCore.Qt.PointingHandCursor, toolTip='Change current editor', clicked=lambda: newWindow_signal.emit(menuIndex))
        self.newWindow_signal = newWindow_signal
        self.menuIndex = menuIndex

        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Preferred)
        self.setObjectName('Custom_Window_Button')
        self.setStyleSheet(self.stylesheet)


class OpenMenuButton(Qtw.QPushButton):
    def __init__(self, width:int, onClick, bgColor: QColor, parent=None):
        super().__init__(parent, clicked=onClick)

        self.setMinimumSize(60, 60)

        self.setSizePolicy(Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Expanding)
        self.setFixedWidth(width)

        self.bgColor = bgColor
        self.menuColor = QColor(255, 255, 255)
        self.shadowColor = QColor(200, 200, 220)
        self.shadowSize = 0.7

        self._animation = QtCore.QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.001,
            endValue=min(0.25, 1.0 - self.shadowSize),
            duration=500
        )
        self._animation.setEasingCurve(QtCore.QEasingCurve.OutElastic)

    def _animate(self, value):
        qss = """
            font: 75 14pt "Microsoft YaHei UI";
            font-weight: bold;
            text-align: left;
            color: rgb(255, 255, 255);
            border: 0px solid rgb(255, 255, 255);
        """
        grad = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {menuColor}, stop:{value1} {menuColor}, stop:{value2} {shadowColor}, stop: {value3} {bgColor}, stop: 1.0 {bgColor});".format(
            bgColor=self.bgColor.name(), menuColor=self.menuColor.name(), shadowColor=self.shadowColor.name(), value1=value-0.0001, value2=value, value3=value+self.shadowSize
        )
        qss += grad
        self.setStyleSheet(qss)

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class EditorIndex():
    ANIMATOR, EQUATION_INTERPRETER, HUE_EDITOR = range(3)

class StatusBar_Widget(Qtw.QWidget):
    stylesheet = """
    QPushButton {
    border: 0px;
    border-radius: 3px;
    max-width: 30px;
    min-width: 30px;
    max-height: 30px;
    min-height: 30px;
    margin-left: 50px;
    margin-bottom: 0px;
    }
    QPushButton:hover {
        border-color: rgb(139, 173, 228);
    }
    QPushButton:pressed {
        color: #cbcbcb;
    }

    #menuButton {
        image : url(:/UI/home.svg);
    }
    #saveButton {
        image : url(:/UI/save.svg);
    }
    #openButton {
        image : url(:/UI/import.svg);
    }
    """

    def __init__(self, openMenu_signal:QtCore.pyqtSignal, saveFile_signal:QtCore.pyqtSignal, openFile_signal:QtCore.pyqtSignal):
        super().__init__()
        self.openMenu_signal = openMenu_signal
        self.saveFile_signal = saveFile_signal
        self.openFile_signal = openFile_signal

        self.layout=Qtw.QHBoxLayout(self)
        self.setLayout(self.layout)
        self.setStyleSheet(self.stylesheet)

        self.layout.addItem(Qtw.QSpacerItem(20, 40, Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Minimum))
        self.layout.addWidget(Qtw.QPushButton('', self, clicked=lambda:self.openMenu_signal.emit(), cursor=QtCore.Qt.PointingHandCursor, toolTip='Go to menu', objectName='menuButton'))
        self.layout.addWidget(Qtw.QPushButton('', self, clicked=lambda:self.saveFile_signal.emit(), cursor=QtCore.Qt.PointingHandCursor, toolTip='Save animation', objectName='saveButton'))
        self.layout.addWidget(Qtw.QPushButton('', self, clicked=lambda:self.openFile_signal.emit(), cursor=QtCore.Qt.PointingHandCursor, toolTip='Open animation', objectName='openButton'))
        self.layout.addItem(Qtw.QSpacerItem(20, 40, Qtw.QSizePolicy.Expanding, Qtw.QSizePolicy.Minimum))
        #self.layout.addWidget(Qtw.QPushButton('Play', self, clicked=lambda:self.openMenu_signal.emit(), objectName='menuButton'))
        #self.layout.addWidget(Qtw.QLabel('ComPort cube'))



class Editors_MainWidget(Qtw.QWidget):
    newWindow_signal = QtCore.pyqtSignal(int)
    waitingCursor_signal = QtCore.pyqtSignal(bool)
    saveFile_signal = QtCore.pyqtSignal()
    openFile_signal = QtCore.pyqtSignal()

    def __init__(self, openMenu_signal:QtCore.pyqtSignal, mainApplication : Qtw.QApplication):
        super().__init__()
        self.cubeSize = CubeSize(8,8,8)
        self.mainApplication = mainApplication
        self.setObjectName('Custom_Main_Widget')
        self.backgroundColor = QColor(250,250,255)
        self.openMenu_signal = openMenu_signal

        ## Windows instantiation
        self.animator = Animator(self, self.waitingCursor_signal, self.cubeSize)
        #self.startBackground = StartingMenuBackground(self)
        self.equationInterpreter = EIWindow(self)
        self.hueEditor = HueEditor(self.cubeSize, self)

        ## Main menu
        #self.drawerMenu = CDrawer(self)
        self.mainMenu = MainMenu(self.newWindow_signal, self)
        #self.drawerMenu.setWidget(self.mainMenu)

        ## Windows manager, add widget according to the order given in EditorIndex
        self.windowStack = Qtw.QStackedWidget(self)
        self.windowStack.addWidget(self.animator)
        self.windowStack.addWidget(self.equationInterpreter)
        self.windowStack.addWidget(self.hueEditor)
        self.currentIndexEditor = self.windowStack.currentIndex()

        self.newWindow_signal.connect(self.changeWindow)
        self.waitingCursor_signal.connect(self.setWaitingCursor)
        self.saveFile_signal.connect(self.saveFile)
        self.openFile_signal.connect(self.openFile)

        self.statusBar = StatusBar_Widget(self.openMenu_signal, self.saveFile_signal, self.openFile_signal)

        ## MainWidget layout
        self.mainLayout=Qtw.QVBoxLayout(self)
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.statusBar)
        self.mainLayout.addWidget(self.windowStack)      
        #self.mainLayout.addWidget(OpenMenuButton(max(30,self.screen().size().width()*0.03), self.openMainMenu, self.backgroundColor), 0, 0)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)

        #self.waitingIcon = LoadingDialog(self)
        #self.waitingIcon.start()
        #self.waitingIcon.stop()

    def setWaitingCursor(self, activate : bool):
        
        if activate:
            self.mainApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            #self.waitingIcon.start()
        else:
            self.mainApplication.restoreOverrideCursor()
            #self.waitingIcon.stop()
    
    #def openMainMenu(self):
    #    self.drawerMenu.show()
    
    def changeWindow(self, newIndexWindow):
        self.waitingCursor_signal.emit(True)
        oldIndexWindow = self.windowStack.currentIndex()

        if oldIndexWindow == EditorIndex.HUE_EDITOR:                      ## HUE WINDOW OUT
            self.hueEditor.activeAnimation(False)

        if newIndexWindow == EditorIndex.ANIMATOR:                        ## ANIMATION WINDOW IN
            ''' With launching pop-up
            if not self.animator.isEmpty():
                self.windowStack.setCurrentIndex(newIndexWindow)
    
            newAnimDialog = NewAnimationDialog(self)
            if newAnimDialog.exec_(): #If pop-up not exited
                self.waitingCursor_signal.emit(True)
                if newAnimDialog.createNewAnimation(): #Create a new animation
                    print('Create new animation')
                    self.animator.createAnimation(self.cubeSize,'New animation')
                elif newAnimDialog.loadAnimation(): #Load an existing animation
                    print('Load animation: ' + newAnimDialog.getFileLocation())
                    self.animator.changeCubeSize(self.cubeSize)
                    self.animator.loadAnimation(newAnimDialog.getFileLocation())
                self.waitingCursor_signal.emit(False)
                self.windowStack.setCurrentIndex(newIndexWindow)
            self.animator.resizeEvent(None) #update positions
            '''
            
            self.animator.createAnimation(self.cubeSize,'New animation')
            self.windowStack.setCurrentIndex(EditorIndex.ANIMATOR)
            self.animator.resizeEvent(None)
            self.currentIndexEditor = EditorIndex.ANIMATOR

        if newIndexWindow == EditorIndex.EQUATION_INTERPRETER:            ## EQUATION WINDOW IN
            self.windowStack.setCurrentIndex(newIndexWindow)
            self.currentIndexEditor = EditorIndex.EQUATION_INTERPRETER
        
        if newIndexWindow == EditorIndex.HUE_EDITOR:                      ## HUE WINDOW IN
            self.hueEditor.activeAnimation(True)
            self.windowStack.setCurrentIndex(newIndexWindow)
            self.currentIndexEditor = EditorIndex.HUE_EDITOR

        #self.drawerMenu.animationOut()
        self.waitingCursor_signal.emit(False)
    
    def changeBackgroundColor(self, color:QColor):
        self.setStyleSheet("#Custom_Main_Widget {background: %s;}"%(color.name()))
        #self.startBackground.setBackgroundColor(color)
        self.animator.setBackgroundColor(color)
        self.hueEditor.setBackgroundColor(color)
        self.backgroundColor = color
    
    def saveFile(self):
        boulOut = True
        if self.windowStack.currentIndex() == EditorIndex.ANIMATOR:
            boulOut = self.animator.saveAnimation()
        return boulOut
        
    def openFile(self):
        if self.windowStack.currentIndex() == EditorIndex.ANIMATOR:
            self.animator.openAnimation()
    
    def getCurrentIndexEditor(self):
        return self.currentIndexEditor
    
    def currentFileSaved(self) -> bool:
        boolOut = True
        if self.windowStack.currentIndex() == EditorIndex.ANIMATOR:
            boolOut = self.animator.isSaved()
            print(boolOut)
        return boolOut

class Menu_MainWidget(Qtw.QWidget):
    def __init__(self, mainApplication : Qtw.QApplication, newWindow_signal:QtCore.pyqtSignal, ):
        super().__init__()
        self.mainApplication = mainApplication
        self.setObjectName('Custom_Menu_Widget')
        self.backgroundColor = QColor(250,250,255)
        self.newWindow_signal = newWindow_signal

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)
        #self.mainLayout.addWidget(Qtw.QPushButton('Animator', self, clicked=lambda:print('Anim'), objectName='AnimationButton'),0,0)
        #self.mainLayout.addWidget(Qtw.QPushButton('HUE', self, clicked=lambda:print('HUE'), objectName='HUEButton'),0,1)
        #self.mainLayout.addWidget(Qtw.QPushButton('Equation', self, clicked=lambda:print('Equation'), objectName='EquationButton'),0,2)

        self.mainLayout.addWidget(WindowSelectionButton('Animator',self.newWindow_signal, EditorIndex.ANIMATOR),0,0)
        self.mainLayout.addWidget(WindowSelectionButton('HUE',self.newWindow_signal, EditorIndex.HUE_EDITOR),0,1)
        self.mainLayout.addWidget(WindowSelectionButton('Equation',self.newWindow_signal, EditorIndex.EQUATION_INTERPRETER),0,2)


class MainWindow(Qtw.QMainWindow):
    openMenu_signal = QtCore.pyqtSignal()
    
    def __init__(self, mainApplication : Qtw.QApplication, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("CubAnimate")
        self.setObjectName('Custom_Main_Window')
        self.mainWidget = Editors_MainWidget(self.openMenu_signal, mainApplication)
        self.mainWidget.newWindow_signal.connect(lambda i: self.closeMenu())
        self.menuWidget = Menu_MainWidget(mainApplication, self.mainWidget.newWindow_signal)
        self.windowStack = Qtw.QStackedWidget(self)
        self.windowStack.addWidget(self.mainWidget)
        self.windowStack.addWidget(self.menuWidget)
        self.setCentralWidget(self.windowStack)
    
        self.editorsIndex = self.windowStack.indexOf(self.mainWidget)
        self.menuIndex = self.windowStack.indexOf(self.menuWidget)
        self.windowStack.setCurrentIndex(self.menuIndex)

        self.backgroundColor = QColor(250,250,255)
        self.changeBackgroundColor(self.backgroundColor)
        self.centralWidget().layout().setContentsMargins(0,0,0,0)
        self.centralWidget().setContentsMargins(0,0,0,0)

        self.openMenu_signal.connect(self.openMenu)
        self.setBaseSize(self.screen().size())

        ## Saving Pop-up
        self.savingPopUp = Qtw.QMessageBox()
        self.savingPopUp.setText("The document has been modified.")
        self.savingPopUp.setInformativeText("Do you want to save your changes?")
        self.savingPopUp.setStandardButtons(Qtw.QMessageBox.Save | Qtw.QMessageBox.Discard | Qtw.QMessageBox.Cancel)
        self.savingPopUp.setDefaultButton(Qtw.QMessageBox.Save)
        self.savingPopUp.setIcon(Qtw.QMessageBox.Warning)
    
    def canLeaveEditor(self):
        boolOut = True
        if self.windowStack.currentIndex() == self.editorsIndex and not self.mainWidget.currentFileSaved(): #Leaving not saved editor
            if self.mainWidget.getCurrentIndexEditor() == EditorIndex.ANIMATOR: #Animator
                out = self.savingPopUp.exec()
                if out == Qtw.QMessageBox.Save:
                    print('Save')
                    boolOut = self.mainWidget.saveFile()
                if out == Qtw.QMessageBox.Discard:
                    print('Discard')
                if out == Qtw.QMessageBox.Cancel:
                    print('Cancel')
                    boolOut = False
        return boolOut

    def openMenu(self):
        if self.canLeaveEditor():
            self.windowStack.setCurrentIndex(self.menuIndex)
    
    def closeMenu(self):
        self.windowStack.setCurrentIndex(self.editorsIndex)

    def changeBackgroundColor(self, color : QColor):
        self.setStyleSheet("#Custom_Main_Window {background:%s;}"%(color.name()))
        self.mainWidget.changeBackgroundColor(color)
    
    def closeEvent(self, event):
        if self.canLeaveEditor():
            event.accept() # let the window close
        else:
            event.ignore()

