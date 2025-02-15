from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

class RisksTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Load UI
        loader = QUiLoader()
        ui_file = QFile("ui/risks_tab.ui")
        ui_file.open(QFile.ReadOnly)
        self.tab_content = loader.load(ui_file)
        ui_file.close()
        
        # Add the loaded UI to this widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_content)
        
    def update_metrics(self, metrics):
        """Update the risk metrics
        
        Args:
            metrics (dict): Dictionary containing the metric values
        """
        if 'sharp_ratio' in metrics:
            self.tab_content.progress_sharp_ratio.setValue(metrics['sharp_ratio'])
            
        if 'max_drawdown' in metrics:
            self.tab_content.progress_max_drawdown.setValue(metrics['max_drawdown'])
            
        if 'profit_factor' in metrics:
            self.tab_content.progress_profit_factor.setValue(metrics['profit_factor'])
            
        if 'deposit_load' in metrics:
            self.tab_content.progress_deposit_load.setValue(metrics['deposit_load'])
            
        if 'recovery_factor' in metrics:
            self.tab_content.progress_recovery_factor.setValue(metrics['recovery_factor'])
            
        if 'trades_per_week' in metrics:
            self.tab_content.progress_trades_per_week.setValue(metrics['trades_per_week']) 