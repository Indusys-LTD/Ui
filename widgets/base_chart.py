from PySide6.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BaseChartWidget(QWidget):
    def __init__(self, width=8, height=4, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(width, height), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Set figure size policy to be expanding
        self.canvas.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        
    def clear_plot(self):
        """Clear the current plot"""
        self.ax.clear()
        self.canvas.draw()
        
    def get_canvas(self):
        """Return the canvas widget for adding to layouts"""
        return self.canvas 