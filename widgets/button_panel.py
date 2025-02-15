from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

class ButtonPanel(QWidget):
    def __init__(self, orientation='horizontal', parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout() if orientation == 'horizontal' else QVBoxLayout()
        self.setLayout(self.layout)
        self.buttons = {}
        
    def add_button(self, name, text, callback=None):
        """Add a button to the panel
        
        Args:
            name (str): Internal name for the button
            text (str): Button display text
            callback (callable, optional): Function to call when button is clicked
        """
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        self.buttons[name] = button
        self.layout.addWidget(button)
        return button
        
    def get_button(self, name):
        """Get a button by its name
        
        Args:
            name (str): Button's internal name
            
        Returns:
            QPushButton: The requested button
        """
        return self.buttons.get(name)
        
    def enable_button(self, name, enabled=True):
        """Enable or disable a button
        
        Args:
            name (str): Button's internal name
            enabled (bool): Whether to enable or disable the button
        """
        if button := self.buttons.get(name):
            button.setEnabled(enabled)
            
    def set_button_text(self, name, text):
        """Set a button's text
        
        Args:
            name (str): Button's internal name
            text (str): New button text
        """
        if button := self.buttons.get(name):
            button.setText(text) 