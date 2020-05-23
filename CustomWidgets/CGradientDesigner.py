from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from CustomWidgets.CToolBox.CColorPicker import CColorPicker

stylesheet = """
QGroupBox, QLabel, QTabWidget {
    font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif;
}
QtWidgets {
    background: white;
    border-radius: 5px;
}
"""

class GradientDesigner(QtWidgets.QWidget):

    gradientChanged = pyqtSignal()

    def __init__(self, gradient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        if gradient:
            self._gradient = gradient

        else:
            self._gradient = [
                (0.0, QtGui.QColor(255,255,255)),
                (1.0, QtGui.QColor(255,255,255)),
            ]

        # Stop point handle sizes.
        self._handleRadius = 50

        self._drag_position = None

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setObjectName('Custom_GradientViewer')
        self.setStyleSheet(stylesheet)
        effect = QtWidgets.QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(10)
        effect.setOffset(0, 0)
        effect.setColor(QtCore.Qt.gray)
        self.setGraphicsEffect(effect)
    
    
    def getColorAt(self, pos:float) -> QtGui.QColor :
        """ Return color at position pos in the current gradient.

        Parameters:
            pos (float): Position in percent (from 0.0 to 1.0)
        """

        if pos > 0.0 and pos < 1.0:
            indexSup = 0
            while pos > self._gradient[indexSup][0]:
                indexSup += 1
            posSup, colorSup = self._gradient[indexSup]
            posInf, colorInf = self._gradient[indexSup-1]
            ratio = (pos - posInf) / (posSup - posInf)
            r = int(colorInf.red() * (1.0 - ratio) + colorSup.red() * ratio)
            g = int(colorInf.green() * (1.0 - ratio) + colorSup.green() * ratio)
            b = int(colorInf.blue() * (1.0 - ratio) + colorSup.blue() * ratio)
            return QtGui.QColor(r,g,b)
        else:
            return self._gradient[0][1]
    

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = painter.device().width()
        height = painter.device().height()

        # Draw the linear horizontal gradient.
        gradient = QtGui.QLinearGradient(0, 0, width, 0)
        for stop, color in self._gradient:
            gradient.setColorAt(stop, color)

        rect = QtCore.QRect(0, 0, width, height)
        painter.fillRect(rect, gradient)
        painter.setPen(QtGui.QPen(Qt.black,  2, Qt.SolidLine))

        y = painter.device().height() / 2

        # Draw the stop handles.
        for stop, color in self._gradient:
            gradientBrush = QtGui.QRadialGradient(stop * width - self._handleRadius/2, y - self._handleRadius/2, 70)
            gradientBrush.setColorAt(1, color)
            gradientBrush.setColorAt(0, Qt.white)

            painter.setBrush(QtGui.QBrush(gradientBrush))

            painter.drawEllipse(stop * width - self._handleRadius/2,
                y - self._handleRadius/2,
                self._handleRadius,
                self._handleRadius
            )
        painter.end()

    def sizeHint(self):
        return QtCore.QSize(200, 50)

    def _sort_gradient(self):
        self._gradient = sorted(self._gradient, key=lambda g:g[0])

    def _constrain_gradient(self):
        self._gradient = [
            # Ensure values within valid range.
            (max(0.0, min(1.0, stop)), color)
            for stop, color in self._gradient
        ]

    def setGradient(self, gradient):
        assert all([0.0 <= stop <= 1.0 for stop, _ in gradient])
        self._gradient = gradient
        self._constrain_gradient()
        self._sort_gradient()
        self.gradientChanged.emit()

    def gradient(self):
        return self._gradient

    @property
    def _end_stops(self):
        return [0, len(self._gradient)-1]

    def addStop(self, stop, color=None):
        # Stop is a value 0...1, find the point to insert this stop
        # in the list.
        assert 0.0 <= stop <= 1.0

        for n, g in enumerate(self._gradient):
            if g[0] > stop:
                # Insert before this entry, with specified or next color.
                self._gradient.insert(n, (stop, color or g[1]))
                break
        self._constrain_gradient()
        self.gradientChanged.emit()
        self.update()

    def removeStopAtPosition(self, n):
        if n not in self._end_stops:
            del self._gradient[n]
            self.gradientChanged.emit()
            self.update()

    def setColorAtPosition(self, n, color):
        if n < len(self._gradient):
            stop, _ = self._gradient[n]
            self._gradient[n] = stop, color
            self.gradientChanged.emit()
            self.update()

    def chooseColorAtPosition(self, n, current_color=None):
        print('Chance color stop in ' + str(n))
        '''
        dlg = QtWidgets.QColorDialog(self)
        if current_color:
            dlg.setCurrentColor(QtGui.QColor(current_color))
        
        if dlg.exec_():
            lastIndex = len(self._gradient) - 1
            if n in [0,lastIndex]: #if border stop
                self.setColorAtPosition(0, dlg.currentColor().name())
                self.setColorAtPosition(lastIndex, dlg.currentColor().name())
            else:
                self.setColorAtPosition(n, dlg.currentColor().name())
        '''
        colorDialog = CColorPicker(self)
        ret, color = colorDialog.getColor()
        if ret == QtWidgets.QDialog.Accepted:
            lastIndex = len(self._gradient) - 1
            if n in [0,lastIndex]: #if border stop
                self.setColorAtPosition(0, color)
                self.setColorAtPosition(lastIndex, color)
            else:
                self.setColorAtPosition(n, color)
        

    def _find_stop_handle_for_event(self, e, to_exclude=None):
        width = self.width()
        height = self.height()
        midpoint = height / 2

        # Are we inside a stop point? First check y.
        if (
            e.y() >= midpoint - self._handleRadius and
            e.y() <= midpoint + self._handleRadius
        ):

            for n, (stop, _) in enumerate(self._gradient):
                if to_exclude and n in to_exclude:
                    # Allow us to skip the extreme ends of the gradient.
                    continue
                if (
                    e.x() >= stop * width - self._handleRadius and
                    e.x() <= stop * width + self._handleRadius
                ):
                    return n

    def mousePressEvent(self, e):
        # We're in this stop point.
        if e.button() == Qt.RightButton:
            n = self._find_stop_handle_for_event(e)
            if n is not None:
                _, color = self._gradient[n]
                self.chooseColorAtPosition(n, color)

        elif e.button() == Qt.LeftButton:
            n = self._find_stop_handle_for_event(e, to_exclude=self._end_stops)
            if n is not None:
                # Activate drag mode.
                self._drag_position = n


    def mouseReleaseEvent(self, e):
        self._drag_position = None
        self._sort_gradient()

    def mouseMoveEvent(self, e):
        # If drag active, move the stop.
        if self._drag_position:
            stop = e.x() / self.width()
            _, color = self._gradient[self._drag_position]
            self._gradient[self._drag_position] = stop, color
            self._constrain_gradient()
            self.update()

    def mouseDoubleClickEvent(self, e):
        # Calculate the position of the click relative 0..1 to the width.
        n = self._find_stop_handle_for_event(e)
        if n:
            self._sort_gradient() # Ensure ordered.
            # Delete existing, if not at the ends.
            if n > 0 and n < len(self._gradient) - 1:
                self.removeStopAtPosition(n)

        else:
            stop = e.x() / self.width()
            self.addStop(stop)
        

if __name__ == "__main__":
    from PyQt5 import QtCore, QtGui, QtWidgets

    class Window(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            gradient = GradientDesigner()
            gradient.setGradient([(0, 'black'), (1, 'green'), (0.5, 'red')])
            self.setCentralWidget(gradient)

    app = QtWidgets.QApplication([])
    w = Window()
    w.show()
    app.exec_()





