import json
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from datetime import datetime

class TradingReport(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        
        # Load initial data
        self.load_data()
        
        # Connect buttons
        self.generateBtn.clicked.connect(self.generate_report)
        
    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = self.get_default_data()
            
    def get_default_data(self):
        return {
            "account": {
                "name": "Demo Account",
                "currency": "EUR",
                "type": "demo",
                "broker": "MetaQuotes Ltd.",
                "account": 90121026,
                "digits": 2
            },
            "summary": {
                "gain": 0.0,
                "activity": 0.0,
                "deposit": [0.0, 0],
                "withdrawal": [0.0, 0],
                "dividend": 0.0,
                "correction": 0.0,
                "credit": 0.0
            }
        }
        
    def generate_report(self):
        # Get date range
        start_date = self.startDate.date().toPyDate()
        end_date = self.endDate.date().toPyDate()
        
        # Generate report data
        report_data = self.generate_report_data(start_date, end_date)
        
        # Save report
        self.save_report(report_data)
        
    def generate_report_data(self, start_date, end_date):
        # Here you would add logic to generate the actual report data
        # This is a simplified example
        return {
            "account": self.data["account"],
            "summary": self.data["summary"],
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        }
        
    def save_report(self, report_data):
        # Save as HTML report
        with open('Report.html', 'r') as template:
            html = template.read()
            
        # Insert report data
        html = html.replace('window.__report = {}', 
                          f'window.__report = {json.dumps(report_data)}')
            
        # Save generated report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f'report_{timestamp}.html', 'w') as f:
            f.write(html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TradingReport()
    window.show()
    sys.exit(app.exec_())
