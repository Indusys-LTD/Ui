from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton,
                              QFormLayout, QFrame, QComboBox)
from PySide6.QtCore import Qt

class AccountSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Account Setup")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Login credentials section
        credentials_frame = self.create_section("Login Credentials")
        credentials_layout = QFormLayout()
        
        self.login_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.server_combo = QComboBox()
        self.server_combo.addItems(["Demo Server", "Live Server 1", "Live Server 2"])
        
        credentials_layout.addRow("Account Login:", self.login_edit)
        credentials_layout.addRow("Password:", self.password_edit)
        credentials_layout.addRow("Server:", self.server_combo)
        
        credentials_frame.setLayout(credentials_layout)
        main_layout.addWidget(credentials_frame)
        
        # Trading parameters section
        params_frame = self.create_section("Trading Parameters")
        params_layout = QFormLayout()
        
        self.max_positions = QSpinBox()
        self.max_positions.setRange(1, 100)
        self.max_positions.setValue(10)
        
        self.max_volume = QDoubleSpinBox()
        self.max_volume.setRange(0.01, 100.0)
        self.max_volume.setValue(1.0)
        self.max_volume.setSingleStep(0.01)
        
        self.base_balance = QDoubleSpinBox()
        self.base_balance.setRange(0, 1000000)
        self.base_balance.setValue(10000)
        self.base_balance.setSingleStep(100)
        self.base_balance.setPrefix("$")
        
        params_layout.addRow("Max Positions:", self.max_positions)
        params_layout.addRow("Max Volume:", self.max_volume)
        params_layout.addRow("Base Balance:", self.base_balance)
        
        params_frame.setLayout(params_layout)
        main_layout.addWidget(params_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Set dialog size
        self.setMinimumWidth(400)
        
    def create_section(self, title):
        """Create a styled section frame"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #4CAF50;
            }
        """)
        
        # Add title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        frame.title_label = title_label  # Keep reference to add in layout later
        
        return frame
        
    def get_account_data(self):
        """Return the account data as a dictionary"""
        return {
            'login': self.login_edit.text(),
            'password': self.password_edit.text(),
            'server': self.server_combo.currentText(),
            'max_positions': self.max_positions.value(),
            'max_volume': self.max_volume.value(),
            'base_balance': self.base_balance.value()
        } 