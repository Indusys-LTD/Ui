from typing import Dict, Any
import schedule
import time
import threading
from .model import AIModel
from .data_organizer import DataOrganizer

class ModelTrainer:
    def __init__(self, model: AIModel, data_organizer: DataOrganizer, 
                 training_query: str, training_interval_hours: int = 24):
        """
        Initialize the model trainer.
        
        Args:
            model: Instance of AIModel
            data_organizer: Instance of DataOrganizer
            training_query: SQL query to fetch training data
            training_interval_hours: Hours between training sessions
        """
        self.model = model
        self.data_organizer = data_organizer
        self.training_query = training_query
        self.training_interval_hours = training_interval_hours
        self._stop_event = threading.Event()
        
    def start_training_schedule(self):
        """Start the scheduled training process in a separate thread."""
        schedule.every(self.training_interval_hours).hours.do(self.train_model)
        
        def run_schedule():
            while not self._stop_event.is_set():
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        self.schedule_thread = threading.Thread(target=run_schedule)
        self.schedule_thread.start()
        
    def stop_training_schedule(self):
        """Stop the scheduled training process."""
        self._stop_event.set()
        if hasattr(self, 'schedule_thread'):
            self.schedule_thread.join()
            
    def train_model(self):
        """
        Perform one training iteration.
        
        Returns:
            bool: True if training was successful
        """
        try:
            # Fetch and organize training data
            input_vectors, output_labels = self.data_organizer.fetch_training_data(
                self.training_query
            )
            
            # Update normalization parameters
            self.data_organizer.update_normalization_params(input_vectors)
            
            # Normalize input vectors
            normalized_vectors = [
                self.data_organizer.normalize_data(vector)
                for vector in input_vectors
            ]
            
            # Train the model
            self.model.train(normalized_vectors, output_labels)
            return True
            
        except Exception as e:
            print(f"Training failed: {str(e)}")
            return False
            
    def train_now(self):
        """
        Trigger an immediate training iteration.
        
        Returns:
            bool: True if training was successful
        """
        return self.train_model() 