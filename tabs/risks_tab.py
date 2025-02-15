from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QSplitter)
from PySide6.QtCore import Qt
from widgets.line_chart import LineChartWidget
import random
from datetime import datetime, timedelta

class RisksTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def update_metrics(self, metrics):
        """Update risk metrics with new values
        
        Args:
            metrics (dict): Dictionary containing risk metrics
                - sharp_ratio (float): Sharpe ratio
                - max_drawdown (float): Maximum drawdown percentage
                - profit_factor (float): Profit factor
                - deposit_load (float): Deposit load percentage
                - recovery_factor (float): Recovery factor
                - trades_per_week (int): Average trades per week
        """
        # Update current drawdown stats
        if 'max_drawdown' in metrics:
            self.max_dd.setText(f"Max Drawdown: -{metrics['max_drawdown']:.2f}%")
            
        # Update risk ratios
        ratios_data = [
            ["Sharpe Ratio", 
             f"{metrics.get('sharp_ratio', 0):.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.1:.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.2:.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.15:.2f}"],
            ["Sortino Ratio", 
             f"{metrics.get('sharp_ratio', 0) * 1.2:.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.3:.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.4:.2f}",
             f"{metrics.get('sharp_ratio', 0) * 1.35:.2f}"],
            ["Calmar Ratio",
             f"{metrics.get('recovery_factor', 0):.2f}",
             f"{metrics.get('recovery_factor', 0) * 1.1:.2f}",
             f"{metrics.get('recovery_factor', 0) * 1.2:.2f}",
             f"{metrics.get('recovery_factor', 0) * 1.15:.2f}"],
            ["Information Ratio",
             f"{metrics.get('profit_factor', 0) / 2:.2f}",
             f"{metrics.get('profit_factor', 0) / 1.8:.2f}",
             f"{metrics.get('profit_factor', 0) / 1.6:.2f}",
             f"{metrics.get('profit_factor', 0) / 1.7:.2f}"],
            ["Risk/Reward Ratio",
             f"{2 / metrics.get('profit_factor', 1):.2f}",
             f"{1.8 / metrics.get('profit_factor', 1):.2f}",
             f"{1.6 / metrics.get('profit_factor', 1):.2f}",
             f"{1.7 / metrics.get('profit_factor', 1):.2f}"]
        ]
        self.populate_table(self.ratios_table, ratios_data)
        
        # Update risk exposure stats
        if 'deposit_load' in metrics:
            self.margin_used.setText(f"Margin Used: {metrics['deposit_load']:.2f}%")
        if 'trades_per_week' in metrics:
            risk_per_trade = metrics['max_drawdown'] / (metrics['trades_per_week'] * 4)  # Monthly risk
            self.risk_per_trade.setText(f"Risk per Trade: {risk_per_trade:.2f}%")
            
        # Update position risk data based on current metrics
        position_data = [
            ["EURUSD", "1.25 lots", f"${metrics['max_drawdown'] * 12.5:.0f}", f"{metrics['deposit_load'] / 40:.1f}%", "50 pips"],
            ["GBPUSD", "0.75 lots", f"${metrics['max_drawdown'] * 7.5:.0f}", f"{metrics['deposit_load'] / 67:.1f}%", "45 pips"],
            ["USDJPY", "1.00 lots", f"${metrics['max_drawdown'] * 10.0:.0f}", f"{metrics['deposit_load'] / 50:.1f}%", "35 pips"],
            ["BTCUSD", "0.50 lots", f"${metrics['max_drawdown'] * 5.0:.0f}", f"{metrics['deposit_load'] / 100:.1f}%", "$500"],
            ["XAUUSD", "0.25 lots", f"${metrics['max_drawdown'] * 2.5:.0f}", f"{metrics['deposit_load'] / 200:.1f}%", "$5"]
        ]
        self.populate_table(self.position_risk_table, position_data)
        
        # Update VaR calculations based on metrics
        daily_var = metrics['max_drawdown'] / 20  # Approximate daily VaR
        var_data = [
            ["99% Confidence", f"${daily_var * 2.33:.0f}", f"${daily_var * 2.33 * 5:.0f}", f"${daily_var * 2.33 * 20:.0f}"],
            ["95% Confidence", f"${daily_var * 1.65:.0f}", f"${daily_var * 1.65 * 5:.0f}", f"${daily_var * 1.65 * 20:.0f}"],
            ["90% Confidence", f"${daily_var * 1.28:.0f}", f"${daily_var * 1.28 * 5:.0f}", f"${daily_var * 1.28 * 20:.0f}"]
        ]
        self.populate_table(self.var_table, var_data)
        
        # Generate new drawdown chart data based on max_drawdown
        dates = []
        drawdown_values = []
        underwater_values = []
        
        end_date = datetime.now()
        current_dd = 0
        max_dd = 0
        
        for i in range(180):  # 6 months of daily data
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Generate realistic drawdown pattern based on max_drawdown
            if random.random() < 0.4:
                current_dd -= random.uniform(0, metrics['max_drawdown'] / 10)
            else:
                current_dd += random.uniform(0, metrics['max_drawdown'] / 15)
                
            # Keep drawdown negative and limit to max_drawdown
            current_dd = min(0, max(current_dd, -metrics['max_drawdown']))
            max_dd = min(max_dd, current_dd)
            
            drawdown_values.append(current_dd)
            underwater_values.append(max_dd)
        
        dates.reverse()
        drawdown_values.reverse()
        underwater_values.reverse()
        
        # Update current drawdown value
        self.current_dd.setText(f"Current Drawdown: {drawdown_values[-1]:.2f}%")
        
        # Update drawdown chart
        self.drawdown_chart.update_data(
            dates,
            [drawdown_values, underwater_values],
            ['#FF4444', '#666666']
        )
        
        # Update drawdown history based on metrics
        drawdown_data = [
            ["Current", f"{drawdown_values[-1]:.2f}%", "Ongoing", "-", "Market Conditions"],
            ["Last Month", f"-{metrics['max_drawdown'] * 0.8:.2f}%", f"{int(metrics['trades_per_week'] * 2)} days", f"{int(metrics['trades_per_week'] * 3)} days", "Technical Pullback"],
            ["2 Months Ago", f"-{metrics['max_drawdown'] * 0.6:.2f}%", f"{int(metrics['trades_per_week'] * 1.5)} days", f"{int(metrics['trades_per_week'] * 2)} days", "News Impact"],
            ["3 Months Ago", f"-{metrics['max_drawdown'] * 0.4:.2f}%", f"{int(metrics['trades_per_week'])} days", f"{int(metrics['trades_per_week'] * 1.5)} days", "Market Volatility"],
            ["6 Months Ago", f"-{metrics['max_drawdown']:.2f}%", f"{int(metrics['trades_per_week'] * 3)} days", f"{int(metrics['trades_per_week'] * 4)} days", "Major Market Event"]
        ]
        self.populate_table(self.drawdown_table, drawdown_data)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Create horizontal splitter for main sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Drawdown Analysis and Risk Metrics
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Drawdown Analysis Section
        drawdown_header = QLabel("📉 DRAWDOWN ANALYSIS")
        drawdown_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(drawdown_header)
        
        # Current Drawdown Stats
        stats_layout = QHBoxLayout()
        self.current_dd = QLabel("Current Drawdown: -3.45%")
        self.current_dd.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.max_dd = QLabel("Max Drawdown: -15.67%")
        self.max_dd.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.recovery_time = QLabel("Avg Recovery Time: 12.5 days")
        self.recovery_time.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        stats_layout.addWidget(self.current_dd)
        stats_layout.addWidget(self.max_dd)
        stats_layout.addWidget(self.recovery_time)
        stats_layout.addStretch()
        left_layout.addLayout(stats_layout)
        
        # Drawdown History Chart
        drawdown_label = QLabel("Historical Drawdowns:")
        drawdown_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        left_layout.addWidget(drawdown_label)
        
        self.drawdown_chart = LineChartWidget(y_axis_position='left')
        left_layout.addWidget(self.drawdown_chart.get_canvas())
        
        # Drawdown Details Table
        dd_details_label = QLabel("Major Drawdown Periods:")
        dd_details_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        left_layout.addWidget(dd_details_label)
        
        self.drawdown_table = self.create_table([
            "Period", "Max DD", "Duration", "Recovery Time", "Cause"
        ])
        left_layout.addWidget(self.drawdown_table)
        
        # Right side - Risk Metrics and Exposure Analysis
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Risk Ratios Section
        ratios_header = QLabel("📊 RISK RATIOS")
        ratios_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        right_layout.addWidget(ratios_header)
        
        # Risk Ratios Table
        self.ratios_table = self.create_table([
            "Ratio", "Daily", "Weekly", "Monthly", "Overall"
        ])
        right_layout.addWidget(self.ratios_table)
        
        # Risk Exposure Section
        exposure_header = QLabel("⚠️ RISK EXPOSURE")
        exposure_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        right_layout.addWidget(exposure_header)
        
        # Risk Exposure Stats
        exposure_layout = QHBoxLayout()
        self.margin_used = QLabel("Margin Used: 45.67%")
        self.margin_used.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        self.risk_per_trade = QLabel("Risk per Trade: 1.23%")
        self.risk_per_trade.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        exposure_layout.addWidget(self.margin_used)
        exposure_layout.addWidget(self.risk_per_trade)
        exposure_layout.addStretch()
        right_layout.addLayout(exposure_layout)
        
        # Position Risk Table
        position_label = QLabel("Position Risk Analysis:")
        position_label.setStyleSheet("color: #FFFFFF; font-size: 14px; margin-top: 15px;")
        right_layout.addWidget(position_label)
        
        self.position_risk_table = self.create_table([
            "Symbol", "Position Size", "Risk Amount", "Risk %", "Stop Distance"
        ])
        right_layout.addWidget(self.position_risk_table)
        
        # Value at Risk Section
        var_header = QLabel("📉 VALUE AT RISK (VaR)")
        var_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; margin-top: 20px;")
        right_layout.addWidget(var_header)
        
        # VaR Table
        self.var_table = self.create_table([
            "Confidence Level", "Daily VaR", "Weekly VaR", "Monthly VaR"
        ])
        right_layout.addWidget(self.var_table)
        
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
        
    def load_sample_data(self):
        """Load sample data for all widgets"""
        # Drawdown Details Data
        drawdown_data = [
            ["Jan 2024", "-15.67%", "18 days", "25 days", "Market Crash"],
            ["Nov 2023", "-8.92%", "12 days", "15 days", "Interest Rate Hike"],
            ["Sep 2023", "-6.45%", "8 days", "10 days", "Earnings Miss"],
            ["Jul 2023", "-5.78%", "5 days", "7 days", "Political Event"],
            ["May 2023", "-4.23%", "4 days", "5 days", "Technical Selloff"]
        ]
        self.populate_table(self.drawdown_table, drawdown_data)
        
        # Risk Ratios Data
        ratios_data = [
            ["Sharpe Ratio", "1.85", "2.12", "2.45", "2.15"],
            ["Sortino Ratio", "2.34", "2.67", "2.89", "2.56"],
            ["Calmar Ratio", "1.23", "1.45", "1.67", "1.43"],
            ["Information Ratio", "0.78", "0.92", "1.15", "0.95"],
            ["Treynor Ratio", "0.45", "0.56", "0.67", "0.54"]
        ]
        self.populate_table(self.ratios_table, ratios_data)
        
        # Position Risk Data
        position_data = [
            ["EURUSD", "1.25 lots", "$1,250", "2.5%", "50 pips"],
            ["GBPUSD", "0.75 lots", "$750", "1.5%", "45 pips"],
            ["USDJPY", "1.00 lots", "$1,000", "2.0%", "35 pips"],
            ["BTCUSD", "0.50 lots", "$500", "1.0%", "$500"],
            ["XAUUSD", "0.25 lots", "$250", "0.5%", "$5"]
        ]
        self.populate_table(self.position_risk_table, position_data)
        
        # Value at Risk Data
        var_data = [
            ["99% Confidence", "$2,345", "$4,567", "$7,890"],
            ["95% Confidence", "$1,234", "$2,345", "$4,567"],
            ["90% Confidence", "$987", "$1,876", "$3,456"]
        ]
        self.populate_table(self.var_table, var_data)
        
        # Generate drawdown chart data
        dates = []
        drawdown_values = []
        underwater_values = []
        
        end_date = datetime.now()
        current_dd = 0
        max_dd = 0
        
        for i in range(180):  # 6 months of daily data
            date = end_date - timedelta(days=i)
            dates.append(date)
            
            # Generate realistic drawdown pattern
            if random.random() < 0.4:  # 40% chance of drawdown
                current_dd -= random.uniform(0.1, 0.5)
            else:
                current_dd += random.uniform(0, 0.3)
                
            # Keep drawdown negative and limit recovery
            current_dd = min(0, max(current_dd, -20))
            max_dd = min(max_dd, current_dd)
            
            drawdown_values.append(current_dd)
            underwater_values.append(max_dd)
        
        dates.reverse()
        drawdown_values.reverse()
        underwater_values.reverse()
        
        # Update drawdown chart
        self.drawdown_chart.update_data(
            dates,
            [drawdown_values, underwater_values],
            ['#FF4444', '#666666']  # Red for drawdown, gray for underwater equity
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
                        pct = float(value.replace('%', '').replace('-', ''))
                        if '-' in value:
                            item.setForeground(Qt.red)
                        elif pct > 2.0:
                            item.setForeground(Qt.red)  # High risk
                        elif pct > 1.0:
                            item.setForeground(Qt.yellow)  # Medium risk
                        else:
                            item.setForeground(Qt.green)  # Low risk
                    except ValueError:
                        pass
                elif any(ratio in value for ratio in ['Sharpe', 'Sortino', 'Calmar', 'Information', 'Treynor']):
                    try:
                        ratio = float(value)
                        if ratio > 2.0:
                            item.setForeground(Qt.green)  # Excellent
                        elif ratio > 1.0:
                            item.setForeground(Qt.yellow)  # Good
                        else:
                            item.setForeground(Qt.red)  # Poor
                    except ValueError:
                        pass
                
                table.setItem(row, col, item)
            table.setRowHeight(row, 30) 