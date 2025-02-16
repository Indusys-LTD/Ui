from typing import Dict, List, Any
from .model import AIModel
from .data_organizer import DataOrganizer

class RequestProcessor:
    def __init__(self, model: AIModel, data_organizer: DataOrganizer):
        """
        Initialize the request processor.
        
        Args:
            model: Instance of AIModel
            data_organizer: Instance of DataOrganizer
        """
        self.model = model
        self.data_organizer = data_organizer
        
    def process_request(self, input_data: Dict[str, Any]) -> List[float]:
        """
        Process a live request and return recommendations.
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            List of recommendations
        """
        # Organize the input data
        organized_data = self.data_organizer.organize_live_data(input_data)
        
        # Normalize the data
        normalized_data = self.data_organizer.normalize_data(organized_data)
        
        # Get predictions from the model
        predictions = self.model.predict(normalized_data)
        
        return predictions
    
    def format_recommendations(self, predictions: List[float]) -> List[Dict[str, Any]]:
        """
        Format the raw predictions into human-readable recommendations.
        
        Args:
            predictions: Raw model predictions
            
        Returns:
            List of formatted recommendations
        """
        recommendations = []
        
        # Example formatting - customize based on your specific needs
        if len(predictions) >= 3:  # Assuming we have at least 3 prediction values
            recommendations.append({
                'action': 'Risk Level',
                'value': f"{predictions[0]:.2f}",
                'confidence': f"{predictions[1]:.2%}"
            })
            
            recommendations.append({
                'action': 'Suggested Position',
                'value': f"{predictions[2]:.2f}",
                'confidence': f"{predictions[1]:.2%}"
            })
            
        return recommendations 