import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel,
                             QComboBox, QPushButton, QHBoxLayout, QHeaderView)
from PySide6.QtCore import Qt
import pandas as pd
from datetime import datetime, timedelta
from database.read import DatabaseReader

class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MetaTrader Account Analysis")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize database reader
        self.db_reader = DatabaseReader()
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create filter controls
        filter_layout = QHBoxLayout()
        
        # Account selector
        self.account_combo = QComboBox()
        self.account_combo.currentIndexChanged.connect(self.update_data)
        filter_layout.addWidget(QLabel("Account:"))
        filter_layout.addWidget(self.account_combo)
        
        # Date selector
        self.date_combo = QComboBox()
        self.date_combo.currentIndexChanged.connect(self.update_data)
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.date_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create individual tabs
        self.overview_tab = QWidget()
        self.risk_tab = QWidget()
        self.forecast_tab = QWidget()
        
        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.risk_tab, "Risk Analysis")
        self.tabs.addTab(self.forecast_tab, "Forecasts")
        
        # Setup tab layouts
        self.setup_overview_tab()
        self.setup_risk_tab()
        self.setup_forecast_tab()
        
        # Initial data load
        self.refresh_data()
        
    def setup_overview_tab(self):
        layout = QVBoxLayout(self.overview_tab)
        
        # Basic metrics table
        self.basic_metrics_table = QTableWidget()
        layout.addWidget(QLabel("Basic Metrics"))
        layout.addWidget(self.basic_metrics_table)
        
        # Performance metrics table
        self.performance_metrics_table = QTableWidget()
        layout.addWidget(QLabel("Performance Metrics"))
        layout.addWidget(self.performance_metrics_table)
        
    def setup_risk_tab(self):
        layout = QVBoxLayout(self.risk_tab)
        
        # Risk metrics table
        self.risk_metrics_table = QTableWidget()
        layout.addWidget(QLabel("Risk Metrics"))
        layout.addWidget(self.risk_metrics_table)
        
        # Advanced risk metrics table
        self.advanced_risk_table = QTableWidget()
        layout.addWidget(QLabel("Advanced Risk Metrics"))
        layout.addWidget(self.advanced_risk_table)
        
    def setup_forecast_tab(self):
        layout = QVBoxLayout(self.forecast_tab)
        
        # Forecast scenarios table
        self.forecast_scenarios_table = QTableWidget()
        layout.addWidget(QLabel("Forecast Scenarios"))
        layout.addWidget(self.forecast_scenarios_table)
        
        # Symbol forecasts table
        self.symbol_forecasts_table = QTableWidget()
        layout.addWidget(QLabel("Symbol Forecasts"))
        layout.addWidget(self.symbol_forecasts_table)
        
    def refresh_data(self):
        # Update account list
        accounts = self.db_reader.get_available_accounts()
        self.account_combo.clear()
        self.account_combo.addItems(accounts)
        
        # Update date list
        dates = self.db_reader.get_available_dates()
        self.date_combo.clear()
        self.date_combo.addItems(dates)
        
        self.update_data()
        
    def update_data(self):
        if not self.account_combo.currentText() or not self.date_combo.currentText():
            return
            
        account = None if self.account_combo.currentText() == "All Accounts" else int(self.account_combo.currentText())
        date = self.date_combo.currentText()
        
        # Update Overview Tab
        basic_df, perf_df = self.db_reader.get_overview_data(account, date)
        self.update_table(self.basic_metrics_table, basic_df)
        self.update_table(self.performance_metrics_table, perf_df)
        
        # Update Risk Tab
        risk_df, adv_risk_df = self.db_reader.get_risk_data(account, date)
        self.update_table(self.risk_metrics_table, risk_df)
        self.update_table(self.advanced_risk_table, adv_risk_df)
        
        # Update Forecast Tab
        scenarios_df, symbols_df = self.db_reader.get_forecast_data(account, date)
        self.update_table(self.forecast_scenarios_table, scenarios_df)
        self.update_table(self.symbol_forecasts_table, symbols_df)
                
    def update_table(self, table: QTableWidget, df: pd.DataFrame):
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        
        # Set headers
        table.setHorizontalHeaderLabels(df.columns)
        
        # Set data
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                value = df.iloc[i, j]
                if isinstance(value, float):
                    value = f"{value:.4f}"
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Color coding for PnL and percentage values
                if isinstance(value, (float, str)) and df.columns[j].lower() in ['pnl', 'profit', 'change_%', 'profit_%']:
                    try:
                        num_value = float(str(value).replace('%', ''))
                        if num_value > 0:
                            item.setForeground(Qt.darkGreen)
                        elif num_value < 0:
                            item.setForeground(Qt.red)
                    except ValueError:
                        pass
                
                table.setItem(i, j, item)
        
        # Adjust column widths
        header = table.horizontalHeader()
        for i in range(df.shape[1]):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        # Set alternating row colors
        table.setAlternatingRowColors(True)

def main():
    app = QApplication(sys.argv)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 