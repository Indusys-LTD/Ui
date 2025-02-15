from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

class CustomTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the table's default properties"""
        # Make the table adjust to the window size
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
    def set_data(self, data, headers=None):
        """Set the table data
        
        Args:
            data (list): List of rows, where each row is a list of values
            headers (list, optional): List of column headers
        """
        # Set dimensions
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]) if data else 0)
        
        # Set headers if provided
        if headers:
            self.setHorizontalHeaderLabels(headers)
            
        # Populate data
        for row_idx, row in enumerate(data):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.setItem(row_idx, col_idx, item)
                
    def get_selected_data(self):
        """Get the currently selected cells' data
        
        Returns:
            list: List of selected cell values
        """
        return [item.text() for item in self.selectedItems()] 