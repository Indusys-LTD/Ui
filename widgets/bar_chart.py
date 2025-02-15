from .base_chart import BaseChartWidget

class BarChartWidget(BaseChartWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ax.set_title('Bar Chart')
        
    def update_data(self, categories, values):
        """Update the bar chart with new data
        
        Args:
            categories (list): List of category labels
            values (list): List of corresponding values
        """
        self.clear_plot()
        self.ax.bar(categories, values)
        self.ax.set_title('Bar Chart')
        self.canvas.draw()
        
    def set_title(self, title):
        """Set the chart title"""
        self.ax.set_title(title)
        self.canvas.draw() 