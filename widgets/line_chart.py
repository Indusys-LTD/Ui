from .base_chart import BaseChartWidget
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

class LineChartWidget(BaseChartWidget):
    def __init__(self, parent=None, y_axis_position='right', width=12, height=4):
        super().__init__(width=width, height=height, parent=parent)
        self.y_axis_position = y_axis_position
        self.setup_chart()
        self.tooltip_annotation = None
        self.scatter_points = []
        self.line_data = None
        self.bar_data = None
        self.dates = None
        self.highlight_rect = None
        
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
        if event.inaxes != self.ax:
            if self.tooltip_annotation:
                self.tooltip_annotation.remove()
                self.tooltip_annotation = None
            if self.highlight_rect:
                self.highlight_rect.remove()
                self.highlight_rect = None
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
            if self.highlight_rect:
                self.highlight_rect.remove()
                
            # Add highlight rectangle
            date_num = mdates.date2num(self.dates[closest_idx])
            self.highlight_rect = self.ax.axvspan(
                date_num - 0.3, date_num + 0.3,
                color='#FFFFFF', alpha=0.1
            )
                
            # Format the tooltip text
            date_str = self.dates[closest_idx].strftime('%Y.%m.%d %H:%M')
            if self.bar_data is not None:
                profit_loss = self.bar_data[closest_idx]
                total = self.line_data[0][closest_idx] if self.line_data else 0
                
                # Split into profit and loss for display
                if profit_loss > 0:
                    tooltip_text = f'{date_str}\nProfit: +{profit_loss:.2f}\nTotal: {total:.2f}'
                else:
                    tooltip_text = f'{date_str}\nLoss: {profit_loss:.2f}\nTotal: {total:.2f}'
            else:
                total = self.line_data[0][closest_idx]
                tooltip_text = f'{date_str}\nTotal: {total:.2f}'
            
            # Calculate y position for tooltip (use the maximum value point)
            if self.bar_data is not None:
                y_pos = max(abs(self.bar_data[closest_idx]), self.line_data[0][closest_idx])
            else:
                y_pos = self.line_data[0][closest_idx]
            
            # Create and show the tooltip
            self.tooltip_annotation = self.ax.annotate(
                tooltip_text,
                xy=(mdates.date2num(self.dates[closest_idx]), y_pos),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='#2D2D2D', ec='#FFFFFF', alpha=0.8),
                color='#FFFFFF',
                fontsize=9,
                ha='left',
                va='bottom'
            )
            self.canvas.draw_idle()
        elif self.tooltip_annotation:
            self.tooltip_annotation.remove()
            self.tooltip_annotation = None
            if self.highlight_rect:
                self.highlight_rect.remove()
                self.highlight_rect = None
            self.canvas.draw_idle()
        
    def update_data(self, x_data, y_data, colors=None, bar_data=None, bar_colors=None):
        """Update the chart with new data
        
        Args:
            x_data (list): List of x-axis values (dates as strings or datetime objects)
            y_data (list): List of lists containing y values for each line
            colors (list, optional): List of colors for each line
            bar_data (list, optional): List of values for bars
            bar_colors (list, optional): List of colors for bars
        """
        self.clear_plot()
        
        # Store data for tooltip
        self.dates = []
        for d in x_data:
            if isinstance(d, str):
                self.dates.append(datetime.strptime(d, '%Y.%m.%d'))
            else:
                self.dates.append(d)
                
        self.line_data = y_data
        self.bar_data = bar_data
        
        # Convert dates to numbers for plotting
        x_nums = mdates.date2num(self.dates)
        
        # Plot bars if provided
        if bar_data is not None:
            bars = self.ax.bar(x_nums, bar_data, color=bar_colors, alpha=0.7, width=0.5, zorder=3)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                if height != 0:  # Only show label if value is not zero
                    self.ax.text(
                        bar.get_x() + bar.get_width()/2,
                        height,
                        f'{height:+,.2f}',
                        ha='center',
                        va='bottom' if height >= 0 else 'top',
                        color='#FFFFFF',
                        fontsize=9
                    )
        
        # Plot each line
        self.scatter_points = []
        for i, data in enumerate(y_data):
            color = colors[i] if colors and i < len(colors) else None
            
            # Plot line with increased width for visibility
            self.ax.plot(x_nums, data, color=color, linewidth=2, zorder=4)
            
        # Format x-axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y.%m.%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Rotate and align the tick labels so they look better
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        # Update the display
        self.canvas.draw_idle()
        
    def set_title(self, title):
        """Set the chart title"""
        self.ax.set_title(title)
        self.canvas.draw() 