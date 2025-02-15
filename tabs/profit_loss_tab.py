from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from widgets import BarChartWidget, PieChartWidget, LineChartWidget
import matplotlib.dates as mdates
from datetime import datetime

class ProfitLossTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Load UI
        loader = QUiLoader()
        ui_file = QFile("ui/profit_loss_tab.ui")
        ui_file.open(QFile.ReadOnly)
        self.tab_content = loader.load(ui_file)
        ui_file.close()
        
        # Add the loaded UI to this widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_content)
        
        # Create chart container layouts
        charts_layout = QGridLayout()
        charts_layout.setSpacing(20)  # Increase spacing between charts
        charts_layout.setContentsMargins(0, 10, 0, 10)  # Add vertical margins
        self.tab_content.chart_container.setLayout(charts_layout)
        
        # Setup main chart (combined line and bar)
        self.main_chart = LineChartWidget(width=16, height=4)
        charts_layout.addWidget(self.main_chart.get_canvas(), 0, 0, 1, 3)  # Span all 3 columns
        
        # Setup bottom charts with equal sizes
        bottom_width = 5
        bottom_height = 3
        
        # Setup pie chart
        self.pie_chart = PieChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.pie_chart.get_canvas(), 1, 0)
        
        # Setup weekly bar chart
        self.weekly_chart = BarChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.weekly_chart.get_canvas(), 1, 1)
        
        # Setup source bar chart
        self.source_chart = BarChartWidget(width=bottom_width, height=bottom_height)
        charts_layout.addWidget(self.source_chart.get_canvas(), 1, 2)
        
        # Set column stretches to distribute space evenly
        charts_layout.setColumnStretch(0, 1)
        charts_layout.setColumnStretch(1, 1)
        charts_layout.setColumnStretch(2, 1)
        
        # Configure chart styles
        for chart in [self.main_chart, self.pie_chart, self.weekly_chart, self.source_chart]:
            chart.figure.patch.set_facecolor('#1E1E1E')
            chart.ax.set_facecolor('#1E1E1E')
            chart.ax.tick_params(colors='#FFFFFF', which='both')
            for spine in chart.ax.spines.values():
                spine.set_color('#2D2D2D')
            chart.ax.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
            
            # Use constrained layout for all charts
            chart.figure.set_constrained_layout(True)
        
        # Set initial button states
        self.tab_content.button_money.setProperty("active", True)
        self.tab_content.button_deals.setProperty("active", False)
        
        # Connect button signals
        self.tab_content.button_money.clicked.connect(self.show_money_view)
        self.tab_content.button_deals.clicked.connect(self.show_deals_view)
        
        # Initial data
        self.update_chart_data()
        
    def update_metrics(self, metrics):
        """Update all metrics
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        if 'profit' in metrics:
            self.tab_content.value_profit.setText(f"{metrics['profit']:,.2f}")
        if 'loss' in metrics:
            self.tab_content.value_loss.setText(f"-{metrics['loss']:,.2f}")
        if 'swaps' in metrics:
            self.tab_content.value_swaps.setText(str(metrics['swaps']))
        if 'dividends' in metrics:
            self.tab_content.value_dividends.setText(str(metrics['dividends']))
        if 'commissions' in metrics:
            self.tab_content.value_commissions.setText(str(metrics['commissions']))
        if 'year_total' in metrics:
            self.tab_content.value_year_total.setText(f"{metrics['year_total']}k")
        if 'total' in metrics:
            self.tab_content.value_total.setText(f"{metrics['total']}k")
            
    def update_chart_data(self, view_type='money'):
        """Update all charts with profit/loss data
        
        Args:
            view_type (str): Type of view to show ('money' or 'deals')
        """
        if view_type == 'money':
            # Update main chart (combined line and bar)
            dates = [
                '2025.02.09', '2025.02.10', '2025.02.11', '2025.02.12', 
                '2025.02.13', '2025.02.14'
            ]
            # Daily profit/loss values for bars
            profit_loss = [0, 0, 221.56, -38.75, 182.81, 0]
            # Cumulative total for line
            total = [12000, 12000, 12221.56, 12182.81, 12365.62, 12365.62]
            
            self.main_chart.update_data(
                x_data=dates,
                y_data=[total],  # Line data showing cumulative total
                bar_data=profit_loss,  # Bar data showing daily profit/loss
                colors=['#2196F3'],  # Blue for total line
                bar_colors=['#4CAF50' if v >= 0 else '#F44336' for v in profit_loss]  # Green/red for profit/loss
            )
            
            # Update pie chart
            gross_profit = 22.69
            gross_loss = 10.31
            self.pie_chart.update_data(
                sizes=[gross_profit, gross_loss],
                labels=['Gross Profit\n+22.69k', 'Gross Loss\n-10.31k'],
                colors=['#4CAF50', '#F44336']
            )
            
            # Update weekly bar chart
            days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
            daily_values = [500, 1200, -300, 800, -200, 0, 0]
            colors = ['#4CAF50' if v >= 0 else '#F44336' for v in daily_values]
            
            self.weekly_chart.update_data(
                categories=days,
                values=daily_values,
                colors=colors
            )
            
            # Update source bar chart
            sources = ['Manual', 'Robot', 'Signals']
            source_values = [3500, 15000, 0]
            source_colors = ['#4CAF50'] * len(sources)
            
            self.source_chart.update_data(
                categories=sources,
                values=source_values,
                colors=source_colors
            )
            
        else:  # deals view
            # Update main chart to show deals over time
            dates = ['2025.02.09', '2025.02.10', '2025.02.11', '2025.02.12', '2025.02.13', '2025.02.14']
            deals = [2, 3, 5, 4, 3, 1]
            
            self.main_chart.update_data(
                x_data=dates,
                y_data=[deals],
                colors=['#4CAF50']
            )
            
            # Update pie chart for deal distribution
            manual_deals = 5
            robot_deals = 15
            signals_deals = 0
            
            self.pie_chart.update_data(
                sizes=[manual_deals, robot_deals, signals_deals],
                labels=['Manual', 'Robot', 'Signals'],
                colors=['#4CAF50', '#2196F3', '#9C27B0']
            )
            
            # Update weekly bar chart
            days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
            daily_deals = [2, 3, 5, 4, 3, 0, 0]
            colors = ['#4CAF50'] * len(days)
            
            self.weekly_chart.update_data(
                categories=days,
                values=daily_deals,
                colors=colors
            )
            
            # Update source bar chart
            sources = ['Manual', 'Robot', 'Signals']
            deal_counts = [manual_deals, robot_deals, signals_deals]
            source_colors = ['#4CAF50', '#2196F3', '#9C27B0']
            
            self.source_chart.update_data(
                categories=sources,
                values=deal_counts,
                colors=source_colors
            )
            
        # Update text colors for all charts
        for chart in [self.main_chart, self.pie_chart, self.weekly_chart, self.source_chart]:
            for text in chart.ax.get_xticklabels() + chart.ax.get_yticklabels():
                text.set_color('#FFFFFF')
                text.set_fontsize(9)
            chart.canvas.draw()
        
    def show_money_view(self):
        """Switch to money view"""
        self.tab_content.button_money.setProperty("active", True)
        self.tab_content.button_deals.setProperty("active", False)
        self.tab_content.button_money.style().unpolish(self.tab_content.button_money)
        self.tab_content.button_money.style().polish(self.tab_content.button_money)
        self.tab_content.button_deals.style().unpolish(self.tab_content.button_deals)
        self.tab_content.button_deals.style().polish(self.tab_content.button_deals)
        self.update_chart_data('money')
        
    def show_deals_view(self):
        """Switch to deals view"""
        self.tab_content.button_money.setProperty("active", False)
        self.tab_content.button_deals.setProperty("active", True)
        self.tab_content.button_money.style().unpolish(self.tab_content.button_money)
        self.tab_content.button_money.style().polish(self.tab_content.button_money)
        self.tab_content.button_deals.style().unpolish(self.tab_content.button_deals)
        self.tab_content.button_deals.style().polish(self.tab_content.button_deals)
        self.update_chart_data('deals') 