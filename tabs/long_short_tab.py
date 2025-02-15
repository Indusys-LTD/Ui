from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                              QProgressBar)
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from widgets import BarChartWidget, PieChartWidget, LineChartWidget
import matplotlib.dates as mdates
from datetime import datetime

class LongShortTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create metrics section at top
        metrics_layout = QHBoxLayout()
        
        # Long trades count
        self.long_count = QLabel("325 (58.77%)")
        self.long_count.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.long_label = QLabel("Long")
        self.long_label.setStyleSheet("color: #4CAF50;")
        metrics_layout.addWidget(self.long_label)
        metrics_layout.addWidget(self.long_count)
        
        # Short trades count
        self.short_count = QLabel("228 (41.23%)")
        self.short_count.setStyleSheet("color: #F44336; font-weight: bold;")
        self.short_label = QLabel("Short")
        self.short_label.setStyleSheet("color: #F44336;")
        metrics_layout.addWidget(self.short_label)
        metrics_layout.addWidget(self.short_count)
        
        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)
        
        # Create charts container
        charts_layout = QGridLayout()
        charts_layout.setSpacing(20)
        charts_layout.setContentsMargins(0, 10, 0, 10)
        
        # Setup main chart (combined line and bar)
        self.main_chart = LineChartWidget(width=16, height=4)
        charts_layout.addWidget(self.main_chart.get_canvas(), 0, 0, 1, 3)
        
        # Setup bottom charts with equal sizes
        bottom_width = 5
        bottom_height = 3
        
        # Setup distribution pie chart
        self.pie_chart = PieChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.pie_chart.get_canvas(), 1, 0)
        
        # Setup daily distribution bar chart
        self.daily_chart = BarChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.daily_chart.get_canvas(), 1, 1)
        
        # Setup source distribution bar chart
        self.source_chart = BarChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.source_chart.get_canvas(), 1, 2)
        
        # Add metrics grid at the bottom
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(10)
        
        # Create progress bars
        self.progress_bars = {}
        metrics_data = [
            # Left column
            ('netto_pl', 'Netto P/L', '12 381.77', 0, 20000),
            ('commissions', 'Commissions', '0.00', 0, 100),
            ('avg_pl', 'Average P/L', '25.83', 0, 100),
            
            # Middle column
            ('avg_profit', 'Average Profit', '47.08', 0, 100),
            ('avg_pl_percent', 'Average P/L %', '0.0254%', 0, 1),
            ('avg_profit_percent', 'Average Profit %', '0.0459%', 0, 1),
            
            # Right column
            ('trades', 'Trades', '553', 0, 1000),
            ('win_trades', 'Win Trades', '460', 0, 553),
            ('win_trades_percent', 'Win Trades %', '83.18%', 0, 100)
        ]
        
        # Create and add progress bars to grid
        for idx, (key, label, value, min_val, max_val) in enumerate(metrics_data):
            row = idx % 3
            col = idx // 3 * 2  # Multiply by 2 to leave space for values
            
            # Create label
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #AAAAAA;")
            metrics_grid.addWidget(label_widget, row, col)
            
            # Create progress bar
            progress = QProgressBar()
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: #2D2D2D;
                    border: none;
                    border-radius: 2px;
                    text-align: right;
                    padding-right: 5px;
                    height: 20px;
                    color: #FFFFFF;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 2px;
                }
            """)
            progress.setMinimum(min_val)
            progress.setMaximum(max_val)
            progress.setTextVisible(False)
            metrics_grid.addWidget(progress, row, col + 1)
            
            # Create value label
            value_label = QLabel(value)
            value_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            metrics_grid.addWidget(value_label, row, col + 1)
            
            # Store references
            self.progress_bars[key] = (progress, value_label)
        
        # Add metrics grid to main layout
        layout.addLayout(charts_layout)
        layout.addLayout(metrics_grid)
        
        # Set column stretches
        charts_layout.setColumnStretch(0, 1)
        charts_layout.setColumnStretch(1, 1)
        charts_layout.setColumnStretch(2, 1)
        
        # Configure chart styles
        for chart in [self.main_chart, self.pie_chart, self.daily_chart, self.source_chart]:
            chart.figure.patch.set_facecolor('#1E1E1E')
            chart.ax.set_facecolor('#1E1E1E')
            chart.ax.tick_params(colors='#FFFFFF', which='both')
            for spine in chart.ax.spines.values():
                spine.set_color('#2D2D2D')
            chart.ax.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
            chart.figure.set_constrained_layout(True)
        
        # Initial data
        self.update_chart_data()
        
    def update_metrics(self, metrics):
        """Update all metrics including progress bars
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        # Update Long/Short counts
        if 'long_count' in metrics and 'long_percent' in metrics:
            self.long_count.setText(f"{metrics['long_count']} ({metrics['long_percent']:.2f}%)")
            
        if 'short_count' in metrics and 'short_percent' in metrics:
            self.short_count.setText(f"{metrics['short_count']} ({metrics['short_percent']:.2f}%)")
            
        # Update progress bars
        progress_mappings = {
            'netto_pl': ('netto_pl', '{:,.2f}'),
            'commissions': ('commissions', '{:.2f}'),
            'avg_pl': ('avg_pl', '{:.2f}'),
            'avg_profit': ('avg_profit', '{:.2f}'),
            'avg_pl_percent': ('avg_pl_percent', '{:.4f}%'),
            'avg_profit_percent': ('avg_profit_percent', '{:.4f}%'),
            'trades': ('trades', '{:d}'),
            'win_trades': ('win_trades', '{:d}'),
            'win_trades_percent': ('win_trades_percent', '{:.2f}%')
        }
        
        for metric_key, (progress_key, format_str) in progress_mappings.items():
            if metric_key in metrics and progress_key in self.progress_bars:
                progress_bar, value_label = self.progress_bars[progress_key]
                value = metrics[metric_key]
                
                # Update progress bar
                if isinstance(value, (int, float)):
                    progress_bar.setValue(int(value))
                
                # Update value label with formatted text
                try:
                    formatted_value = format_str.format(value)
                    value_label.setText(formatted_value)
                except (ValueError, TypeError):
                    value_label.setText(str(value))
        
    def update_chart_data(self):
        """Update all charts with long/short data"""
        # Update main chart
        dates = ['2025.02.09', '2025.02.10', '2025.02.11', '2025.02.12', '2025.02.13', '2025.02.14']
        
        # Long/Short positions for bars (positive for long, negative for short)
        positions = [10, -5, 15, -8, 12, -6]
        cumulative = [100, 95, 110, 102, 114, 108]  # Cumulative line
        
        self.main_chart.update_data(
            x_data=dates,
            y_data=[cumulative],
            bar_data=positions,
            colors=['#2196F3'],  # Blue for cumulative line
            bar_colors=['#4CAF50' if v >= 0 else '#F44336' for v in positions]  # Green for long, Red for short
        )
        
        # Update pie chart
        self.pie_chart.update_data(
            sizes=[58.77, 41.23],
            labels=['Long\n58.77%', 'Short\n41.23%'],
            colors=['#4CAF50', '#F44336']
        )
        
        # Update daily distribution
        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        long_values = [20, 35, 45, 30, 25, 0, 0]
        short_values = [-15, -25, -30, -20, -18, 0, 0]
        
        self.daily_chart.update_data(
            categories=days,
            values=long_values,
            colors=['#4CAF50'] * len(days)  # All green for long positions
        )
        
        # Update source distribution
        sources = ['Trading Robots', 'Manual Trading', 'Trading Signals']
        values = [532, 21, 0]
        colors = ['#9C27B0', '#2196F3', '#FF9800']  # Purple, Blue, Orange
        
        self.source_chart.update_data(
            categories=sources,
            values=values,
            colors=colors
        )
        
        # Update text colors for all charts
        for chart in [self.main_chart, self.pie_chart, self.daily_chart, self.source_chart]:
            for text in chart.ax.get_xticklabels() + chart.ax.get_yticklabels():
                text.set_color('#FFFFFF')
                text.set_fontsize(9)
            chart.canvas.draw() 