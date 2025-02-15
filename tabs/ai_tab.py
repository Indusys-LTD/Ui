from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QSplitter)
from PySide6.QtCore import Qt
from widgets.line_chart import LineChartWidget
import random
from datetime import datetime, timedelta

class AITab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create horizontal splitter for main sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - ML Insights and Performance
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # ML Insights Section
        ml_header = QLabel("🤖 ML INSIGHTS")
        ml_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(ml_header)
        
        # Pattern Detection Stats
        stats_layout = QHBoxLayout()
        self.detected_patterns = QLabel("Detected Trading Patterns: 5")
        self.detected_patterns.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.anomalous_trades = QLabel("Anomalous Trades: 1167")
        self.anomalous_trades.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        stats_layout.addWidget(self.detected_patterns)
        stats_layout.addWidget(self.anomalous_trades)
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        # Pattern Analysis Table
        pattern_label = QLabel("Trading Patterns Analysis:")
        pattern_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        left_layout.addWidget(pattern_label)
        
        self.pattern_table = self.create_pattern_table()
        left_layout.addWidget(self.pattern_table)
        
        # Model Performance Section
        performance_header = QLabel("📊 MODEL PERFORMANCE")
        performance_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        left_layout.addWidget(performance_header)
        
        # Model Accuracy Chart
        accuracy_label = QLabel("Model Prediction Accuracy Over Time")
        accuracy_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        left_layout.addWidget(accuracy_label)
        
        self.accuracy_chart = LineChartWidget(y_axis_position='left')
        left_layout.addWidget(self.accuracy_chart.get_canvas())
        
        # Model Performance Metrics Table
        metrics_label = QLabel("Performance Metrics:")
        metrics_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        left_layout.addWidget(metrics_label)
        
        self.metrics_table = self.create_metrics_table()
        left_layout.addWidget(self.metrics_table)
        
        # Right side - Recommendations and Impact Analysis
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Active Recommendations Section
        recommendations_header = QLabel("💡 ACTIVE RECOMMENDATIONS")
        recommendations_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(recommendations_header)
        
        self.recommendations_table = self.create_recommendations_table()
        right_layout.addWidget(self.recommendations_table)
        
        # Model Impact Analysis Section
        impact_header = QLabel("📈 MODEL IMPACT ANALYSIS")
        impact_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        right_layout.addWidget(impact_header)
        
        # Performance Comparison Chart
        comparison_label = QLabel("Model-Based vs. Manual Trading Performance")
        comparison_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        right_layout.addWidget(comparison_label)
        
        self.comparison_chart = LineChartWidget(y_axis_position='left')
        right_layout.addWidget(self.comparison_chart.get_canvas())
        
        # Impact Analysis Table
        impact_label = QLabel("Trading Performance Comparison:")
        impact_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        right_layout.addWidget(impact_label)
        
        self.impact_table = self.create_impact_table()
        right_layout.addWidget(self.impact_table)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
    def create_table_base(self, headers):
        """Create a base styled table widget"""
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
        return table
        
    def create_pattern_table(self):
        """Create pattern analysis table"""
        table = self.create_table_base([
            "Pattern", "Count", "Success Rate", "Avg Profit", "Avg Duration (min)"
        ])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        return table
        
    def create_metrics_table(self):
        """Create performance metrics table"""
        table = self.create_table_base([
            "Metric", "Last Week", "Last Month", "Overall"
        ])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        return table
        
    def create_recommendations_table(self):
        """Create recommendations table"""
        table = self.create_table_base([
            "Recommendation", "Confidence", "Expected Impact", "Status"
        ])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        return table
        
    def create_impact_table(self):
        """Create impact analysis table"""
        table = self.create_table_base([
            "Metric", "Model-Based", "Manual", "Difference"
        ])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        return table
        
    def load_sample_data(self):
        """Load sample data for all widgets"""
        # Pattern Analysis Data
        patterns_data = [
            ["pattern_0", "980", "42.96%", "$-0.57", "2.75"],
            ["pattern_1", "1", "100.00%", "$100,000.00", "nan"],
            ["pattern_2", "2", "50.00%", "$12.98", "993.9"],
            ["pattern_3", "161", "37.27%", "$58.63", "2.79"],
            ["pattern_4", "29", "37.93%", "$-10.43", "87.23"]
        ]
        self.populate_table(self.pattern_table, patterns_data)
        
        # Performance Metrics Data
        metrics_data = [
            ["Accuracy", "82.5%", "79.8%", "78.5%"],
            ["Precision", "0.85", "0.83", "0.82"],
            ["Recall", "0.79", "0.77", "0.75"],
            ["F1 Score", "0.82", "0.80", "0.78"],
            ["ROI", "+15.3%", "+12.8%", "+10.5%"]
        ]
        self.populate_table(self.metrics_table, metrics_data)
        
        # Recommendations Data
        recommendations_data = [
            ["Reduce position size for EURUSD", "85%", "Risk ↓ 15%", "Active"],
            ["Increase hedge ratio", "92%", "Risk ↓ 25%", "Pending"],
            ["Close GBPUSD positions", "78%", "Profit ↑ 5%", "Active"],
            ["Adjust stop loss levels", "88%", "Risk ↓ 10%", "Completed"],
            ["Open long position BTCUSD", "76%", "Profit ↑ 8%", "Pending"]
        ]
        self.populate_table(self.recommendations_table, recommendations_data)
        
        # Impact Analysis Data
        impact_data = [
            ["Win Rate", "78.5%", "65.2%", "+13.3%"],
            ["Avg Profit/Trade", "$125.45", "$98.32", "+$27.13"],
            ["Max Drawdown", "12.3%", "18.7%", "-6.4%"],
            ["Sharpe Ratio", "2.15", "1.82", "+0.33"],
            ["Total ROI", "+15.8%", "+10.2%", "+5.6%"]
        ]
        self.populate_table(self.impact_table, impact_data)
        
        # Generate chart data
        dates = []
        accuracy_values = []
        baseline_values = []
        model_performance = []
        manual_performance = []
        
        end_date = datetime.now()
        base_value = 10000
        model_value = base_value
        manual_value = base_value
        
        for i in range(30):
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Accuracy data
            accuracy = 65 + (i * 0.5) + random.uniform(-5, 5)
            accuracy = min(max(accuracy, 60), 95)
            accuracy_values.append(accuracy)
            baseline_values.append(70)
            
            # Performance data
            model_change = random.uniform(-0.02, 0.03)
            manual_change = random.uniform(-0.025, 0.025)
            model_value *= (1 + model_change)
            manual_value *= (1 + manual_change)
            model_performance.append(model_value)
            manual_performance.append(manual_value)
        
        dates.reverse()
        accuracy_values.reverse()
        baseline_values.reverse()
        model_performance.reverse()
        manual_performance.reverse()
        
        # Update charts
        self.accuracy_chart.update_data(
            dates,
            [accuracy_values, baseline_values],
            ['#4CAF50', '#666666']
        )
        
        self.comparison_chart.update_data(
            dates,
            [model_performance, manual_performance],
            ['#4CAF50', '#2196F3']
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
                        if pct > 0:
                            item.setForeground(Qt.green)
                        elif pct < 0:
                            item.setForeground(Qt.red)
                    except ValueError:
                        pass
                elif '$' in value:
                    try:
                        amount = float(value.replace('$', '').replace(',', ''))
                        if amount > 0:
                            item.setForeground(Qt.green)
                        elif amount < 0:
                            item.setForeground(Qt.red)
                    except ValueError:
                        pass
                elif value in ['Active', 'Completed', 'Pending']:
                    if value == 'Active':
                        item.setForeground(Qt.green)
                    elif value == 'Pending':
                        item.setForeground(Qt.yellow)
                    else:
                        item.setForeground(Qt.gray)
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30) 