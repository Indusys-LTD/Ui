from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
import random
from datetime import datetime, timedelta

class SequenceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create table for sequence data
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Time", "Operation", "Symbol", "Volume", "Price", "Profit/Loss"
        ])
        
        # Set table properties
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
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
        
        layout.addWidget(self.table)
        
    def load_sample_data(self):
        # Sample trade data
        operations = ["Buy", "Sell"]
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
        
        # Generate sample trades for the last 24 hours
        now = datetime.now()
        trades = []
        
        for i in range(20):
            time = now - timedelta(hours=random.randint(0, 24))
            operation = random.choice(operations)
            symbol = random.choice(symbols)
            volume = round(random.uniform(0.1, 2.0), 2)
            price = round(random.uniform(1.0, 50000.0), 2)
            pl = round(random.uniform(-500, 500), 2)
            
            trades.append({
                'time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'operation': operation,
                'symbol': symbol,
                'volume': volume,
                'price': price,
                'pl': pl
            })
            
        # Sort trades by time
        trades.sort(key=lambda x: x['time'], reverse=True)
        
        # Populate table
        self.table.setRowCount(len(trades))
        for row, trade in enumerate(trades):
            self.table.setItem(row, 0, QTableWidgetItem(trade['time']))
            
            operation_item = QTableWidgetItem(trade['operation'])
            operation_item.setForeground(
                Qt.green if trade['operation'] == "Buy" else Qt.red
            )
            self.table.setItem(row, 1, operation_item)
            
            self.table.setItem(row, 2, QTableWidgetItem(trade['symbol']))
            self.table.setItem(row, 3, QTableWidgetItem(str(trade['volume'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"${trade['price']:,.2f}"))
            
            pl_item = QTableWidgetItem(f"${trade['pl']:+,.2f}")
            pl_item.setForeground(Qt.green if trade['pl'] >= 0 else Qt.red)
            self.table.setItem(row, 5, pl_item) 