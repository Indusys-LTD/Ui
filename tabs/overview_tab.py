from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QGridLayout
from PySide6.QtCore import Qt
from widgets.bar_chart import BarChartWidget

class OverviewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Account selection
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Account 1 (Main)", "Account 2 (Demo)", "Account 3 (Test)"])
        self.account_combo.currentIndexChanged.connect(self.on_account_changed)
        layout.addWidget(self.account_combo)
        
        # Grid for metrics
        metrics_grid = QGridLayout()
        
        # Create labels for metrics
        self.labels = {
            'total_balance': QLabel("Total Balance:"),
            'open_positions': QLabel("Open Positions:"),
            'daily_profit': QLabel("Daily Profit:"),
            'monthly_profit': QLabel("Monthly Profit:"),
            'win_rate': QLabel("Win Rate:"),
            'risk_ratio': QLabel("Risk Ratio:")
        }
        
        self.values = {
            'total_balance': QLabel(),
            'open_positions': QLabel(),
            'daily_profit': QLabel(),
            'monthly_profit': QLabel(),
            'win_rate': QLabel(),
            'risk_ratio': QLabel()
        }
        
        # Add labels and values to grid
        row = 0
        for key in self.labels.keys():
            metrics_grid.addWidget(self.labels[key], row, 0)
            metrics_grid.addWidget(self.values[key], row, 1)
            row += 1
            
        # Style labels
        for label in self.values.values():
            label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            
        layout.addLayout(metrics_grid)
        
        # Add bar chart for monthly performance
        self.performance_chart = BarChartWidget()
        layout.addWidget(self.performance_chart.get_canvas())
        
    def load_sample_data(self):
        self.sample_data = {
            "Account 1 (Main)": {
                'total_balance': "$125,432.50",
                'open_positions': "12",
                'daily_profit': "+$1,234.56",
                'monthly_profit': "+$15,678.90",
                'win_rate': "78.5%",
                'risk_ratio': "2.3"
            },
            "Account 2 (Demo)": {
                'total_balance': "$10,000.00",
                'open_positions': "5",
                'daily_profit': "+$156.78",
                'monthly_profit': "+$1,234.56",
                'win_rate': "65.2%",
                'risk_ratio': "1.8"
            },
            "Account 3 (Test)": {
                'total_balance': "$50,000.00",
                'open_positions': "8",
                'daily_profit': "+$567.89",
                'monthly_profit': "+$4,567.89",
                'win_rate': "71.3%",
                'risk_ratio': "2.1"
            }
        }
        self.update_display("Account 1 (Main)")
        
    def on_account_changed(self, index):
        account = self.account_combo.currentText()
        self.update_display(account)
        
    def update_display(self, account):
        data = self.sample_data[account]
        for key, value in data.items():
            self.values[key].setText(value)
            
        # Update chart with monthly performance data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        values = [4.5, -2.1, 3.8, 5.2, -1.5, 6.3]
        
        # Set colors based on values
        colors = ['#4CAF50' if val >= 0 else '#F44336' for val in values]
        
        # Update chart
        self.performance_chart.update_data(months, values, colors)
        self.performance_chart.set_title("Monthly Performance (%)") 