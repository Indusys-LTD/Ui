from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
import random
from datetime import datetime, timedelta

class DatabaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_timer()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Connection Status Section
        status_frame = self.create_section("Database Connection Status")
        status_layout = QHBoxLayout()
        
        self.connection_status = QLabel()
        self.connection_status.setStyleSheet("font-size: 14px; margin: 10px;")
        status_layout.addWidget(self.connection_status)
        
        self.response_time = QLabel()
        self.response_time.setStyleSheet("font-size: 14px; margin: 10px;")
        status_layout.addWidget(self.response_time)
        
        status_layout.addStretch()
        status_frame.layout().addLayout(status_layout)
        main_layout.addWidget(status_frame)
        
        # Performance Metrics Section
        metrics_frame = self.create_section("Performance Metrics")
        metrics_layout = QVBoxLayout()
        
        self.metrics = {}
        for metric in ["CPU Usage", "Memory Usage", "Disk I/O", "Active Connections"]:
            metric_container = QWidget()
            metric_layout = QHBoxLayout(metric_container)
            metric_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{metric}:")
            progress = QProgressBar()
            progress.setTextVisible(True)
            progress.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #2D2D2D;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
            
            metric_layout.addWidget(label)
            metric_layout.addWidget(progress)
            self.metrics[metric] = progress
            metrics_layout.addWidget(metric_container)
            
        metrics_frame.layout().addLayout(metrics_layout)
        main_layout.addWidget(metrics_frame)
        
        # Recent Queries Section
        queries_frame = self.create_section("Recent Queries")
        
        self.queries_table = QTableWidget()
        self.queries_table.setColumnCount(4)
        self.queries_table.setHorizontalHeaderLabels([
            "Timestamp", "Query Type", "Duration (ms)", "Status"
        ])
        
        # Set table properties
        self.queries_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.queries_table.setAlternatingRowColors(True)
        self.queries_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #2D2D2D;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #FFFFFF;
                padding: 5px;
            }
        """)
        
        queries_frame.layout().addWidget(self.queries_table)
        main_layout.addWidget(queries_frame)
        
    def create_section(self, title):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2D2D2D;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        return frame
        
    def setup_timer(self):
        """Setup timer for periodic updates"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(5000)  # Update every 5 seconds
        
    def load_sample_data(self):
        """Load initial sample data"""
        self.update_connection_status()
        self.update_metrics()
        self.update_queries()
        
    def update_connection_status(self):
        """Update connection status indicators"""
        status = random.choice(["Connected", "Connected", "Connected", "Slow Response"])
        response = random.randint(5, 100)
        
        status_color = "#4CAF50" if status == "Connected" else "#FFA500"
        response_color = "#4CAF50" if response < 50 else "#FFA500"
        
        self.connection_status.setText(
            f"Status: <span style='color: {status_color}'>{status}</span>"
        )
        self.response_time.setText(
            f"Response Time: <span style='color: {response_color}'>{response} ms</span>"
        )
        
    def update_metrics(self):
        """Update performance metrics"""
        for metric, progress in self.metrics.items():
            if metric == "Active Connections":
                value = random.randint(10, 50)
            else:
                value = random.randint(20, 80)
            progress.setValue(value)
            
            # Update progress bar color based on value
            color = "#4CAF50" if value < 70 else "#FFA500" if value < 90 else "#F44336"
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #2D2D2D;
                    border-radius: 5px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                }}
            """)
            
    def update_queries(self):
        """Update recent queries table"""
        query_types = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        statuses = [
            ("Success", QColor("#4CAF50")),
            ("Success", QColor("#4CAF50")),
            ("Success", QColor("#4CAF50")),
            ("Slow", QColor("#FFA500")),
            ("Error", QColor("#F44336"))
        ]
        
        # Generate sample queries
        now = datetime.now()
        queries = []
        
        for i in range(10):
            time = now - timedelta(seconds=random.randint(0, 300))
            query_type = random.choice(query_types)
            duration = random.randint(5, 200)
            status, color = random.choice(statuses)
            
            queries.append({
                'time': time.strftime("%H:%M:%S"),
                'type': query_type,
                'duration': duration,
                'status': (status, color)
            })
            
        # Sort queries by time
        queries.sort(key=lambda x: x['time'], reverse=True)
        
        # Update table
        self.queries_table.setRowCount(len(queries))
        for row, query in enumerate(queries):
            self.queries_table.setItem(row, 0, QTableWidgetItem(query['time']))
            self.queries_table.setItem(row, 1, QTableWidgetItem(query['type']))
            self.queries_table.setItem(row, 2, QTableWidgetItem(str(query['duration'])))
            
            status_item = QTableWidgetItem(query['status'][0])
            status_item.setForeground(query['status'][1])
            self.queries_table.setItem(row, 3, status_item) 