from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from widgets import LineChartWidget, BarChartWidget

class RisksTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        
        # Create top metrics section
        top_layout = QHBoxLayout()
        
        # Balance metrics
        balance_layout = QHBoxLayout()
        self.balance_value = QLabel("112 381.77")
        self.balance_value.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 14px;")
        self.balance_label = QLabel("Balance")
        self.balance_label.setStyleSheet("color: #2196F3;")
        balance_layout.addWidget(self.balance_value)
        balance_layout.addWidget(self.balance_label)
        
        # Add spacing between metrics
        balance_layout.addSpacing(20)
        
        # Drawdown metrics
        drawdown_layout = QHBoxLayout()
        self.drawdown_value = QLabel("0.0633%")
        self.drawdown_value.setStyleSheet("color: #F44336; font-weight: bold; font-size: 14px;")
        self.drawdown_label = QLabel("Drawdown")
        self.drawdown_label.setStyleSheet("color: #F44336;")
        drawdown_layout.addWidget(self.drawdown_value)
        drawdown_layout.addWidget(self.drawdown_label)
        
        # Add metrics to top layout
        top_layout.addLayout(balance_layout)
        top_layout.addLayout(drawdown_layout)
        top_layout.addStretch()
        
        self.main_layout.addLayout(top_layout)
        
        # Create main chart (Balance and Drawdown lines)
        self.main_chart = LineChartWidget(width=16, height=4)
        self.setup_chart(self.main_chart)
        self.main_layout.addWidget(self.main_chart.get_canvas())
        
        # Create bottom chart (MFE metrics)
        self.mfe_chart = BarChartWidget(width=16, height=3)
        self.setup_chart(self.mfe_chart)
        self.main_layout.addWidget(self.mfe_chart.get_canvas())
        
        # Initial data
        self.update_chart_data()
        
    def setup_chart(self, chart):
        """Configure common chart properties
        
        Args:
            chart: The chart widget to configure
        """
        chart.figure.patch.set_facecolor('#1E1E1E')
        chart.ax.set_facecolor('#1E1E1E')
        chart.ax.tick_params(colors='#FFFFFF', which='both')
        for spine in chart.ax.spines.values():
            spine.set_color('#2D2D2D')
        chart.ax.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
        chart.figure.set_constrained_layout(True)
        
    def update_metrics(self, metrics):
        """Update all metrics
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        if 'balance' in metrics:
            self.balance_value.setText(f"{metrics['balance']:,.2f}")
        if 'drawdown' in metrics:
            self.drawdown_value.setText(f"{metrics['drawdown']:.4f}%")
            
    def update_chart_data(self):
        """Update all charts with risk data"""
        # Update main chart (Balance and Drawdown)
        dates = ['2025.02']
        for i in range(1, 15):  # Generate dates for February
            dates.append(f'2025.02')
            
        # Balance line data (blue line)
        balance = [100000, 100200, 100400, 100600, 100800, 101000, 101200, 101400,
                  102000, 102200, 104000, 106000, 108000, 112000, 112381.77]
        
        # Drawdown line data (red line, right y-axis)
        drawdown = [0, 0.1, 0.2, 0.15, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 
                   2.0, 4.0, 6.0, 8.0, 0.0633]
        
        # Configure main chart
        self.main_chart.ax.clear()
        
        # Plot balance line on left y-axis
        ax1 = self.main_chart.ax
        ax1.plot(dates, balance, color='#2196F3', linewidth=2, label='Balance')
        ax1.set_ylabel('Balance', color='#2196F3')
        ax1.tick_params(axis='y', labelcolor='#2196F3')
        
        # Create right y-axis for drawdown
        ax2 = ax1.twinx()
        ax2.plot(dates, drawdown, color='#F44336', linewidth=2, label='Drawdown')
        ax2.set_ylabel('Drawdown %', color='#F44336')
        ax2.tick_params(axis='y', labelcolor='#F44336')
        
        # Set y-axis limits
        ax1.set_ylim(100000, 115000)
        ax2.set_ylim(0, 10)
        
        # Add legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Update MFE chart with metrics from image
        metrics = [
            ('Best trade', 8826.02),
            ('Max. consecutive wins', 31),
            ('Max. consecutive profit', 125.36),
            ('Worst trade', -2690.08),
            ('Max. consecutive losses', 6),
            ('Max. consecutive loss', -47.68)
        ]
        
        # Create positive and negative bars
        categories = []
        values = []
        colors = []
        
        for label, value in metrics:
            categories.append(label)
            values.append(value)
            colors.append('#4CAF50' if value > 0 else '#F44336')
        
        self.mfe_chart.update_data(
            categories=categories,
            values=values,
            colors=colors
        )
        
        # Update text colors and redraw
        for chart in [self.main_chart, self.mfe_chart]:
            for text in chart.ax.get_xticklabels() + chart.ax.get_yticklabels():
                text.set_color('#FFFFFF')
                text.set_fontsize(9)
            chart.canvas.draw() 