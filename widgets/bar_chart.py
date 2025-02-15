from .base_chart import BaseChartWidget
import matplotlib.pyplot as plt
import numpy as np

class BarChartWidget(BaseChartWidget):
    def __init__(self, width=8, height=4, parent=None):
        super().__init__(width=width, height=height, parent=parent)
        self.setup_chart()
        
    def setup_chart(self):
        """Setup chart properties"""
        # Remove top spine
        self.ax.spines['top'].set_visible(False)
        
        # Set background color
        self.ax.set_facecolor('#1E1E1E')
        self.figure.patch.set_facecolor('#1E1E1E')
        
        # Format y-axis
        self.ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
        
    def update_data(self, categories, values, colors=None):
        """Update the bar chart with new data
        
        Args:
            categories (list): List of category labels
            values (list): List of values for each category
            colors (list, optional): List of colors for each bar
        """
        self.clear_plot()
        
        # Create bars
        x = np.arange(len(categories))
        bars = self.ax.bar(x, values, color=colors)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            if height != 0:  # Only show label if value is not zero
                self.ax.text(
                    bar.get_x() + bar.get_width()/2,
                    height,
                    f'{height:+,.2f}' if isinstance(height, float) else f'{height:+,d}',
                    ha='center',
                    va='bottom' if height >= 0 else 'top',
                    color='#FFFFFF',
                    fontsize=9
                )
        
        # Set category labels
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(categories, rotation=45, ha='right')
        
        # Use constrained layout
        self.figure.set_constrained_layout(True)
        
        self.canvas.draw()
        
    def set_title(self, title):
        """Set the chart title"""
        self.ax.set_title(title)
        self.canvas.draw() 