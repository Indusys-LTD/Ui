from typing import Dict, List, Any
from .model import AIModel
from .data_organizer import DataOrganizer
from .trainer import ModelTrainer
from .processor import RequestProcessor

class AIExpert:
    def __init__(self, db_config: Dict[str, str], model_path: str = "ai_model.joblib",
                 training_query: str = None, training_interval_hours: int = 24):
        """
        Initialize the AI Expert system.
        
        Args:
            db_config: Database configuration dictionary
            model_path: Path to save/load the model
            training_query: SQL query for fetching training data
            training_interval_hours: Hours between training sessions
        """
        # Initialize components
        self.data_organizer = DataOrganizer(db_config)
        self.model = AIModel(model_path)
        self.trainer = ModelTrainer(
            self.model,
            self.data_organizer,
            training_query or self._default_training_query(),
            training_interval_hours
        )
        self.processor = RequestProcessor(self.model, self.data_organizer)
        
    def start_training_schedule(self):
        """Start the scheduled training process."""
        self.trainer.start_training_schedule()
        
    def stop_training_schedule(self):
        """Stop the scheduled training process."""
        self.trainer.stop_training_schedule()
        
    def train_now(self) -> bool:
        """
        Trigger an immediate training iteration.
        
        Returns:
            bool: True if training was successful
        """
        return self.trainer.train_now()
    
    def get_recommendations(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get recommendations for the given input data.
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            List of recommendations
        """
        predictions = self.processor.process_request(input_data)
        return self.processor.format_recommendations(predictions)
    
    def _default_training_query(self) -> str:
        """
        Return the default training query if none is provided.
        
        Returns:
            str: SQL query for fetching training data
        """
        return """
            SELECT 
                input_features.*,
                array[risk_level, confidence, suggested_position] as output_labels
            FROM training_data
            JOIN input_features ON training_data.feature_id = input_features.id
            ORDER BY training_data.timestamp DESC
            LIMIT 10000
        """

# Example usage:
#if __name__ == "__main__":
    # Database configuration
#    db_config = {
#        "host": "localhost",
#        "database": "your_database",
#        "user": "your_user",
#        "password": "your_password",
#        "port": "5432"
#    }
    
    # Initialize AI Expert
#    ai_expert = AIExpert(db_config)
    
    # Start training schedule
#    ai_expert.start_training_schedule()
    
    # Example input data
#    input_data = {
#        "market_trend": 0.75,
#        "volatility": 0.45,
#        "volume": 1000000,
#        "price": 150.50,
#        "momentum": 0.25
#    }
    
    # Get recommendations
#    recommendations = ai_expert.get_recommendations(input_data)
#    print("Recommendations:", recommendations)
