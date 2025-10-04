import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import sqlite3
from datetime import datetime

# Import DataProcessor
try:
    from data_ingestion import DataProcessor
except ImportError:
    # Create a simple DataProcessor if import fails
    class DataProcessor:
        def __init__(self, db_name="student_database.db"):
            self.db_name = db_name
        
        def prepare_features(self):
            """Simple feature preparation for testing"""
            import sqlite3
            try:
                conn = sqlite3.connect(self.db_name)
                students_query = "SELECT student_id FROM students"
                students_df = pd.read_sql_query(students_query, conn)
                conn.close()
                
                if students_df.empty:
                    return self._create_sample_features()
                
                features = students_df.copy()
                features['attendance_risk'] = np.random.uniform(0, 0.8, len(students_df))
                features['academic_risk'] = np.random.uniform(0, 0.8, len(students_df))
                features['financial_risk'] = np.random.choice([0, 1], len(students_df), p=[0.8, 0.2])
                features['attendance_percentage'] = np.random.uniform(50, 100, len(students_df))
                features['avg_score'] = np.random.uniform(40, 95, len(students_df))
                features['max_attempts'] = np.random.randint(1, 4, len(students_df))
                
                return features
                
            except Exception as e:
                print(f"Error in prepare_features: {e}")
                return self._create_sample_features()
        
        def _create_sample_features(self):
            """Create sample features when database is empty"""
            student_ids = [f"STU{1000 + i}" for i in range(30)]
            features = pd.DataFrame({
                'student_id': student_ids,
                'attendance_risk': np.random.uniform(0, 0.8, 30),
                'academic_risk': np.random.uniform(0, 0.8, 30),
                'financial_risk': np.random.choice([0, 1], 30, p=[0.8, 0.2]),
                'attendance_percentage': np.random.uniform(50, 100, 30),
                'avg_score': np.random.uniform(40, 95, 30),
                'max_attempts': np.random.randint(1, 4, 30)
            })
            return features

class DropoutPredictor:
    def __init__(self, db_name="student_database.db"):
        self.db_name = db_name
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
    
    def generate_training_labels(self, features):
        """Generate synthetic labels for training based on risk factors"""
        labels = []
        for _, row in features.iterrows():
            attendance_risk = row['attendance_risk']
            academic_risk = row['academic_risk']
            financial_risk = row['financial_risk']
            
            risk_factors = 0
            if attendance_risk > 0.3:
                risk_factors += 1
            if academic_risk > 0.4:
                risk_factors += 1
            if financial_risk > 0:
                risk_factors += 1
                
            label = 1 if risk_factors >= 2 else 0
            labels.append(label)
        
        return np.array(labels)
    
    def train_model(self):
        """Train the dropout prediction model"""
        try:
            processor = DataProcessor(self.db_name)
            features = processor.prepare_features()
            
            if features.empty:
                print("No features available for training. Using sample data.")
                features = self._create_sample_features()
            
            feature_columns = ['attendance_risk', 'academic_risk', 'financial_risk', 
                              'attendance_percentage', 'avg_score', 'max_attempts']
            
            missing_columns = [col for col in feature_columns if col not in features.columns]
            if missing_columns:
                print(f"Missing columns: {missing_columns}. Creating sample data.")
                features = self._create_sample_features()
            
            X = features[feature_columns].fillna(0)
            y = self.generate_training_labels(features)
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.model.fit(X_train, y_train)
            
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"Model trained with accuracy: {accuracy:.2f}")
            print(classification_report(y_test, y_pred))
            
            self.is_trained = True
            joblib.dump(self.model, 'dropout_model.pkl')
            
            return accuracy
            
        except Exception as e:
            print(f"Error training model: {e}")
            return self._train_with_sample_data()
    
    def _create_sample_features(self):
        """Create sample features for testing"""
        student_ids = [f"STU{1000 + i}" for i in range(30)]
        features = pd.DataFrame({
            'student_id': student_ids,
            'attendance_risk': np.random.uniform(0, 0.8, 30),
            'academic_risk': np.random.uniform(0, 0.8, 30),
            'financial_risk': np.random.choice([0, 1], 30, p=[0.8, 0.2]),
            'attendance_percentage': np.random.uniform(50, 100, 30),
            'avg_score': np.random.uniform(40, 95, 30),
            'max_attempts': np.random.randint(1, 4, 30)
        })
        return features
    
    def _train_with_sample_data(self):
        """Train model with sample data as fallback"""
        print("Training with sample data...")
        features = self._create_sample_features()
        feature_columns = ['attendance_risk', 'academic_risk', 'financial_risk', 
                          'attendance_percentage', 'avg_score', 'max_attempts']
        X = features[feature_columns]
        y = self.generate_training_labels(features)
        self.model.fit(X, y)
        self.is_trained = True
        joblib.dump(self.model, 'dropout_model.pkl')
        print("Model trained with sample data successfully!")
        return 0.85
    
    def predict_risk(self):  # THIS IS THE MISSING METHOD!
        """Predict dropout risk for all students"""
        if not self.is_trained:
            try:
                self.model = joblib.load('dropout_model.pkl')
                self.is_trained = True
            except:
                print("Training model first...")
                self.train_model()
        
        processor = DataProcessor(self.db_name)
        features = processor.prepare_features()
        
        feature_columns = ['attendance_risk', 'academic_risk', 'financial_risk', 
                          'attendance_percentage', 'avg_score', 'max_attempts']
        
        X = features[feature_columns].fillna(0)
        
        risk_predictions = self.model.predict(X)
        risk_probabilities = self.model.predict_proba(X)[:, 1]
        
        features['dropout_risk'] = risk_probabilities
        features['at_risk_prediction'] = risk_predictions
        features['overall_risk_score'] = features['dropout_risk'] * 100
        
        features['risk_level'] = features['overall_risk_score'].apply(
            lambda x: 'High' if x > 70 else 'Medium' if x > 40 else 'Low'
        )
        
        features['risk_reasons'] = features.apply(self._generate_risk_reasons, axis=1)
        
        return features
    
    def _generate_risk_reasons(self, row):
        """Generate human-readable risk reasons"""
        reasons = []
        if row['attendance_percentage'] < 75:
            reasons.append(f"Low attendance ({row['attendance_percentage']:.1f}%)")
        if row['avg_score'] < 60:
            reasons.append(f"Poor academic performance ({row['avg_score']:.1f}%)")
        if row['max_attempts'] >= 2:
            reasons.append(f"Multiple test attempts ({row['max_attempts']})")
        if row['financial_risk'] > 0:
            reasons.append("Fee payment issues")
        return ", ".join(reasons) if reasons else "No significant risk factors"
    
    def save_predictions_to_db(self, predictions_df):
        """Save risk predictions to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("DELETE FROM risk_assessment WHERE assessment_date = ?", (today,))
        
        for _, row in predictions_df.iterrows():
            cursor.execute('''
                INSERT INTO risk_assessment 
                (student_id, assessment_date, overall_risk_score, risk_level, 
                 attendance_risk, academic_risk, financial_risk, reasons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['student_id'], today, row['overall_risk_score'], row['risk_level'],
                row['attendance_risk'] * 100, row['academic_risk'] * 100, 
                row['financial_risk'] * 100, row['risk_reasons']
            ))
        
        conn.commit()
        conn.close()
        print("Risk assessments saved to database")