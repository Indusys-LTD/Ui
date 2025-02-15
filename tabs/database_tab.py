from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame, QTableWidget, QTableWidgetItem,
                               QHeaderView, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
import random
from datetime import datetime, timedelta

class DatabaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create horizontal splitter for main sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Database Overview and Performance
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Database Overview Section
        overview_header = QLabel("🗄️ DATABASE OVERVIEW")
        overview_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(overview_header)
        
        # Database Stats
        stats_layout = QHBoxLayout()
        self.db_size = QLabel("Database Size: 2.45 GB")
        self.db_size.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.table_count = QLabel("Tables: 24")
        self.table_count.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.active_connections = QLabel("Active Connections: 12/100")
        self.active_connections.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        stats_layout.addWidget(self.db_size)
        stats_layout.addWidget(self.table_count)
        stats_layout.addWidget(self.active_connections)
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        # Table Space Usage
        space_label = QLabel("Table Space Usage:")
        space_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        left_layout.addWidget(space_label)
        
        self.space_table = self.create_table([
            "Table Name", "Size", "Index Size", "Total Size", "Row Count"
        ])
        left_layout.addWidget(self.space_table)
        
        # Query Performance Section
        performance_header = QLabel("📊 QUERY PERFORMANCE")
        performance_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        left_layout.addWidget(performance_header)
        
        # Slow Queries Table
        slow_label = QLabel("Slow Queries (>1000ms):")
        slow_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        left_layout.addWidget(slow_label)
        
        self.slow_queries_table = self.create_table([
            "Query", "Duration (ms)", "Calls", "Rows", "Cache Hit Ratio"
        ])
        left_layout.addWidget(self.slow_queries_table)
        
        # Right side - System Metrics and Maintenance
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # System Metrics Section
        metrics_header = QLabel("📈 SYSTEM METRICS")
        metrics_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(metrics_header)
        
        # Cache Stats Table
        cache_label = QLabel("Cache Statistics:")
        cache_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        right_layout.addWidget(cache_label)
        
        self.cache_table = self.create_table([
            "Metric", "Value", "Percentage"
        ])
        right_layout.addWidget(self.cache_table)
        
        # Index Health Section
        index_header = QLabel("🔍 INDEX HEALTH")
        index_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        right_layout.addWidget(index_header)
        
        # Index Usage Table
        index_label = QLabel("Index Usage Statistics:")
        index_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        right_layout.addWidget(index_label)
        
        self.index_table = self.create_table([
            "Index Name", "Table", "Size", "Scans", "Unused"
        ])
        right_layout.addWidget(self.index_table)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
    def create_table(self, headers):
        """Create a styled table widget"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #2D2D2D;
                color: #FFFFFF;
                gridline-color: #3D3D3D;
                border: 1px solid #3D3D3D;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #FFFFFF;
                padding: 5px;
                border: none;
                border-bottom: 1px solid #3D3D3D;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
        """)
        
        # Set column resize modes
        for i in range(len(headers)):
            if i == 0:
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
                
        return table
        
    def setup_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(5000)  # Update every 5 seconds
        
    def load_sample_data(self):
        """Load initial sample data"""
        # Table Space Usage Data
        space_data = [
            ["trades", "1.2 GB", "450 MB", "1.65 GB", "5,234,567"],
            ["orders", "856 MB", "320 MB", "1.18 GB", "3,456,789"],
            ["accounts", "234 MB", "89 MB", "323 MB", "125,432"],
            ["positions", "567 MB", "178 MB", "745 MB", "2,345,678"],
            ["transactions", "890 MB", "256 MB", "1.15 GB", "4,567,890"]
        ]
        self.populate_table(self.space_table, space_data)
        
        # Slow Queries Data
        slow_queries_data = [
            ["SELECT * FROM trades WHERE date > ?", "2345", "1,234", "50,432", "85.4%"],
            ["UPDATE positions SET status = ?", "1876", "876", "23,456", "92.3%"],
            ["INSERT INTO transactions (VALUES)", "1543", "2,345", "78,654", "78.9%"],
            ["SELECT SUM(profit) FROM trades", "1234", "5,678", "1", "95.6%"],
            ["UPDATE account_balance SET value = ?", "1123", "3,456", "12,345", "88.7%"]
        ]
        self.populate_table(self.slow_queries_table, slow_queries_data)
        
        # Cache Statistics Data
        cache_data = [
            ["Buffer Cache Hit Ratio", "8.45 GB", "94.5%"],
            ["Shared Buffer Usage", "7.89 GB", "87.2%"],
            ["WAL Buffer Usage", "2.34 GB", "45.6%"],
            ["Effective Cache Size", "12.0 GB", "75.3%"],
            ["Temp Buffer Usage", "1.23 GB", "24.8%"]
        ]
        self.populate_table(self.cache_table, cache_data)
        
        # Index Usage Data
        index_data = [
            ["trades_date_idx", "trades", "234 MB", "45,678", "No"],
            ["orders_status_idx", "orders", "123 MB", "23,456", "No"],
            ["accounts_user_idx", "accounts", "45 MB", "12,345", "Yes"],
            ["positions_symbol_idx", "positions", "89 MB", "34,567", "No"],
            ["transactions_date_idx", "transactions", "156 MB", "56,789", "No"]
        ]
        self.populate_table(self.index_table, index_data)
        
    def update_metrics(self):
        """Update dynamic metrics"""
        # Update connection count
        current_connections = random.randint(8, 15)
        self.active_connections.setText(f"Active Connections: {current_connections}/100")
        
        # Update database size (simulate growth)
        current_size = float(self.db_size.text().split()[2])
        new_size = current_size + random.uniform(0.01, 0.05)
        self.db_size.setText(f"Database Size: {new_size:.2f} GB")
        
    def populate_table(self, table, data):
        """Populate a table with data and formatting"""
        table.setRowCount(len(data))
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                
                # Set alignment
                if col == 0:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Color formatting
                if '%' in value:
                    try:
                        pct = float(value.replace('%', ''))
                        if pct > 90:
                            item.setForeground(Qt.green)
                        elif pct < 70:
                            item.setForeground(Qt.red)
                        else:
                            item.setForeground(Qt.yellow)
                    except ValueError:
                        pass
                elif 'Yes' in value:
                    item.setForeground(Qt.red)  # Unused indexes in red
                elif 'ms' in value:
                    try:
                        duration = float(value.replace(' ms', ''))
                        if duration > 2000:
                            item.setForeground(Qt.red)
                        elif duration > 1500:
                            item.setForeground(Qt.yellow)
                    except ValueError:
                        pass
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30) 