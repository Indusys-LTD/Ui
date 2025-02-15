from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame, QScrollArea)
from PySide6.QtCore import Qt
import random

class AITab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_data()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Create container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # AI Analysis Section
        self.market_sentiment = QLabel()
        self.market_sentiment.setStyleSheet("font-size: 14px; margin: 10px;")
        
        analysis_frame = self.create_section(
            "AI Market Analysis",
            [self.market_sentiment]
        )
        container_layout.addWidget(analysis_frame)
        
        # Risk Assessment Section
        risk_widgets = []
        self.risk_metrics = {}
        
        for metric in ["Market Volatility", "Portfolio Risk", "Trading Strategy Risk"]:
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
            self.risk_metrics[metric] = progress
            risk_widgets.append(metric_container)
        
        risk_frame = self.create_section("Risk Assessment", risk_widgets)
        container_layout.addWidget(risk_frame)
        
        # Predictions Section
        prediction_widgets = []
        self.predictions = {}
        
        for pair in ["EURUSD", "GBPUSD", "BTCUSD"]:
            pred_container = QWidget()
            pred_layout = QHBoxLayout(pred_container)
            pred_layout.setContentsMargins(0, 0, 0, 0)
            
            label = QLabel(f"{pair} Trend:")
            prediction = QLabel()
            prediction.setStyleSheet("font-weight: bold;")
            
            pred_layout.addWidget(label)
            pred_layout.addWidget(prediction)
            self.predictions[pair] = prediction
            prediction_widgets.append(pred_container)
        
        predictions_frame = self.create_section("AI Predictions", prediction_widgets)
        container_layout.addWidget(predictions_frame)
        
        # Add spacer at the bottom
        container_layout.addStretch()
        
        # Set scroll area widget
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def create_section(self, title, widgets):
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
        
        # Add header
        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(header)
        
        # Add widgets
        for widget in widgets:
            layout.addWidget(widget)
        
        return frame
        
    def load_sample_data(self):
        # Sample market sentiment analysis
        sentiment = random.choice(["Bullish", "Bearish", "Neutral"])
        confidence = random.randint(65, 95)
        
        sentiment_color = {
            "Bullish": "green",
            "Bearish": "red",
            "Neutral": "yellow"
        }
        
        self.market_sentiment.setText(
            f"Current Market Sentiment: <span style='color: {sentiment_color[sentiment]}'>"
            f"{sentiment}</span> (Confidence: {confidence}%)<br><br>"
            "Key Factors:<br>"
            "• Technical indicators suggest strong momentum<br>"
            "• Volume analysis shows increasing market participation<br>"
            "• Sentiment analysis of news and social media is positive"
        )
        
        # Sample risk metrics
        for metric, progress in self.risk_metrics.items():
            risk_level = random.randint(20, 80)
            progress.setValue(risk_level)
            
        # Sample predictions
        trend_options = [
            ("Upward", "green", "↑"),
            ("Downward", "red", "↓"),
            ("Sideways", "yellow", "→")
        ]
        
        for pair, label in self.predictions.items():
            trend, color, arrow = random.choice(trend_options)
            probability = random.randint(60, 90)
            label.setText(
                f"<span style='color: {color}'>{trend} {arrow}</span> "
                f"(Probability: {probability}%)"
            ) 