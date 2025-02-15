from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                               QLabel, QGridLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QFrame, QSplitter, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from widgets.bar_chart import BarChartWidget
from widgets.line_chart import LineChartWidget
from dialogs.account_setup_dialog import AccountSetupDialog
import random
from datetime import datetime, timedelta

class OverviewTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Top Controls Section
        top_layout = QHBoxLayout()
        
        # Account Selection
        account_label = QLabel("Account:")
        account_label.setStyleSheet("color: #FFFFFF;")
        
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Account 1 (Main)", "Account 2 (Demo)", "Account 3 (Test)"])
        self.account_combo.currentIndexChanged.connect(self.on_account_changed)
        self.account_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        
        # Setup account button
        self.setup_account_btn = QPushButton("Setup Account")
        self.setup_account_btn.clicked.connect(self.show_account_setup)
        self.setup_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # Trading Control Buttons
        self.trading_btn = QPushButton("Activate Trading")
        self.buy_btn = QPushButton("Activate Buy")
        self.sell_btn = QPushButton("Activate Sell")
        
        # Set initial states
        self.trading_active = False
        self.buy_active = False
        self.sell_active = False
        
        # Connect button signals
        self.trading_btn.clicked.connect(self.toggle_trading)
        self.buy_btn.clicked.connect(self.toggle_buy)
        self.sell_btn.clicked.connect(self.toggle_sell)
        
        # Set button styles
        self.update_button_styles()
        
        top_layout.addWidget(account_label)
        top_layout.addWidget(self.account_combo)
        top_layout.addWidget(self.setup_account_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.trading_btn)
        top_layout.addWidget(self.buy_btn)
        top_layout.addWidget(self.sell_btn)
        
        main_layout.addLayout(top_layout)
        
        # Create splitter for flexible layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Account metrics and ratios
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Account Metrics Section
        metrics_header = QLabel("Account Metrics")
        metrics_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(metrics_header)
        
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        
        self.metrics = {
            'balance': self.create_metric_widget("Balance:", "$125,432.50"),
            'equity': self.create_metric_widget("Equity:", "$124,876.30"),
            'margin': self.create_metric_widget("Margin:", "$12,543.25"),
            'margin_level': self.create_metric_widget("Margin Level:", "89.5%"),
            'floating_pl': self.create_metric_widget("Floating P/L:", "+$1,234.56"),
            'daily_pl': self.create_metric_widget("Daily P/L:", "+$876.54")
        }
        
        row = 0
        col = 0
        for key, widget in self.metrics.items():
            metrics_grid.addLayout(widget, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1
                
        left_layout.addLayout(metrics_grid)
        left_layout.addSpacing(20)
        
        # Trading Ratios Section
        ratios_header = QLabel("Trading Ratios")
        ratios_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(ratios_header)
        
        ratios_grid = QGridLayout()
        ratios_grid.setSpacing(20)
        
        self.ratios = {
            'sharp_ratio': self.create_metric_widget("Sharp Ratio:", "1.87"),
            'sortino_ratio': self.create_metric_widget("Sortino Ratio:", "2.34"),
            'profit_factor': self.create_metric_widget("Profit Factor:", "2.5"),
            'recovery_factor': self.create_metric_widget("Recovery Factor:", "3.2"),
            'win_rate': self.create_metric_widget("Win Rate:", "78.5%"),
            'risk_reward': self.create_metric_widget("Risk/Reward:", "1:2.5")
        }
        
        row = 0
        col = 0
        for key, widget in self.ratios.items():
            ratios_grid.addLayout(widget, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1
                
        left_layout.addLayout(ratios_grid)
        left_layout.addSpacing(20)
        
        # Account Growth Chart
        growth_header = QLabel("Account Growth")
        growth_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(growth_header)
        
        self.growth_chart = LineChartWidget()
        left_layout.addWidget(self.growth_chart.get_canvas())
        
        # Right side - Open positions and equity chart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Open Positions Section
        positions_header = QLabel("Open Positions")
        positions_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(positions_header)
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels([
            "Symbol", "Type", "Volume", "Open Price", "Current Price", "Swap", "Profit/Loss"
        ])
        
        # Set table properties
        self.positions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.positions_table.setAlternatingRowColors(True)
        self.positions_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #FFFFFF;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #3D3D3D;
            }
        """)
        
        right_layout.addWidget(self.positions_table)
        right_layout.addSpacing(20)
        
        # Equity/Balance Chart
        equity_header = QLabel("Equity/Balance")
        equity_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(equity_header)
        
        self.equity_chart = LineChartWidget()
        right_layout.addWidget(self.equity_chart.get_canvas())
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        
        main_layout.addWidget(splitter)
        
    def create_metric_widget(self, label_text, initial_value=""):
        """Create a metric widget with label and value"""
        layout = QHBoxLayout()
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #AAAAAA;")
        value = QLabel(initial_value)
        value.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch()
        
        return layout
        
    def toggle_trading(self):
        """Toggle trading state"""
        self.trading_active = not self.trading_active
        self.update_button_styles()
        
    def toggle_buy(self):
        """Toggle buy state"""
        self.buy_active = not self.buy_active
        self.update_button_styles()
        
    def toggle_sell(self):
        """Toggle sell state"""
        self.sell_active = not self.sell_active
        self.update_button_styles()
        
    def update_button_styles(self):
        """Update button styles based on their states"""
        active_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        inactive_style = """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """
        
        self.trading_btn.setStyleSheet(active_style if self.trading_active else inactive_style)
        self.buy_btn.setStyleSheet(active_style if self.buy_active else inactive_style)
        self.sell_btn.setStyleSheet(active_style if self.sell_active else inactive_style)
        
        # Update button text
        self.trading_btn.setText("Trading Active" if self.trading_active else "Trading Inactive")
        self.buy_btn.setText("Buy Active" if self.buy_active else "Buy Inactive")
        self.sell_btn.setText("Sell Active" if self.sell_active else "Sell Inactive")
        
    def load_sample_data(self):
        self.update_positions()
        self.update_data()
        
    def on_account_changed(self, index):
        self.load_sample_data()
        
    def update_positions(self):
        """Update open positions table with sample data"""
        positions = [
            ("EURUSD", "Buy", 1.0, 1.0876, 1.0892, -0.23, 160.0),
            ("GBPUSD", "Sell", 0.5, 1.2654, 1.2632, -0.12, 110.0),
            ("BTCUSD", "Buy", 0.1, 43250.0, 43450.0, 0.0, 200.0),
            ("USDJPY", "Sell", 1.0, 147.85, 147.65, -0.34, 185.5),
            ("XAUUSD", "Buy", 0.2, 2023.45, 2025.67, -0.15, 44.4)
        ]
        
        self.positions_table.setRowCount(len(positions))
        for row, position in enumerate(positions):
            # Symbol
            self.positions_table.setItem(row, 0, QTableWidgetItem(position[0]))
            
            # Type with color
            type_item = QTableWidgetItem(position[1])
            type_item.setForeground(
                QColor("#4CAF50") if position[1] == "Buy" else QColor("#F44336")
            )
            self.positions_table.setItem(row, 1, type_item)
            
            # Volume
            self.positions_table.setItem(row, 2, QTableWidgetItem(str(position[2])))
            
            # Prices
            self.positions_table.setItem(row, 3, QTableWidgetItem(f"{position[3]:.4f}"))
            self.positions_table.setItem(row, 4, QTableWidgetItem(f"{position[4]:.4f}"))
            
            # Swap
            swap_item = QTableWidgetItem(f"{position[5]:.2f}")
            swap_item.setForeground(
                QColor("#4CAF50") if position[5] >= 0 else QColor("#F44336")
            )
            self.positions_table.setItem(row, 5, swap_item)
            
            # Profit/Loss
            pl_item = QTableWidgetItem(f"${position[6]:.2f}")
            pl_item.setForeground(
                QColor("#4CAF50") if position[6] >= 0 else QColor("#F44336")
            )
            self.positions_table.setItem(row, 6, pl_item)
            
    def update_data(self):
        # Generate dates for the last 30 days
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dates = []
        for i in range(30):
            date = end_date - timedelta(days=i)
            dates.append(date)
        dates.reverse()  # Put in chronological order

        # Generate some sample growth values
        growth_values = []
        current_value = 10000  # Starting value
        for i in range(30):
            change = random.uniform(-0.02, 0.03)  # Random change between -2% and +3%
            current_value *= (1 + change)
            growth_values.append(current_value)

        # Update the growth chart
        self.growth_chart.set_title("Account Growth")
        self.growth_chart.update_data(
            dates,
            [growth_values],
            ['#00ff00']
        )

        # Generate timestamps for the last 7 days with hourly data
        end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        timestamps = []
        for i in range(7 * 24):  # 7 days * 24 hours
            time = end_time - timedelta(hours=i)
            timestamps.append(time)
        timestamps.reverse()  # Put in chronological order

        # Generate sample balance and equity data
        balance = []
        equity = []
        current_balance = 10000
        current_equity = 10000
        
        for i in range(len(timestamps)):
            balance_change = random.uniform(-0.01, 0.015)
            equity_change = random.uniform(-0.012, 0.018)
            
            current_balance *= (1 + balance_change)
            current_equity *= (1 + equity_change)
            
            balance.append(current_balance)
            equity.append(current_equity)

        # Update the equity chart
        self.equity_chart.set_title("Balance/Equity")
        self.equity_chart.update_data(
            timestamps,
            [balance, equity],
            ['#4CAF50', '#2196F3']  # Green for balance, Blue for equity
        ) 

    def show_account_setup(self):
        """Show the account setup dialog"""
        dialog = AccountSetupDialog(self)
        if dialog.exec() == AccountSetupDialog.Accepted:
            account_data = dialog.get_account_data()
            # Add the new account to the combo box
            account_name = f"{account_data['login']} ({account_data['server']})"
            self.account_combo.addItem(account_name)
            # Select the new account
            self.account_combo.setCurrentText(account_name)
            # TODO: Save account data to persistent storage 