from .base_chart import BaseChartWidget
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class LineChartWidget(BaseChartWidget):
    def __init__(self, parent=None, y_axis_position='right'):
        super().__init__(width=12, height=4, parent=parent)
        self.y_axis_position = y_axis_position
        self.setup_chart()
        self.tooltip_annotation = None
        self.scatter_points = []
        self.balance_data = None
        self.equity_data = None
        self.dates = None
        
        # Connect event handlers
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
    def setup_chart(self):
        """Setup chart properties"""
        # Remove top spine
        self.ax.spines['top'].set_visible(False)
        
        # Configure y-axis position
        if self.y_axis_position == 'right':
            # Move y-axis to the right
            self.ax.yaxis.set_label_position('right')
            self.ax.yaxis.tick_right()
            # Hide left spine and show right spine
            self.ax.spines['left'].set_visible(False)
            self.ax.spines['right'].set_visible(True)
        else:
            # Default left position
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['left'].set_visible(True)
        
        # Set background color
        self.ax.set_facecolor('#1E1E1E')
        self.figure.patch.set_facecolor('#1E1E1E')
        
        # Format y-axis
        self.ax.yaxis.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
        
    def on_mouse_move(self, event):
        """Handle mouse movement over the chart"""
        if event.inaxes != self.ax or not self.scatter_points:
            if self.tooltip_annotation:
                self.tooltip_annotation.remove()
                self.tooltip_annotation = None
                self.canvas.draw_idle()
            return

        # Find the closest point based only on x-axis distance
        closest_idx = -1
        min_distance = float('inf')
        mouse_x = event.xdata
        
        for idx, date in enumerate(self.dates):
            x_data = mdates.date2num(date)
            distance = abs(x_data - mouse_x)
            if distance < min_distance:
                min_distance = distance
                closest_idx = idx
                
        # Show tooltip if close enough to a point (adjust threshold as needed)
        if min_distance < 2:  # Increased threshold and using only x-distance
            if self.tooltip_annotation:
                self.tooltip_annotation.remove()
                
            # Format the tooltip text
            tooltip_text = f'Balance: {self.balance_data[closest_idx]:,.2f}\nEquity: {self.equity_data[closest_idx]:,.2f}'
            
            # Calculate y position for tooltip (midway between balance and equity)
            y_pos = (self.balance_data[closest_idx] + self.equity_data[closest_idx]) / 2
            
            # Create and show the tooltip
            self.tooltip_annotation = self.ax.annotate(
                tooltip_text,
                xy=(mdates.date2num(self.dates[closest_idx]), y_pos),
                xytext=(0, 0), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='#2D2D2D', ec='#FFFFFF', alpha=0.8),
                color='#FFFFFF',
                fontsize=9,
                ha='center',  # Center horizontally
                va='center'   # Center vertically
            )
            self.canvas.draw_idle()
        elif self.tooltip_annotation:
            self.tooltip_annotation.remove()
            self.tooltip_annotation = None
            self.canvas.draw_idle()
        
    def update_data(self, x_data, y_data, colors=None):
        """Update the line chart with new data
        
        Args:
            x_data (list): List of x-axis values (dates)
            y_data (list): List of lists containing y values for each line
            colors (list, optional): List of colors for each line
        """
        self.clear_plot()
        
        # Store data for tooltip
        self.dates = [datetime.strptime(d, '%Y.%m.%d') for d in x_data]
        self.balance_data = y_data[0]
        self.equity_data = y_data[1]
        
        # Plot each line
        self.scatter_points = []
        for i, data in enumerate(y_data):
            color = colors[i] if colors and i < len(colors) else None
            
            self.ax.plot(self.dates, data, color=color, linewidth=2)
            
            # Add dots at each point and store references
            scatter = self.ax.scatter(self.dates, data, color=color, s=30, zorder=5)
            self.scatter_points.append(scatter)
        
        # Format x-axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y.%m.%d'))
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        self.canvas.draw()
        
    def set_title(self, title):
        """Set the chart title"""
        self.ax.set_title(title)
        self.canvas.draw() 