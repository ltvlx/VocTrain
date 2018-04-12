from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator


class PlotWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 500)
        self.setWindowTitle("Session statistics")
        # self.setStyleSheet("""background-color: rgb(255, 255, 255)""")

        # a figure instance to plot on
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)

        # Just some button connected to `plot` method
        # self.button = QtWidgets.QPushButton('Plot')
        # self.button.clicked.connect(self.plot)
        # layout.addWidget(self.button)

        self.setLayout(layout)


    def plot(self, f1, f2):

        # ax = self.figure.add_subplot(111)
        ax = self.figure.subplots(nrows=1, ncols=1)
        ax.set_xlabel("Answers")
        ax.set_ylabel("Cumulative results")

        ax.plot(f1, color='C0', marker='o', linestyle='solid', linewidth=3, markersize=4, label='Correct')
        ax.plot(f2, color='C3', marker='o', linestyle='solid', linewidth=3, markersize=4, label='Incorrect')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()
        self.figure.tight_layout()

        self.show()