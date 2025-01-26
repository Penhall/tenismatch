# /tenismatch/apps/matching/ml/training.py 
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

class ModelTraining:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
    def train_model(self, X, y):
        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        return accuracy, report
        
    def save_model(self, filename='tenis_match_model.joblib'):
        joblib.dump(self.model, filename)
        
    def load_model(self, filename='tenis_match_model.joblib'):
        self.model = joblib.load(filename)
        return self.model
        
    def predict_compatibility(self, user_features):
        return self.model.predict_proba(user_features)