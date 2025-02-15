from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
                               QFrame, QComboBox, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from widgets.line_chart import LineChartWidget
import random
from datetime import datetime, timedelta

class ProfitLossTab(QWidget):
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
        
        # Summary Metrics Display
        metrics_frame = QFrame()
        metrics_frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 5px; padding: 10px; }")
        metrics_layout = QHBoxLayout(metrics_frame)
        
        # Create metric displays
        metric_layouts = []
        
        # Total P&L
        total_pl_layout = self.create_metric_display("Total P&L", "$12,381.77")
        metric_layouts.append(total_pl_layout)
        
        # Win Rate
        win_rate_layout = self.create_metric_display("Win Rate", "78.5%")
        metric_layouts.append(win_rate_layout)
        
        # Average Trade
        avg_trade_layout = self.create_metric_display("Average Trade", "$25.83")
        metric_layouts.append(avg_trade_layout)
        
        # Profit Factor
        profit_factor_layout = self.create_metric_display("Profit Factor", "2.5")
        metric_layouts.append(profit_factor_layout)
        
        # Best Trade
        best_trade_layout = self.create_metric_display("Best Trade", "$1,234.56")
        metric_layouts.append(best_trade_layout)
        
        # Worst Trade
        worst_trade_layout = self.create_metric_display("Worst Trade", "-$567.89")
        metric_layouts.append(worst_trade_layout)
        
        # Add all metrics to the frame
        for layout in metric_layouts:
            metrics_layout.addLayout(layout)
        
        # Filters Section
        filters_frame = QFrame()
        filters_frame.setStyleSheet("QFrame { background-color: #2D2D2D; border-radius: 5px; padding: 10px; }")
        filters_layout = QHBoxLayout(filters_frame)
        
        # Time Period Filter
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last Week", "Last Month", "Last Quarter", "Last Year", "All Time"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 120px;
            }
        """)
        
        # Instrument Filter
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItems(["All Instruments", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD"])
        self.instrument_combo.setStyleSheet(self.period_combo.styleSheet())
        
        filters_layout.addWidget(QLabel("Period:"))
        filters_layout.addWidget(self.period_combo)
        filters_layout.addWidget(QLabel("Instrument:"))
        filters_layout.addWidget(self.instrument_combo)
        filters_layout.addStretch()
        
        top_layout.addWidget(metrics_frame)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(filters_frame)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - P&L Analysis
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # P&L Chart
        pnl_header = QLabel("Cumulative P&L")
        pnl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(pnl_header)
        
        self.pnl_chart = LineChartWidget(y_axis_position='left')
        left_layout.addWidget(self.pnl_chart.get_canvas())
        
        # Market Session Analysis
        session_header = QLabel("Market Session Analysis")
        session_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 15px;")
        left_layout.addWidget(session_header)
        
        self.session_table = self.create_table([
            "Session", "Total P&L", "Win Rate", "Avg Profit", "Avg Loss", "Net Trades", "Profit Factor"
        ])
        left_layout.addWidget(self.session_table)
        
        # Right side - Detailed Analysis
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Weekday Analysis
        weekday_header = QLabel("Weekday Analysis")
        weekday_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(weekday_header)
        
        self.weekday_table = self.create_table([
            "Day", "Total P&L", "Win Rate", "Avg Profit", "Avg Loss", "Net Trades", "Profit Factor"
        ])
        right_layout.addWidget(self.weekday_table)
        
        # Monthly Analysis
        monthly_header = QLabel("Monthly Analysis")
        monthly_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 15px;")
        right_layout.addWidget(monthly_header)
        
        self.monthly_table = self.create_table([
            "Month", "Total P&L", "Win Rate", "Avg Profit", "Avg Loss", "Net Trades", "Profit Factor"
        ])
        right_layout.addWidget(self.monthly_table)
        
        # Buy/Sell Analysis
        direction_header = QLabel("Buy/Sell Analysis")
        direction_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 15px;")
        right_layout.addWidget(direction_header)
        
        self.direction_table = self.create_table([
            "Direction", "Total P&L", "Win Rate", "Avg Profit", "Avg Loss", "Net Trades", "Profit Factor"
        ])
        right_layout.addWidget(self.direction_table)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
        
    def create_metric_display(self, label_text, initial_value):
        """Create a metric display with label and value"""
        layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        value = QLabel(initial_value)
        value.setStyleSheet("color: #4CAF50; font-size: 24px; font-weight: bold;")
        layout.addWidget(label)
        layout.addWidget(value)
        return layout
        
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
        # Market Session Analysis Data
        session_data = [
            ["Asian", "$3,245.50", "75.5%", "$450.25", "-$225.75", "125", "2.1"],
            ["European", "$5,678.25", "82.3%", "$525.50", "-$275.25", "245", "2.8"],
            ["New York", "$4,890.75", "79.8%", "$485.75", "-$245.50", "198", "2.5"],
            ["Overlap", "$2,567.25", "73.5%", "$425.25", "-$215.75", "156", "1.9"]
        ]
        self.populate_table(self.session_table, session_data)
        
        # Weekday Analysis Data
        weekday_data = [
            ["Monday", "$2,345.75", "77.5%", "$445.25", "-$225.50", "145", "2.2"],
            ["Tuesday", "$3,567.50", "81.2%", "$475.50", "-$235.75", "167", "2.6"],
            ["Wednesday", "$2,890.25", "76.8%", "$435.75", "-$228.50", "156", "2.1"],
            ["Thursday", "$2,765.75", "79.5%", "$455.25", "-$232.75", "149", "2.3"],
            ["Friday", "$2,812.50", "75.8%", "$425.50", "-$245.25", "157", "2.0"]
        ]
        self.populate_table(self.weekday_table, weekday_data)
        
        # Monthly Analysis Data
        monthly_data = [
            ["January", "$4,567.75", "78.5%", "$465.25", "-$235.50", "245", "2.4"],
            ["February", "$3,890.50", "76.2%", "$445.50", "-$245.75", "198", "2.1"],
            ["March", "$5,234.25", "82.8%", "$495.75", "-$228.50", "267", "2.9"],
            ["April", "$4,765.75", "79.5%", "$475.25", "-$232.75", "234", "2.5"],
            ["May", "$3,912.50", "77.8%", "$455.50", "-$242.25", "212", "2.2"]
        ]
        self.populate_table(self.monthly_table, monthly_data)
        
        # Buy/Sell Analysis Data
        direction_data = [
            ["Buy", "$8,567.75", "81.5%", "$485.25", "-$235.50", "425", "2.7"],
            ["Sell", "$7,813.50", "75.5%", "$445.50", "-$255.75", "349", "2.3"]
        ]
        self.populate_table(self.direction_table, direction_data)
        
        # Generate P&L chart data
        dates = []
        cumulative_pnl = []
        daily_pnl = []
        
        end_date = datetime.now()
        current_pnl = 0
        
        for i in range(180):  # 6 months of daily data
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Generate realistic daily P&L
            daily_change = random.uniform(-500, 750)
            current_pnl += daily_change
            
            cumulative_pnl.append(current_pnl)
            daily_pnl.append(daily_change)
        
        dates.reverse()
        cumulative_pnl.reverse()
        daily_pnl.reverse()
        
        # Update P&L chart without bar value labels
        self.pnl_chart.update_data(
            dates,
            [cumulative_pnl],
            ['#4CAF50'],
            bar_data=daily_pnl,
            bar_colors=['#2196F3' if x >= 0 else '#F44336' for x in daily_pnl],
            show_bar_labels=False  # Add this parameter to disable bar labels
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
                            item.setForeground(QColor("#4CAF50"))  # Green for high win rate
                        elif pct >= 70:
                            item.setForeground(QColor("#FFC107"))  # Yellow for medium win rate
                        else:
                            item.setForeground(QColor("#F44336"))  # Red for low win rate
                    except ValueError:
                        pass
                elif '$' in value:
                    try:
                        amount = float(value.replace('$', '').replace(',', ''))
                        if '-' in value:
                            item.setForeground(QColor("#F44336"))  # Red for losses
                        else:
                            item.setForeground(QColor("#4CAF50"))  # Green for profits
                    except ValueError:
                        pass
                elif col == 6:  # Profit Factor column
                    try:
                        pf = float(value)
                        if pf >= 2.5:
                            item.setForeground(QColor("#4CAF50"))  # Green for high profit factor
                        elif pf >= 2.0:
                            item.setForeground(QColor("#FFC107"))  # Yellow for medium profit factor
                        else:
                            item.setForeground(QColor("#F44336"))  # Red for low profit factor
                    except ValueError:
                        pass
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30)
            
    def update_metrics(self, metrics):
        """Update profit & loss metrics with new values
        
        Args:
            metrics (dict): Dictionary containing P&L metrics
                - profit (float): Total profit
                - loss (float): Total loss
                - swaps (float): Total swaps
                - dividends (float): Total dividends
                - commissions (float): Total commissions
                - year_total (float): Year-to-date total
                - total (float): All-time total
        """
        # Find all metric value labels
        metric_values = {}
        for label in self.findChildren(QLabel):
            if label.text() in ["Total P&L", "Win Rate", "Average Trade", "Profit Factor", "Best Trade", "Worst Trade"]:
                # Store the value label (next sibling)
                value_label = label.parent().findChild(QLabel, "", options=Qt.FindChildOption.FindChildrenRecursively)
                if value_label and value_label != label:
                    metric_values[label.text()] = value_label

        # Update total P&L
        if 'total' in metrics and "Total P&L" in metric_values:
            metric_values["Total P&L"].setText(f"${metrics['total']:,.2f}")
        
        # Calculate and update win rate
        if all(key in metrics for key in ['profit', 'loss']) and "Win Rate" in metric_values:
            total_trades = abs(metrics['profit']) + abs(metrics['loss'])
            if total_trades > 0:
                win_rate = (metrics['profit'] / total_trades) * 100
                metric_values["Win Rate"].setText(f"{win_rate:.1f}%")
        
        # Calculate and update average trade
        if all(key in metrics for key in ['profit', 'loss', 'swaps', 'dividends', 'commissions']) and "Average Trade" in metric_values:
            total_trades = abs(metrics['profit']) + abs(metrics['loss'])
            if total_trades > 0:
                avg_trade = (metrics['profit'] + metrics['loss'] + metrics['swaps'] + 
                           metrics['dividends'] - metrics['commissions']) / total_trades
                metric_values["Average Trade"].setText(f"${avg_trade:.2f}")
        
        # Calculate and update profit factor
        if all(key in metrics for key in ['profit', 'loss']) and "Profit Factor" in metric_values:
            if abs(metrics['loss']) > 0:
                profit_factor = abs(metrics['profit']) / abs(metrics['loss'])
                metric_values["Profit Factor"].setText(f"{profit_factor:.2f}")
        
        # Update best and worst trades
        if 'profit' in metrics and "Best Trade" in metric_values:
            best_trade = metrics.get('best_trade', metrics['profit'])
            metric_values["Best Trade"].setText(f"${best_trade:.2f}")
        
        if 'loss' in metrics and "Worst Trade" in metric_values:
            worst_trade = metrics.get('worst_trade', metrics['loss'])
            metric_values["Worst Trade"].setText(f"${worst_trade:.2f}") 