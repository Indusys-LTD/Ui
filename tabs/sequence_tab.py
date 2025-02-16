from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QFrame, QLabel, QScrollArea)
from PySide6.QtCore import Qt
from datetime import datetime, timedelta

class SequenceTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none;
                background-color: #1E1E1E;
            }
            QScrollBar:vertical {
                background-color: #1E1E1E;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3D3D3D;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("Trading Sequence Performance Report")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        container_layout.addWidget(title)
        
        # First Row of Grouped Tables
        first_row = QHBoxLayout()
        first_row.setSpacing(10)
        
        # Risk Analysis Summary
        risk_section = self.create_section("Risk Analysis Summary")
        self.risk_table = self.create_table(["Metric", "Value"])
        risk_section.layout().addWidget(self.risk_table)
        first_row.addWidget(risk_section, 1)
        
        # Market Context Analysis
        market_section = self.create_section("Market Context Analysis")
        self.market_table = self.create_table(["Metric", "Value"])
        market_section.layout().addWidget(self.market_table)
        first_row.addWidget(market_section, 1)
        
        # Time Distribution Analysis
        time_section = self.create_section("Time Distribution Analysis")
        self.time_table = self.create_table(["Period", "Hour", "Day", "Week", "Month", "Year"])
        time_section.layout().addWidget(self.time_table)
        
        container_layout.addWidget(time_section)
        container_layout.addLayout(first_row)
        
        # Second Row of Grouped Tables
        second_row = QHBoxLayout()
        second_row.setSpacing(10)
        
        # Sequence Performance Summary
        performance_section = self.create_section("Sequence Performance Summary")
        self.performance_table = self.create_table(["Metric", "Value"])
        performance_section.layout().addWidget(self.performance_table)
        second_row.addWidget(performance_section, 1)
        
        # Best/Worst Sequence Analysis
        sequence_section = self.create_section("Best/Worst Sequence Analysis")
        self.sequence_table = self.create_table(["Metric", "Best Sequence", "Worst Sequence"])
        sequence_section.layout().addWidget(self.sequence_table)
        second_row.addWidget(sequence_section, 1)
        
        container_layout.addLayout(second_row)
        
        # Cost Analysis Summary
        cost_section = self.create_section("Cost Analysis Summary")
        self.cost_table = self.create_table(["Metric", "Value"])
        cost_section.layout().addWidget(self.cost_table)
        container_layout.addWidget(cost_section)
        
        # Market Session Performance Analysis
        session_section = self.create_section("Market Session Performance Analysis")
        session_layout = QVBoxLayout()
        session_layout.setSpacing(5)
        
        # Create session table
        self.session_table = self.create_table([
            "Session", "Total Trades", "Win Rate (%)", "Total Profit", "Avg Profit/Trade"
        ])        
        session_layout.addWidget(self.session_table)
        
        # Add best session label
        self.best_session_label = QLabel()
        self.best_session_label.setStyleSheet("color: #4CAF50; padding: 5px 0;")
        session_layout.addWidget(self.best_session_label)
        
        session_section.layout().addLayout(session_layout)
        container_layout.addWidget(session_section)
        
        # Active Sequences Detail
        active_section = self.create_section("Active Sequences Detail")
        self.active_table = self.create_table([
            "Sequence", "Trades", "Win Rate", "Profit", "Avg Profit", 
            "Risk-Reward", "Hold Time", "Sharpe", "Max Pos Size", "Concurrent Pos"
        ])
        active_section.layout().addWidget(self.active_table)
        container_layout.addWidget(active_section)
        
        # Set scroll widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def create_section(self, title):
        """Create a minimal section with title"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        header = QLabel(title)
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        return container
        
    def create_table(self, headers):
        """Create a styled table widget"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Adjust minimum sizes based on table type
        if len(headers) <= 2:  # Small tables (metric-value pairs)
            table.setMinimumHeight(100)
            min_width = 250
        else:  # Larger tables
            table.setMinimumHeight(150)
            min_width = 120 * len(headers)
        
        table.setMinimumWidth(min_width)
        
        # Disable editing
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set selection behavior
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set column resize modes based on content type
        if len(headers) == 2:  # Metric-Value tables
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        else:
            # For other tables, set specific column behaviors
            for i in range(len(headers)):
                if headers[i] in ["Period", "Sequence", "Session", "Metric"]:
                    table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
                elif headers[i] in ["Hold Time", "Win Rate", "Risk-Reward"]:
                    table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
                    table.setColumnWidth(i, 100)
                else:
                    table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Set table properties
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #2D2D2D;
                color: #FFFFFF;
                gridline-color: #3D3D3D;
                border: none;
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
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        
        return table
        
    def load_sample_data(self):
        # Time Distribution Analysis
        self.time_table.setRowCount(2)
        time_data = [
            ["Most Active", "00:00", "Day 0", "Week 0", "Month 0", "0"],
            ["Sequence Count", "0", "0", "0", "0", "0"]
        ]
        self.populate_table(self.time_table, time_data)
        
        # Risk Analysis Summary
        self.risk_table.setRowCount(3)
        risk_data = [
            ["Average Max Position Size", "0.33"],
            ["Average Concurrent Positions", "1"],
            ["Average Sharpe Ratio", "0"]
        ]
        self.populate_table(self.risk_table, risk_data)
        
        # Market Context Analysis
        self.market_table.setRowCount(2)
        market_data = [
            ["Average Spread", "0.00000"],
            ["Volume 0.33", "100.00%"]
        ]
        self.populate_table(self.market_table, market_data)
        
        # Sequence Performance Summary
        self.performance_table.setRowCount(10)
        performance_data = [
            ["Total Sequences", "37"],
            ["Average Positions/Sequence", "0.05"],
            ["Average Profit/Sequence", "$-1.88"],
            ["Average Sequence Hold Time", "0:45:32.643507"],
            ["Maximum Hold Time", "16:00:11.404876"],
            ["Minimum Hold Time", "0:00:00"],
            ["Buy Sequences", "1 ($-56.22)"],
            ["Sell Sequences", "36 ($-13.20)"],
            ["Best Performing Type", "Sell"]
        ]
        self.populate_table(self.performance_table, performance_data)
        
        # Best/Worst Sequence Analysis
        self.sequence_table.setRowCount(7)
        sequence_data = [
            ["Sequence ID", "2502142252_4", "2502141859_78"],
            ["Total Profit", "0.00", "-56.22"],
            ["Win Rate", "0.00%", "0.00%"],
            ["Trade Count", "0", "1"],
            ["Risk-Reward Ratio", "0.00", "0.00"],
            ["Sharpe Ratio", "0.00", "0.00"],
            ["Max Position Size", "0.00", "0.33"]
        ]
        self.populate_table(self.sequence_table, sequence_data)
        
        # Active Sequences Detail
        self.active_table.setRowCount(2)
        active_data = [
            ["2502141859_78", "1", "0.00%", "-56.22", "-56.22", "0.00", 
             "16:00:11.404876", "0.00", "0.33", "1"],
            ["2502142254_967", "1", "0.00%", "-13.20", "-13.20", "0.00", 
             "12:04:56.404876", "0.00", "0.33", "1"]
        ]
        self.populate_table(self.active_table, active_data)
        
        # Market Session Performance
        self.session_table.setRowCount(2)
        session_data = [
            ["New York", "1", "0.00", "-56.00", "-56.00"],
            ["Tokyo", "1", "0.00", "-38.00", "-38.00"]
        ]
        
        # Populate session table
        for row, row_data in enumerate(session_data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                
                # Set alignment
                if col == 0:  # Session name
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:  # Numeric values
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    # Format numeric values
                    if col == 2:  # Win Rate column
                        item.setText(f"{float(value):.2f}%")
                    elif col in [3, 4]:  # Profit columns
                        item.setText(f"${float(value):.2f}")
                
                # Set colors for profit/loss and percentages
                if col in [3, 4]:  # Profit columns
                    try:
                        profit = float(value)
                        item.setForeground(Qt.green if profit >= 0 else Qt.red)
                    except ValueError:
                        pass
                elif col == 2:  # Win Rate column
                    try:
                        win_rate = float(value)
                        item.setForeground(Qt.green if win_rate > 0 else Qt.white)
                    except ValueError:
                        pass
                
                self.session_table.setItem(row, col, item)
        
        # Set row height and adjust table size
        self.session_table.setRowHeight(0, 40)
        self.session_table.setFixedHeight(self.session_table.horizontalHeader().height() + 42)  # Header height + row height + 2px border
        
        self.best_session_label.setText("Best Performing Session: New York (Profit: $-56.00)")
        
        # Cost Analysis Summary
        self.cost_table.setRowCount(3)
        cost_data = [
            ["Total Swap Costs", "$-0.53"],
            ["Weekend Swap Impact", "$-0.53"],
            ["Swap Cost Ratio", "100.00%"]
        ]
        self.populate_table(self.cost_table, cost_data)
        
    def populate_table(self, table, data):
        """Helper method to populate a table with data"""
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                # Convert value to string for display
                str_value = str(value)
                item = QTableWidgetItem(str_value)
                
                # Set alignment based on content type
                if isinstance(value, (int, float)) or (isinstance(str_value, str) and str_value.replace('.', '').replace('-', '').replace('$', '').replace('%', '').isdigit()):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    # Format numeric values for session table
                    if table == self.session_table and col > 0:
                        if col == 2:  # Win Rate column
                            item.setText(f"{float(value):.2f}%")
                        elif col in [3, 4]:  # Profit columns
                            item.setText(f"${float(value):.2f}")
                        else:  # Other numeric columns
                            item.setText(f"{float(value)}")
                elif col == 0:  # First column (usually labels/names)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                
                # Color formatting for specific values
                if '$' in str_value or (table == self.session_table and col in [3, 4]):  # Total Profit and Avg Profit/Trade
                    try:
                        float_value = float(str_value.replace('$', '')) if isinstance(str_value, str) else float(value)
                        if float_value < 0:
                            item.setForeground(Qt.red)
                        else:
                            item.setForeground(Qt.green)
                    except ValueError:
                        pass
                elif '%' in str_value or (table == self.session_table and col == 2):  # Win Rate column
                    try:
                        percent_value = float(str_value.replace('%', '')) if isinstance(str_value, str) else float(value)
                        if percent_value > 0:
                            item.setForeground(Qt.green)
                        elif percent_value < 0:
                            item.setForeground(Qt.red)
                        else:
                            item.setForeground(Qt.white)  # Neutral color for 0%
                    except ValueError:
                        pass
                
                table.setItem(row, col, item)
            
        # Adjust row heights
        for row in range(table.rowCount()):
            table.setRowHeight(row, 40)
            
        # Adjust table height to content
        table_height = (table.rowCount() * 40) + table.horizontalHeader().height() + 2
        table.setMinimumHeight(table_height) 