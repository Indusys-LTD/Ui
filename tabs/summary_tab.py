from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from widgets import PieChartWidget, LineChartWidget
import os
import sys

class SummaryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Load UI
        loader = QUiLoader()
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle
            application_path = sys._MEIPASS
        else:
            # If the application is run from a Python interpreter
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        ui_file_path = os.path.join(application_path, "ui", "summary_tab.ui")
        ui_file = QFile(ui_file_path)
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
        self.tab_content = loader.load(ui_file)
        ui_file.close()
        
        # Add the loaded UI to this widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_content)
        
        # Setup donut chart
        self.donut_chart = PieChartWidget()
        self.tab_content.chart_container.setLayout(QVBoxLayout())
        self.tab_content.chart_container.layout().addWidget(self.donut_chart.get_canvas())
        
        # Configure donut chart style
        self.donut_chart.figure.patch.set_facecolor('#1E1E1E')
        self.donut_chart.ax.set_facecolor('#1E1E1E')
        
        # Setup line chart
        self.line_chart = LineChartWidget(y_axis_position='right')
        self.tab_content.line_chart_container.setLayout(QVBoxLayout())
        self.tab_content.line_chart_container.layout().addWidget(self.line_chart.get_canvas())
        
        # Configure line chart style
        self.line_chart.figure.patch.set_facecolor('#1E1E1E')
        self.line_chart.ax.set_facecolor('#1E1E1E')
        self.line_chart.ax.tick_params(colors='#FFFFFF', which='both')
        for spine in self.line_chart.ax.spines.values():
            spine.set_color('#2D2D2D')
        self.line_chart.ax.grid(True, linestyle='--', alpha=0.3, color='#2D2D2D')
        
        # Ensure progress bar labels are visible
        for label_name in ['label_sharp_ratio', 'label_profit_factor', 'label_recovery_factor',
                          'label_max_drawdown', 'label_deposit_load', 'label_trades_per_week',
                          'label_avg_hold_time']:
            label = getattr(self.tab_content, label_name, None)
            if label:
                label.setStyleSheet("color: #FFFFFF; font-size: 10pt;")
        
        # Ensure progress bar values are visible
        for progress_name in ['progress_sharp_ratio', 'progress_profit_factor', 'progress_recovery_factor',
                            'progress_max_drawdown', 'progress_deposit_load', 'progress_trades_per_week',
                            'progress_avg_hold_time']:
            progress = getattr(self.tab_content, progress_name, None)
            if progress:
                progress.setStyleSheet("""
                    QProgressBar {
                        background-color: #2D2D2D;
                        border: none;
                        border-radius: 2px;
                        text-align: right;
                        padding-right: 5px;
                        height: 20px;
                        color: #FFFFFF;
                        font-size: 10pt;
                    }
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                        border-radius: 2px;
                    }
                """)
        
        # Set initial button states
        self.tab_content.button_balance.setProperty("active", True)
        self.tab_content.button_growth.setProperty("active", False)
        
        # Connect button signals
        self.tab_content.button_balance.clicked.connect(self.show_balance_view)
        self.tab_content.button_growth.clicked.connect(self.show_growth_view)
        
        # Initial data
        self.update_chart_data()
        self.update_line_chart_data()
        
    def update_chart_data(self):
        """Update the donut chart with profit/loss data"""
        # Get values from labels
        gross_profit = float(self.tab_content.value_gross_profit.text().replace('+', '').replace('k', ''))
        gross_loss = abs(float(self.tab_content.value_gross_loss.text().replace('-', '').replace('k', '')))
        
        # Create chart data
        sizes = [gross_profit, gross_loss]
        labels = ['Profit', 'Loss']  # Removed percentages from labels
        colors = ['#4CAF50', '#F44336']  # Green for profit, Red for loss
        
        # Update chart
        self.donut_chart.update_data(
            sizes=sizes,
            labels=labels,
            colors=colors
        )
        
        # Update ALL text colors after chart update
        for text in self.donut_chart.ax.texts:
            text.set_color('#FFFFFF')
            text.set_fontsize(10)  # Ensure text is readable
        
        # Update center text specifically
        center_text = self.donut_chart.ax.texts[-1] if self.donut_chart.ax.texts else None
        if center_text:
            center_text.set_color('#FFFFFF')
            center_text.set_fontsize(12)
            center_text.set_fontweight('bold')
            
        # Force a redraw
        self.donut_chart.figure.canvas.draw()
        
    def update_line_chart_data(self):
        """Update the line chart with balance/equity data"""
        # Sample data - replace with real data
        dates = ['2025.02.09', '2025.02.10', '2025.02.11', '2025.02.12', '2025.02.13', '2025.02.14']
        balance = [112381.77, 112381.77, 112381.77, 112381.77, 112381.77, 112381.77]
        equity = [112309.94, 112309.94, 112309.94, 112309.94, 112309.94, 112309.94]
        
        self.line_chart.update_data(
            x_data=dates,
            y_data=[balance, equity],
            colors=['#2196F3', '#9C27B0']  # Blue for balance, Purple for equity
        )
        
        # Update text colors and style after chart update
        for text in self.line_chart.ax.get_xticklabels() + self.line_chart.ax.get_yticklabels():
            text.set_color('#FFFFFF')
            text.set_fontsize(9)  # Slightly smaller font for axis labels
                
        self.line_chart.canvas.draw()
        
    def update_metrics(self, metrics):
        """Update all metrics including progress bars
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        # Update text metrics
        if 'gross_profit' in metrics:
            self.tab_content.value_gross_profit.setText(f"+{metrics['gross_profit']}k")
        if 'gross_loss' in metrics:
            self.tab_content.value_gross_loss.setText(f"-{metrics['gross_loss']}k")
        if 'swaps' in metrics:
            self.tab_content.value_swaps.setText(str(metrics['swaps']))
        if 'dividends' in metrics:
            self.tab_content.value_dividends.setText(str(metrics['dividends']))
        if 'commissions' in metrics:
            self.tab_content.value_commissions.setText(str(metrics['commissions']))
        if 'balance' in metrics:
            self.tab_content.value_balance.setText(f"{metrics['balance']:,.2f}")
        if 'equity' in metrics:
            self.tab_content.value_equity.setText(f"{metrics['equity']:,.2f}")
            
        # Update progress bars
        if 'sharp_ratio' in metrics:
            self.tab_content.progress_sharp_ratio.setValue(metrics['sharp_ratio'])
        if 'max_drawdown' in metrics:
            self.tab_content.progress_max_drawdown.setValue(metrics['max_drawdown'])
        if 'profit_factor' in metrics:
            self.tab_content.progress_profit_factor.setValue(metrics['profit_factor'])
        if 'deposit_load' in metrics:
            self.tab_content.progress_deposit_load.setValue(metrics['deposit_load'])
        if 'recovery_factor' in metrics:
            self.tab_content.progress_recovery_factor.setValue(metrics['recovery_factor'])
        if 'trades_per_week' in metrics:
            self.tab_content.progress_trades_per_week.setValue(metrics['trades_per_week'])
        if 'average_hold_time' in metrics:
            self.tab_content.progress_avg_hold_time.setValue(metrics['average_hold_time'])
            
    def show_balance_view(self):
        """Switch to balance view"""
        self.tab_content.button_balance.setProperty("active", True)
        self.tab_content.button_growth.setProperty("active", False)
        self.tab_content.button_balance.style().unpolish(self.tab_content.button_balance)
        self.tab_content.button_balance.style().polish(self.tab_content.button_balance)
        self.tab_content.button_growth.style().unpolish(self.tab_content.button_growth)
        self.tab_content.button_growth.style().polish(self.tab_content.button_growth)
        self.update_line_chart_data()
        
    def show_growth_view(self):
        """Switch to growth view"""
        self.tab_content.button_balance.setProperty("active", False)
        self.tab_content.button_growth.setProperty("active", True)
        self.tab_content.button_balance.style().unpolish(self.tab_content.button_balance)
        self.tab_content.button_balance.style().polish(self.tab_content.button_balance)
        self.tab_content.button_growth.style().unpolish(self.tab_content.button_growth)
        self.tab_content.button_growth.style().polish(self.tab_content.button_growth)
        # Update chart with growth data
        self.update_line_chart_data()  # Modify this to show growth data 