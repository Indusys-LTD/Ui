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
        
        # Account Selection and Setup
        account_layout = QHBoxLayout()
        
        # Account combo box
        account_label = QLabel("Account:")
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Account 1 (Main)", "Account 2 (Demo)", "Account 3 (Test)"])
        self.account_combo.currentIndexChanged.connect(self.on_account_changed)
        
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
        
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_combo)
        account_layout.addWidget(self.setup_account_btn)
        account_layout.addStretch()
        
        main_layout.addLayout(account_layout)
        
        # Create splitter for flexible layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Account metrics and ratios
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Account Metrics Section
        metrics_frame = self.create_section("Account Metrics")
        metrics_grid = QGridLayout()
        
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
                
        metrics_frame.layout().addLayout(metrics_grid)
        left_layout.addWidget(metrics_frame)
        
        # Trading Ratios Section
        ratios_frame = self.create_section("Trading Ratios")
        ratios_grid = QGridLayout()
        
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
                
        ratios_frame.layout().addLayout(ratios_grid)
        left_layout.addWidget(ratios_frame)
        
        # Account Growth Chart
        growth_frame = self.create_section("Account Growth")
        self.growth_chart = LineChartWidget()
        growth_frame.layout().addWidget(self.growth_chart.get_canvas())
        left_layout.addWidget(growth_frame)
        
        # Right side - Open positions and equity chart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Open Positions Section
        positions_frame = self.create_section("Open Positions")
        
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
            }
            QHeaderView::section {
                background-color: #333333;
                color: #FFFFFF;
                padding: 5px;
            }
        """)
        
        positions_frame.layout().addWidget(self.positions_table)
        right_layout.addWidget(positions_frame)
        
        # Equity/Balance Chart
        equity_frame = self.create_section("Equity/Balance")
        self.equity_chart = LineChartWidget()
        equity_frame.layout().addWidget(self.equity_chart.get_canvas())
        right_layout.addWidget(equity_frame)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        
        main_layout.addWidget(splitter)
        
    def create_section(self, title):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        return frame
        
    def create_metric_widget(self, label_text, initial_value=""):
        layout = QHBoxLayout()
        
        label = QLabel(label_text)
        value = QLabel(initial_value)
        value.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(value)
        layout.addStretch()
        
        return layout
        
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