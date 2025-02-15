import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from tabs.summary_tab import SummaryTab
from tabs.risks_tab import RisksTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_ui()
        
    def setup_ui(self):
        # Load UI
        loader = QUiLoader()
        ui_file = QFile("main.ui")
        ui_file.open(QFile.ReadOnly)
        self.central_widget = loader.load(ui_file)
        ui_file.close()
        
        # Set central widget
        self.setCentralWidget(self.central_widget)
        
        # Store reference to tab widget
        self.tab_widget = self.central_widget.findChild(QTabWidget, "tabWidget")
        
        # Setup tabs
        self.setup_tabs()
        
    def setup_tabs(self):
        """Setup all tab widgets"""
        # Remove placeholder tabs
        while self.tab_widget.count():
            self.tab_widget.removeTab(0)
            
        # Summary tab
        summary_tab = SummaryTab()
        self.tab_widget.addTab(summary_tab, "Summary")
        
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
            'average_hold_time': 6  # Added average hold time in hours
        })
        
        # Risks tab
        risks_tab = RisksTab()
        self.tab_widget.addTab(risks_tab, "Risks")
        
        # Initialize risks data
        risks_tab.update_metrics({
            'sharp_ratio': 0,
            'max_drawdown': 10,
            'profit_factor': 2,
            'deposit_load': 92,
            'recovery_factor': 2,
            'trades_per_week': 2
        })

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
