import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from tabs.summary_tab import SummaryTab
from tabs.risks_tab import RisksTab
from tabs.profit_loss_tab import ProfitLossTab
from tabs.long_short_tab import LongShortTab
from tabs.currency_tab import CurrencyTab
from tabs.overview_tab import OverviewTab
from tabs.sequence_tab import SequenceTab
from tabs.ai_tab import AITab
from tabs.database_tab import DatabaseTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        
    def setup_ui(self):
        # Create central widget and main layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Setup tabs
        self.setup_tabs()
        
    def setup_tabs(self):
        """Setup all tab widgets"""
        # Overview tab
        overview_tab = OverviewTab()
        self.central_widget.addTab(overview_tab, "Overview")
            
        # Summary tab
        summary_tab = SummaryTab()
        self.central_widget.addTab(summary_tab, "Summary")
        
        # Initialize summary data
        summary_tab.update_metrics({
            # Financial metrics
            'gross_profit': 22.60,
            'gross_loss': 10.3,
            'swaps': -12.77,
            'dividends': 0.00,
            'commissions': 0.00,
            'balance': 112381.77,
            'equity': 112309.94,
            
            # Progress bar metrics
            'sharp_ratio': 0.65,
            'max_drawdown': 10,
            'profit_factor': 2.5,
            'deposit_load': 92.5,
            'recovery_factor': 2.49,
            'trades_per_week': 2,
            'average_hold_time': 6
        })
        
        # Sequence tab
        sequence_tab = SequenceTab()
        self.central_widget.addTab(sequence_tab, "Sequence")
        
        # AI tab
        ai_tab = AITab()
        self.central_widget.addTab(ai_tab, "AI")
        
        # Profit & Loss tab
        profit_loss_tab = ProfitLossTab()
        self.central_widget.addTab(profit_loss_tab, "Profit & Loss")
        
        # Initialize profit & loss data
        profit_loss_tab.update_metrics({
            'profit': 22691.04,
            'loss': 10309.27,
            'swaps': -12.77,
            'dividends': 0.00,
            'commissions': 0.00,
            'year_total': 12.38,
            'total': 12.38
        })
        
        # Long & Short tab
        long_short_tab = LongShortTab()
        self.central_widget.addTab(long_short_tab, "Long & Short")
        
        # Initialize long & short data
        long_short_tab.update_metrics({
            'long_count': 325,
            'long_percent': 58.77,
            'short_count': 228,
            'short_percent': 41.23,
            'netto_pl': 12381.77,
            'commissions': 0.00,
            'avg_pl': 25.83,
            'avg_profit': 47.08,
            'avg_pl_percent': 0.0254,
            'avg_profit_percent': 0.0459,
            'trades': 553,
            'win_trades': 460,
            'win_trades_percent': 83.18
        })
        
        # Currency tab
        currency_tab = CurrencyTab()
        self.central_widget.addTab(currency_tab, "Currency")
        
        # Initialize currency data
        currency_tab.update_metrics({
            'total_value': 12381.77,
            'profit_factor': 2.20,
            'netto_profit': 12381.77,
            'fees': 0.00
        })
        
        # Risks tab
        risks_tab = RisksTab()
        self.central_widget.addTab(risks_tab, "Risks")
        
        # Initialize risks data
        risks_tab.update_metrics({
            'sharp_ratio': 0,
            'max_drawdown': 10,
            'profit_factor': 2,
            'deposit_load': 92,
            'recovery_factor': 2,
            'trades_per_week': 2
        })
        
        # Database tab
        database_tab = DatabaseTab()
        self.central_widget.addTab(database_tab, "Database")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
