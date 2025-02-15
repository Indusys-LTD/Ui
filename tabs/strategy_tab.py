from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                               QFrame, QComboBox, QPushButton, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from widgets.line_chart import LineChartWidget
import random
from datetime import datetime, timedelta

class StrategyTab(QWidget):
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
        
        # Strategy Selection
        strategy_label = QLabel("Strategy:")
        strategy_label.setStyleSheet("color: #FFFFFF;")
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "All Strategies",
            "Trend Following",
            "Mean Reversion",
            "Breakout",
            "ML-Based",
            "Statistical Arbitrage"
        ])
        self.strategy_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        
        top_layout.addWidget(strategy_label)
        top_layout.addWidget(self.strategy_combo)
        top_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Strategy Performance
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Strategy Performance Metrics
        metrics_header = QLabel("Strategy Performance Metrics")
        metrics_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(metrics_header)
        
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        # Create metric displays
        self.create_metric_display(metrics_layout, "Win Rate", "78.5%")
        self.create_metric_display(metrics_layout, "Profit Factor", "2.5")
        self.create_metric_display(metrics_layout, "Sharpe Ratio", "1.87")
        self.create_metric_display(metrics_layout, "Max Drawdown", "-12.3%")
        
        left_layout.addLayout(metrics_layout)
        left_layout.addSpacing(20)
        
        # Strategy Performance Chart
        performance_header = QLabel("Cumulative Performance")
        performance_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(performance_header)
        
        self.performance_chart = LineChartWidget(y_axis_position='left')
        left_layout.addWidget(self.performance_chart.get_canvas())
        left_layout.addSpacing(20)
        
        # Strategy Correlation Matrix
        correlation_header = QLabel("Strategy Correlation Matrix")
        correlation_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(correlation_header)
        
        self.correlation_table = self.create_table([
            "Strategy", "Trend", "Mean Rev", "Breakout", "ML", "Stat Arb"
        ])
        left_layout.addWidget(self.correlation_table)
        
        # Right side - Strategy Details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Strategy Parameters
        params_header = QLabel("Strategy Parameters")
        params_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(params_header)
        
        self.params_table = self.create_table([
            "Parameter", "Current Value", "Optimal Range", "Last Updated"
        ])
        right_layout.addWidget(self.params_table)
        right_layout.addSpacing(20)
        
        # Strategy Allocation
        allocation_header = QLabel("Capital Allocation")
        allocation_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(allocation_header)
        
        self.allocation_table = self.create_table([
            "Strategy", "Allocation %", "Risk %", "Return %", "Sharpe"
        ])
        right_layout.addWidget(self.allocation_table)
        right_layout.addSpacing(20)
        
        # Model Performance (for ML strategies)
        model_header = QLabel("Model Performance")
        model_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(model_header)
        
        # Accuracy Progress Bar
        accuracy_layout = QHBoxLayout()
        accuracy_label = QLabel("Prediction Accuracy:")
        accuracy_label.setStyleSheet("color: #FFFFFF;")
        accuracy_layout.addWidget(accuracy_label)
        
        self.accuracy_bar = QProgressBar()
        self.accuracy_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                text-align: center;
                background-color: #1E1E1E;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        self.accuracy_bar.setValue(85)
        accuracy_layout.addWidget(self.accuracy_bar)
        right_layout.addLayout(accuracy_layout)
        
        # Feature Importance Table
        self.feature_table = self.create_table([
            "Feature", "Importance", "Trend", "Last Update"
        ])
        right_layout.addWidget(self.feature_table)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
        
    def create_metric_display(self, parent_layout, label_text, initial_value):
        """Create a metric display with label and value"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        label = QLabel(label_text)
        label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        value = QLabel(initial_value)
        value.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
        
        layout.addWidget(label)
        layout.addWidget(value)
        parent_layout.addLayout(layout)
        
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
        # Correlation Matrix Data
        correlation_data = [
            ["Trend", "1.00", "0.15", "0.45", "0.35", "0.25"],
            ["Mean Rev", "0.15", "1.00", "0.20", "0.40", "0.30"],
            ["Breakout", "0.45", "0.20", "1.00", "0.55", "0.15"],
            ["ML", "0.35", "0.40", "0.55", "1.00", "0.45"],
            ["Stat Arb", "0.25", "0.30", "0.15", "0.45", "1.00"]
        ]
        self.populate_table(self.correlation_table, correlation_data)
        
        # Strategy Parameters Data
        params_data = [
            ["Lookback Period", "20", "15-25", "2024-03-15"],
            ["Volatility Threshold", "2.5", "2.0-3.0", "2024-03-15"],
            ["Stop Loss %", "1.5", "1.0-2.0", "2024-03-15"],
            ["Take Profit %", "3.0", "2.5-4.0", "2024-03-15"],
            ["Position Size %", "2.0", "1.5-2.5", "2024-03-15"]
        ]
        self.populate_table(self.params_table, params_data)
        
        # Allocation Data
        allocation_data = [
            ["Trend Following", "30%", "25%", "18.5%", "1.85"],
            ["Mean Reversion", "20%", "15%", "12.3%", "1.65"],
            ["Breakout", "15%", "20%", "15.7%", "1.45"],
            ["ML-Based", "25%", "30%", "22.4%", "2.15"],
            ["Statistical Arbitrage", "10%", "10%", "8.9%", "1.95"]
        ]
        self.populate_table(self.allocation_table, allocation_data)
        
        # Feature Importance Data
        feature_data = [
            ["Price Momentum", "85%", "↑", "2024-03-15"],
            ["Volume", "75%", "↓", "2024-03-15"],
            ["Volatility", "70%", "→", "2024-03-15"],
            ["RSI", "65%", "↑", "2024-03-15"],
            ["Moving Averages", "60%", "↓", "2024-03-15"]
        ]
        self.populate_table(self.feature_table, feature_data)
        
        # Generate performance chart data
        dates = []
        strategy_returns = []
        benchmark_returns = []
        
        end_date = datetime.now()
        strategy_value = 10000
        benchmark_value = 10000
        
        for i in range(180):  # 6 months of daily data
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Generate realistic returns
            strategy_change = random.uniform(-0.015, 0.02)
            benchmark_change = random.uniform(-0.01, 0.015)
            
            strategy_value *= (1 + strategy_change)
            benchmark_value *= (1 + benchmark_change)
            
            strategy_returns.append(strategy_value)
            benchmark_returns.append(benchmark_value)
        
        dates.reverse()
        strategy_returns.reverse()
        benchmark_returns.reverse()
        
        # Update performance chart
        self.performance_chart.update_data(
            dates,
            [strategy_returns, benchmark_returns],
            ['#4CAF50', '#666666']  # Green for strategy, gray for benchmark
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
                        pct = float(value.replace('%', ''))
                        if pct >= 80:
                            item.setForeground(QColor("#4CAF50"))
                        elif pct >= 60:
                            item.setForeground(QColor("#FFC107"))
                        else:
                            item.setForeground(QColor("#F44336"))
                    except ValueError:
                        pass
                elif '↑' in value:
                    item.setForeground(QColor("#4CAF50"))
                elif '↓' in value:
                    item.setForeground(QColor("#F44336"))
                elif col == 0 and row == col:  # Diagonal in correlation matrix
                    item.setForeground(QColor("#4CAF50"))
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30) 