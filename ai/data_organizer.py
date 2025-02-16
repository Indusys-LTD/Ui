import pandas as pd
import psycopg2
from typing import Dict, List, Any
import numpy as np

class DataOrganizer:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the DataOrganizer with database configuration.
        
        Args:
            db_config: Dictionary containing database connection parameters
                      (host, database, user, password, port)
        """
        self.db_config = db_config
        
    def _get_db_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(**self.db_config)
    
    def fetch_training_data(self, query: str) -> tuple[List[Dict[str, Any]], List[List[float]]]:
        """
        Fetch and organize training data from the database.
        
        Args:
            query: SQL query to fetch the training data
            
        Returns:
            Tuple of (input_vectors, output_labels)
        """
        with self._get_db_connection() as conn:
            df = pd.read_sql(query, conn)
            
        # Convert dataframe to input vectors and output labels
        input_vectors = df.drop(['output_labels'], axis=1).to_dict('records')
        output_labels = df['output_labels'].tolist()
        
        return input_vectors, output_labels
    
    def organize_live_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Organize live input data into the format expected by the model.
        
        Args:
            input_data: Raw input data dictionary
            
        Returns:
            Processed input data in the correct format
        """
        # Add any necessary preprocessing steps here
        return input_data
    
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the input data to ensure consistent scaling.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Normalized data dictionary
        """
        normalized_data = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # Apply min-max normalization
                normalized_data[key] = (value - self.feature_mins.get(key, 0)) / \
                                     (self.feature_maxs.get(key, 1) - self.feature_mins.get(key, 0) + 1e-8)
            else:
                normalized_data[key] = value
        return normalized_data
    
    def update_normalization_params(self, training_data: List[Dict[str, Any]]):
        """
        Update the normalization parameters based on training data.
        
        Args:
            training_data: List of training data dictionaries
        """
        self.feature_mins = {}
        self.feature_maxs = {}
        
        for feature in training_data[0].keys():
            if all(isinstance(d[feature], (int, float)) for d in training_data):
                values = [d[feature] for d in training_data]
                self.feature_mins[feature] = min(values)
                self.feature_maxs[feature] = max(values) 