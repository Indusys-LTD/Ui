from PySide6.QtWidgets import (QComboBox, QTextEdit, QSpinBox, 
                             QDoubleSpinBox, QLineEdit, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Signal

class LabeledComboBox(QWidget):
    value_changed = Signal(str)
    
    def __init__(self, label="", items=None, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(label)
        self.combo = QComboBox()
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo)
        
        if items:
            self.set_items(items)
            
        self.combo.currentTextChanged.connect(self.value_changed.emit)
        
    def set_items(self, items):
        """Set combobox items"""
        self.combo.clear()
        self.combo.addItems(items)
        
    def get_value(self):
        """Get current value"""
        return self.combo.currentText()

class LabeledTextEdit(QWidget):
    text_changed = Signal(str)
    
    def __init__(self, label="", placeholder="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.label = QLabel(label)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(placeholder)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_edit)
        
        self.text_edit.textChanged.connect(
            lambda: self.text_changed.emit(self.text_edit.toPlainText())
        )
        
    def get_text(self):
        """Get current text"""
        return self.text_edit.toPlainText()
        
    def set_text(self, text):
        """Set text content"""
        self.text_edit.setText(text)

class LabeledSpinBox(QWidget):
    value_changed = Signal(int)
    
    def __init__(self, label="", minimum=0, maximum=100, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(label)
        self.spin = QSpinBox()
        
        self.spin.setMinimum(minimum)
        self.spin.setMaximum(maximum)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spin)
        
        self.spin.valueChanged.connect(self.value_changed.emit)
        
    def get_value(self):
        """Get current value"""
        return self.spin.value()
        
    def set_value(self, value):
        """Set current value"""
        self.spin.setValue(value)

class LabeledLineEdit(QWidget):
    text_changed = Signal(str)
    
    def __init__(self, label="", placeholder="", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(label)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        
        self.line_edit.textChanged.connect(self.text_changed.emit)
        
    def get_text(self):
        """Get current text"""
        return self.line_edit.text()
        
    def set_text(self, text):
        """Set text content"""
        self.line_edit.setText(text) 