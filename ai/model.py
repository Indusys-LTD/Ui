import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from typing import Dict, List, Any
import os

class AIModel:
    def __init__(self, model_path: str = "ai_model.joblib"):
        """
        Initialize the AI model.
        
        Args:
            model_path: Path to save/load the model
        """
        self.model_path = model_path
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42
        )
        self.load_model_if_exists()
        
    def load_model_if_exists(self):
        """Load the model if it exists at the specified path."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            
    def save_model(self):
        """Save the current model to disk."""
        joblib.dump(self.model, self.model_path)
        
    def train(self, input_vectors: List[Dict[str, Any]], output_labels: List[List[float]]):
        """
        Train the model on the provided data.
        
        Args:
            input_vectors: List of input feature dictionaries
            output_labels: List of output label lists
        """
        # Convert input dictionaries to feature matrix
        X = self._convert_to_feature_matrix(input_vectors)
        y = np.array(output_labels)
        
        # Train the model
        self.model.fit(X, y)
        self.save_model()
        
    def predict(self, input_vector: Dict[str, Any]) -> List[float]:
        """
        Make predictions for a single input vector.
        
        Args:
            input_vector: Dictionary of input features
            
        Returns:
            List of predicted values
        """
        X = self._convert_to_feature_matrix([input_vector])
        predictions = self.model.predict(X)
        return predictions[0].tolist()
    
    def _convert_to_feature_matrix(self, input_vectors: List[Dict[str, Any]]) -> np.ndarray:
        """
        Convert a list of input dictionaries to a numpy feature matrix.
        
        Args:
            input_vectors: List of input feature dictionaries
            
        Returns:
            Numpy array of features
        """
        # Get all feature names from the first dictionary
        feature_names = list(input_vectors[0].keys())
        
        # Create the feature matrix
        X = np.zeros((len(input_vectors), len(feature_names)))
        for i, vector in enumerate(input_vectors):
            for j, feature in enumerate(feature_names):
                X[i, j] = float(vector[feature])
                
        return X 