import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta

class DataProcessor:
    def __init__(self, db_name="student_database.db"):
        self.db_name = db_name
    
    def calculate_attendance_metrics(self):
        """Calculate attendance percentages and risks"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT 
                student_id,
                subject,
                COUNT(*) as total_classes,
                SUM(CAST(present AS INTEGER)) as attended_classes,
                (SUM(CAST(present AS INTEGER)) * 100.0 / COUNT(*)) as attendance_percentage
            FROM attendance
            WHERE date >= date('now', '-30 days')
            GROUP BY student_id, subject
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def calculate_academic_metrics(self):
        """Calculate academic performance metrics"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT 
                student_id,
                subject,
                AVG(score) as avg_score,
                MAX(attempt_number) as max_attempts,
                COUNT(*) as total_tests,
                MIN(score) as min_score,
                MAX(score) as max_score
            FROM test_scores
            WHERE test_date >= date('now', '-60 days')
            GROUP BY student_id, subject
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def calculate_financial_metrics(self):
        """Calculate financial risk metrics"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT 
                student_id,
                status,
                amount_due,
                amount_paid,
                (amount_due - amount_paid) as pending_amount,
                CASE 
                    WHEN status = 'Pending' AND due_date < date('now') THEN 1 
                    ELSE 0 
                END as is_overdue
            FROM fee_payments
            WHERE due_date >= date('now', '-90 days')
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_student_details(self):
        """Get basic student information"""
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT student_id, name, email, phone, guardian_name, guardian_phone, mentor_id
            FROM students
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def prepare_features(self):
        """Prepare features for ML model"""
        try:
            # Get all metrics
            attendance_df = self.calculate_attendance_metrics()
            academic_df = self.calculate_academic_metrics()
            financial_df = self.calculate_financial_metrics()
            student_df = self.get_student_details()
            
            # Aggregate attendance by student
            attendance_agg = attendance_df.groupby('student_id').agg({
                'attendance_percentage': 'mean',
                'total_classes': 'sum',
                'attended_classes': 'sum'
            }).reset_index()
            attendance_agg['attendance_risk'] = (100 - attendance_agg['attendance_percentage']) / 100
            
            # Aggregate academic performance
            academic_agg = academic_df.groupby('student_id').agg({
                'avg_score': 'mean',
                'max_attempts': 'max',
                'total_tests': 'sum',
                'min_score': 'min'
            }).reset_index()
            academic_agg['academic_risk'] = ((100 - academic_agg['avg_score']) / 100) * 0.7 + \
                                           (academic_agg['max_attempts'] / 3) * 0.3
            
            # Aggregate financial data
            financial_agg = financial_df.groupby('student_id').agg({
                'is_overdue': 'max',
                'pending_amount': 'sum'
            }).reset_index()
            financial_agg['financial_risk'] = financial_agg['is_overdue']
            
            # Merge all features
            features = student_df.merge(attendance_agg, on='student_id', how='left')
            features = features.merge(academic_agg, on='student_id', how='left')
            features = features.merge(financial_agg, on='student_id', how='left')
            
            # Fill NaN values
            features.fillna({
                'attendance_risk': 0,
                'academic_risk': 0,
                'financial_risk': 0,
                'attendance_percentage': 100,
                'avg_score': 100
            }, inplace=True)
            
            return features
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=['student_id', 'attendance_risk', 'academic_risk', 'financial_risk', 
                                       'attendance_percentage', 'avg_score', 'max_attempts'])