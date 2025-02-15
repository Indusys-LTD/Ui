from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                              QPushButton, QProgressBar)
from PySide6.QtCore import Qt
from widgets import PieChartWidget, LineChartWidget

class CurrencyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create top section
        top_layout = QHBoxLayout()
        
        # Total value
        self.total_value = QLabel("12,381.77")
        self.total_value.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px;")
        top_layout.addWidget(self.total_value)
        
        # Currency label (EURUSD)
        self.currency_label = QLabel("EURUSD")
        self.currency_label.setStyleSheet("color: #AAAAAA;")
        top_layout.addWidget(self.currency_label)
        
        top_layout.addStretch()
        
        # View toggle buttons
        self.button_money = QPushButton("Money")
        self.button_deals = QPushButton("Deals")
        
        for button in [self.button_money, self.button_deals]:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton[active="true"] {
                    background-color: #2196F3;
                }
            """)
            top_layout.addWidget(button)
            
        layout.addLayout(top_layout)
        
        # Main chart
        self.main_chart = LineChartWidget(width=16, height=4)
        self.main_chart.figure.patch.set_facecolor('#1E1E1E')
        self.main_chart.ax.set_facecolor('#1E1E1E')
        layout.addWidget(self.main_chart.get_canvas())
        
        # Create bottom section
        bottom_layout = QVBoxLayout()
        
        # Pie charts row
        charts_layout = QHBoxLayout()
        
        # Setup pie charts with equal sizes
        chart_width = 5
        chart_height = 3
        
        # Currency distribution pie chart
        self.currency_pie = PieChartWidget(width=chart_width, height=chart_height)
        charts_layout.addWidget(self.currency_pie.get_canvas())
        
        # EURUSD distribution pie chart
        self.eurusd_pie = PieChartWidget(width=chart_width, height=chart_height)
        charts_layout.addWidget(self.eurusd_pie.get_canvas())
        
        # Trading distribution pie chart
        self.trading_pie = PieChartWidget(width=chart_width, height=chart_height)
        charts_layout.addWidget(self.trading_pie.get_canvas())
        
        bottom_layout.addLayout(charts_layout)
        
        # Progress bars section
        bars_layout = QVBoxLayout()
        bars_layout.setSpacing(10)
        
        # Create progress bars
        self.progress_bars = {}
        metrics_data = [
            ('profit_factor', 'Profit Factor by Symbols', 'EURUSD', '2.20', 0, 3),
            ('netto_profit', 'Netto Profit by Symbols', 'EURUSD', '12,381.77', -20000, 20000),
            ('fees', 'Fees by Symbols', 'EURUSD', '0.00', 0, 100)
        ]
        
        for key, label, symbol, value, min_val, max_val in metrics_data:
            # Create container for each metric
            container = QHBoxLayout()
            
            # Label
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #AAAAAA;")
            container.addWidget(label_widget)
            
            # Symbol
            symbol_widget = QLabel(symbol)
            symbol_widget.setStyleSheet("color: #FFFFFF;")
            container.addWidget(symbol_widget)
            
            # Progress bar
            progress = QProgressBar()
            progress.setStyleSheet("""
                QProgressBar {
                    background-color: #2D2D2D;
                    border: none;
                    border-radius: 2px;
                    text-align: right;
                    padding-right: 5px;
                    height: 20px;
                    color: #FFFFFF;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 2px;
                }
            """)
            progress.setMinimum(min_val)
            progress.setMaximum(max_val)
            progress.setTextVisible(False)
            container.addWidget(progress)
            
            # Value
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: #FFFFFF; font-weight: bold;")
            value_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            container.addWidget(value_widget)
            
            # Store references
            self.progress_bars[key] = (progress, value_widget)
            
            # Add to layout
            bars_layout.addLayout(container)
        
        bottom_layout.addLayout(bars_layout)
        layout.addLayout(bottom_layout)
        
        # Configure chart styles
        for chart in [self.main_chart, self.currency_pie, self.eurusd_pie, self.trading_pie]:
            chart.figure.patch.set_facecolor('#1E1E1E')
            chart.ax.set_facecolor('#1E1E1E')
            chart.ax.tick_params(colors='#FFFFFF', which='both')
            for spine in chart.ax.spines.values():
                spine.set_color('#2D2D2D')
            chart.figure.set_constrained_layout(True)
        
        # Set initial button states
        self.button_money.setProperty("active", True)
        self.button_deals.setProperty("active", False)
        
        # Connect button signals
        self.button_money.clicked.connect(self.show_money_view)
        self.button_deals.clicked.connect(self.show_deals_view)
        
        # Initial data
        self.update_chart_data()
        
    def update_metrics(self, metrics):
        """Update all metrics
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        if 'total_value' in metrics:
            self.total_value.setText(f"{metrics['total_value']:,.2f}")
            
        # Update progress bars
        progress_mappings = {
            'profit_factor': ('{:.2f}', True),
            'netto_profit': ('{:,.2f}', True),
            'fees': ('{:.2f}', True)
        }
        
        for metric_key, (format_str, show_value) in progress_mappings.items():
            if metric_key in metrics and metric_key in self.progress_bars:
                progress_bar, value_label = self.progress_bars[metric_key]
                value = metrics[metric_key]
                
                # Update progress bar
                if isinstance(value, (int, float)):
                    progress_bar.setValue(int(value))
                
                # Update value label
                if show_value:
                    try:
                        formatted_value = format_str.format(value)
                        value_label.setText(formatted_value)
                    except (ValueError, TypeError):
                        value_label.setText(str(value))
                        
    def update_chart_data(self, view_type='money'):
        """Update all charts
        
        Args:
            view_type (str): Type of view to show ('money' or 'deals')
        """
        if view_type == 'money':
            # Update main chart
            dates = ['2025.02.10', '2025.02.11', '2025.02.11', '2025.02.12', '2025.02.13', '2025.02.14']
            values = [0, 2000, 6000, 6000, 12000, 12381.77]
            
            self.main_chart.update_data(
                x_data=dates,
                y_data=[values],
                colors=['#2196F3']  # Blue line
            )
            
            # Update currency distribution pie
            self.currency_pie.update_data(
                sizes=[553],
                labels=['Currency\n553'],
                colors=['#2196F3']
            )
            
            # Update EURUSD distribution pie
            self.eurusd_pie.update_data(
                sizes=[553],
                labels=['EURUSD\n553 (100%)'],
                colors=['#2196F3']
            )
            
            # Update trading distribution pie
            self.trading_pie.update_data(
                sizes=[532, 21, 0],
                labels=['Trading Robots\n532', 'Manual Trading\n21', 'Trading Signals\n0'],
                colors=['#9C27B0', '#2196F3', '#FF9800']
            )
            
        else:  # deals view
            # Update main chart with deals data
            dates = ['2025.02.10', '2025.02.11', '2025.02.11', '2025.02.12', '2025.02.13', '2025.02.14']
            deals = [10, 15, 20, 18, 25, 30]
            
            self.main_chart.update_data(
                x_data=dates,
                y_data=[deals],
                colors=['#4CAF50']  # Green line
            )
            
        # Update text colors for all charts
        for chart in [self.main_chart, self.currency_pie, self.eurusd_pie, self.trading_pie]:
            for text in chart.ax.get_xticklabels() + chart.ax.get_yticklabels():
                text.set_color('#FFFFFF')
                text.set_fontsize(9)
            chart.canvas.draw()
            
    def show_money_view(self):
        """Switch to money view"""
        self.button_money.setProperty("active", True)
        self.button_deals.setProperty("active", False)
        self.button_money.style().unpolish(self.button_money)
        self.button_money.style().polish(self.button_money)
        self.button_deals.style().unpolish(self.button_deals)
        self.button_deals.style().polish(self.button_deals)
        self.update_chart_data('money')
        
    def show_deals_view(self):
        """Switch to deals view"""
        self.button_money.setProperty("active", False)
        self.button_deals.setProperty("active", True)
        self.button_money.style().unpolish(self.button_money)
        self.button_money.style().polish(self.button_money)
        self.button_deals.style().unpolish(self.button_deals)
        self.button_deals.style().polish(self.button_deals)
        self.update_chart_data('deals') 