from .base_chart import BaseChartWidget
import matplotlib.pyplot as plt

class PieChartWidget(BaseChartWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ax.set_title('Pie Chart')
        
    def update_data(self, sizes, labels=None, autopct='%1.1f%%', colors=None):
        """Update the pie chart with new data
        
        Args:
            sizes (list): List of values for each slice
            labels (list, optional): List of labels for each slice
            autopct (str, optional): Format string for percentage labels
            colors (list, optional): List of colors for each slice
        """
        self.clear_plot()
        
        # Create donut chart
        total = sum(sizes)
        wedges, texts, autotexts = self.ax.pie(sizes, 
                                              labels=labels, 
                                              autopct=autopct,
                                              colors=colors,
                                              pctdistance=0.85,  # Move percentage labels outside
                                              wedgeprops=dict(width=0.17))  # Create thinner donut effect
        
        # Add center text with total
        self.ax.text(0, 0, f'+{total:.2f}k\nTotal', 
                    ha='center', 
                    va='center',
                    fontsize=12,
                    fontweight='bold')
        
        # Style the percentage labels
        plt.setp(autotexts, size=8, weight="bold")
        
        # Equal aspect ratio ensures circular plot
        self.ax.set_aspect('equal')
        
        self.canvas.draw()
        
    def set_title(self, title):
        """Set the chart title"""
        self.ax.set_title(title)
        self.canvas.draw() 