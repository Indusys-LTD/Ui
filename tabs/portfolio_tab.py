from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                              QPushButton, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                              QComboBox, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from widgets import PieChartWidget, LineChartWidget
import random
from datetime import datetime, timedelta

class PortfolioTab(QWidget):
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
        
        # Portfolio Value Display
        value_frame = QFrame()
        value_frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 5px; padding: 10px; }")
        value_layout = QVBoxLayout(value_frame)
        
        self.total_value_label = QLabel("Total Portfolio Value")
        self.total_value_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.total_value = QLabel("$125,432.50")
        self.total_value.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
        
        value_layout.addWidget(self.total_value_label)
        value_layout.addWidget(self.total_value)
        
        # Portfolio Performance
        perf_frame = QFrame()
        perf_frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 5px; padding: 10px; }")
        perf_layout = QHBoxLayout(perf_frame)
        
        # Daily Change
        daily_layout = QVBoxLayout()
        daily_label = QLabel("24h Change")
        daily_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.daily_value = QLabel("+2.5%")
        self.daily_value.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        daily_layout.addWidget(daily_label)
        daily_layout.addWidget(self.daily_value)
        
        # Weekly Change
        weekly_layout = QVBoxLayout()
        weekly_label = QLabel("7d Change")
        weekly_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.weekly_value = QLabel("+5.8%")
        self.weekly_value.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        weekly_layout.addWidget(weekly_label)
        weekly_layout.addWidget(self.weekly_value)
        
        # Monthly Change
        monthly_layout = QVBoxLayout()
        monthly_label = QLabel("30d Change")
        monthly_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.monthly_value = QLabel("+12.3%")
        self.monthly_value.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
        monthly_layout.addWidget(monthly_label)
        monthly_layout.addWidget(self.monthly_value)
        
        perf_layout.addLayout(daily_layout)
        perf_layout.addLayout(weekly_layout)
        perf_layout.addLayout(monthly_layout)
        
        # View Controls
        controls_layout = QHBoxLayout()
        
        # Asset Type Filter
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems(["All Assets", "Currencies", "Stocks", "Crypto"])
        self.asset_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Time Range Buttons
        self.time_range_buttons = []
        for period in ["1D", "1W", "1M", "3M", "1Y", "ALL"]:
            btn = QPushButton(period)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:checked {
                    background-color: #4CAF50;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
            """)
            self.time_range_buttons.append(btn)
            controls_layout.addWidget(btn)
        
        # Add all top section elements
        top_layout.addWidget(value_frame)
        top_layout.addWidget(perf_frame)
        top_layout.addStretch()
        top_layout.addWidget(self.asset_type_combo)
        
        main_layout.addLayout(top_layout)
        main_layout.addLayout(controls_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Portfolio Composition and Performance
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Portfolio Composition Section
        composition_header = QLabel("Portfolio Composition")
        composition_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(composition_header)
        
        self.composition_table = self.create_table([
            "Asset", "Type", "Amount", "Value", "24h Change", "Weight"
        ])
        left_layout.addWidget(self.composition_table)
        
        # Portfolio Performance Chart
        performance_header = QLabel("Portfolio Performance")
        performance_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 15px;")
        left_layout.addWidget(performance_header)
        
        self.performance_chart = LineChartWidget(y_axis_position='left')
        left_layout.addWidget(self.performance_chart.get_canvas())
        
        # Right side - Asset Analysis and Metrics
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Asset Metrics Section
        metrics_header = QLabel("Asset Metrics")
        metrics_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(metrics_header)
        
        self.metrics_table = self.create_table([
            "Metric", "Currencies", "Stocks", "Crypto", "Total"
        ])
        right_layout.addWidget(self.metrics_table)
        
        # Asset Distribution Chart
        distribution_header = QLabel("Asset Distribution")
        distribution_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 15px;")
        right_layout.addWidget(distribution_header)
        
        self.distribution_chart = LineChartWidget(y_axis_position='left')
        right_layout.addWidget(self.distribution_chart.get_canvas())
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
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
        
    def load_sample_data(self):
        """Load sample data for all widgets"""
        # Portfolio Composition Data
        composition_data = [
            ["EURUSD", "Currency", "100,000", "$108,750", "+1.2%", "15.3%"],
            ["AAPL", "Stock", "500", "$95,500", "+2.5%", "13.4%"],
            ["BTCUSD", "Crypto", "2.5", "$85,250", "-1.8%", "12.0%"],
            ["GBPUSD", "Currency", "75,000", "$82,500", "+0.8%", "11.6%"],
            ["MSFT", "Stock", "250", "$75,000", "+1.5%", "10.5%"],
            ["USDJPY", "Currency", "10,000,000", "$67,500", "-0.5%", "9.5%"],
            ["ETHBTC", "Crypto", "25", "$65,000", "+3.2%", "9.1%"],
            ["GOOGL", "Stock", "50", "$62,500", "+1.8%", "8.8%"],
            ["XAUUSD", "Currency", "40", "$45,000", "+0.3%", "6.3%"],
            ["TSLA", "Stock", "100", "$25,000", "-2.1%", "3.5%"]
        ]
        self.populate_table(self.composition_table, composition_data)
        
        # Asset Metrics Data
        metrics_data = [
            ["Total Value", "$303,750", "$258,000", "$150,250", "$712,000"],
            ["24h Change", "+0.8%", "+1.9%", "+0.7%", "+1.2%"],
            ["7d Change", "+2.3%", "+4.5%", "+3.2%", "+3.4%"],
            ["30d Change", "+5.6%", "+8.9%", "+7.4%", "+7.3%"],
            ["Weight", "42.7%", "36.2%", "21.1%", "100%"],
            ["Volatility", "8.5%", "12.3%", "25.6%", "13.8%"]
        ]
        self.populate_table(self.metrics_table, metrics_data)
        
        # Generate performance chart data
        dates = []
        portfolio_values = []
        currency_values = []
        stock_values = []
        crypto_values = []
        
        end_date = datetime.now()
        base_value = 712000  # Current total value
        
        for i in range(180):  # 6 months of daily data
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Generate realistic value changes
            daily_change = random.uniform(-0.02, 0.025)
            base_value = base_value / (1 + daily_change)  # Work backwards
            
            portfolio_values.append(base_value)
            currency_values.append(base_value * 0.427)  # 42.7% of total
            stock_values.append(base_value * 0.362)    # 36.2% of total
            crypto_values.append(base_value * 0.211)   # 21.1% of total
        
        dates.reverse()
        portfolio_values.reverse()
        currency_values.reverse()
        stock_values.reverse()
        crypto_values.reverse()
        
        # Update performance chart
        self.performance_chart.update_data(
            dates,
            [portfolio_values, currency_values, stock_values, crypto_values],
            ['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']
        )
        
        # Update distribution chart (using the same data but different visualization)
        self.distribution_chart.update_data(
            dates[-30:],  # Last 30 days only
            [currency_values[-30:], stock_values[-30:], crypto_values[-30:]],
            ['#2196F3', '#FFC107', '#9C27B0']
        )
        
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
                        pct = float(value.replace('%', '').replace('+', ''))
                        if '+' in value:
                            item.setForeground(QColor("#4CAF50"))  # Green for positive
                        elif '-' in value:
                            item.setForeground(QColor("#F44336"))  # Red for negative
                    except ValueError:
                        pass
                elif '$' in value and col not in [0]:  # Don't color asset names
                    item.setForeground(QColor("#4CAF50"))
                elif value in ['Currency', 'Stock', 'Crypto']:
                    if value == 'Currency':
                        item.setForeground(QColor("#2196F3"))
                    elif value == 'Stock':
                        item.setForeground(QColor("#FFC107"))
                    else:
                        item.setForeground(QColor("#9C27B0"))
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30)
            
    def update_metrics(self, metrics):
        """Update portfolio metrics with new values
        
        Args:
            metrics (dict): Dictionary containing portfolio metrics
                - total_value (float): Total portfolio value
                - profit_factor (float): Profit factor
                - netto_profit (float): Net profit
                - fees (float): Total fees
        """
        if 'total_value' in metrics:
            self.total_value.setText(f"${metrics['total_value']:,.2f}")
        if 'profit_factor' in metrics:
            self.daily_value.setText(f"+{(metrics['profit_factor'] - 1) * 100:.1f}%")
        if 'netto_profit' in metrics:
            self.weekly_value.setText(f"+{metrics['netto_profit'] / metrics['total_value'] * 100:.1f}%")
        if 'fees' in metrics:
            fee_pct = metrics['fees'] / metrics['total_value'] * 100
            self.monthly_value.setText(f"-{fee_pct:.1f}%") 