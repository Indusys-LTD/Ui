from PySide6.QtWidgets import QProgressBar
from PySide6.QtCore import QTimer

class AnimatedProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        
        # Setup animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_progress)
        self._progress_value = 0
        
    def start_animation(self, interval=100):
        """Start the progress bar animation
        
        Args:
            interval (int): Update interval in milliseconds
        """
        self._timer.start(interval)
        
    def stop_animation(self):
        """Stop the progress bar animation"""
        self._timer.stop()
        
    def _update_progress(self):
        """Update the progress value"""
        self._progress_value = (self._progress_value + 1) % 101
        self.setValue(self._progress_value)
        
    def set_progress(self, value):
        """Set the progress bar value directly
        
        Args:
            value (int): Progress value (0-100)
        """
        self._progress_value = max(0, min(100, value))
        self.setValue(self._progress_value) 