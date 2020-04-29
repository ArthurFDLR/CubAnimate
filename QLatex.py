import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets as Qtw

def mathTex_to_QPixmap(mathTex, fs):

    #---- set up a mpl figure instance ----

    fig = Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvas(fig))
    renderer = fig.canvas.get_renderer()

    #---- plot the mathTex expression ----

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')
    t = ax.text(0, 0, mathTex, ha='left', va='bottom', fontsize=fs)

    #---- fit figure size to text artist ----

    fwidth, fheight = fig.get_size_inches()
    fig_bbox = fig.get_window_extent(renderer)

    text_bbox = t.get_window_extent(renderer)

    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height

    fig.set_size_inches(tight_fwidth, tight_fheight)

    #---- convert mpl figure to QPixmap ----

    buf, size = fig.canvas.print_to_buffer()
    qimage = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, size[0], size[1],
                                                  QtGui.QImage.Format_ARGB32))
    qpixmap = QtGui.QPixmap(qimage)

    return qpixmap

class MainWindow(Qtw.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CubAnimate")

        self.mainLayout=Qtw.QGridLayout(self)
        self.setLayout(self.mainLayout)

        self.viewer = Qtw.QLabel("Hello")
        self.viewer.setPixmap(mathTex_to_QPixmap('$ \\frac{Hello \\ there!}{\\sqrt{2}} $', 250))
        self.mainLayout.addWidget(self.viewer,0,0)

if __name__ == '__main__':    
    app = Qtw.QApplication(sys.argv)
    mainWid = MainWindow()
    mainWid.show()
    sys.exit(app.exec_())
