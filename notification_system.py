import sqlite3
from datetime import datetime
from email_sender import send_email
import pandas as pd

class NotificationSystem:
    def __init__(self, db_name="student_database.db"):
        self.db_name = db_name
    
    def generate_mentor_notifications(self):
        """Generate notifications for mentors about at-risk students"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            query = '''
                SELECT r.student_id, s.name as student_name, s.mentor_id, 
                       r.overall_risk_score, r.risk_level, r.reasons
                FROM risk_assessment r
                JOIN students s ON r.student_id = s.student_id
                WHERE r.risk_level IN ('High', 'Medium')
                AND r.assessment_date = date('now')
            '''
            
            at_risk_students = pd.read_sql_query(query, conn)
            conn.close()
            
            if at_risk_students.empty:
                print("No at-risk students found for mentor notifications.")
                return []
            
            notifications = []
            for mentor_id in at_risk_students['mentor_id'].unique():
                mentor_students = at_risk_students[at_risk_students['mentor_id'] == mentor_id]
                
                message = f"Alert: {len(mentor_students)} students under your mentorship require attention:\n\n"
                
                for _, student in mentor_students.iterrows():
                    message += f"• {student['student_name']} ({student['student_id']}) - "
                    message += f"{student['risk_level']} Risk ({student['overall_risk_score']:.1f}/100)\n"
                    message += f"  Reasons: {student['reasons']}\n\n"
                
                message += "Please schedule counseling sessions and contact guardians if necessary."
                
                notifications.append({
                    'mentor_id': mentor_id,
                    'message': message,
                    'student_count': len(mentor_students)
                })
            
            return notifications
            
        except Exception as e:
            print(f"Error generating mentor notifications: {e}")
            return []
    
    def generate_guardian_notifications(self):
        """Generate notifications for guardians"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            query = '''
                SELECT s.student_id, s.name as student_name, s.guardian_name, 
                       s.guardian_phone, r.overall_risk_score, r.risk_level, r.reasons
                FROM risk_assessment r
                JOIN students s ON r.student_id = s.student_id
                WHERE r.risk_level = 'High'
                AND r.assessment_date = date('now')
            '''
            
            high_risk_students = pd.read_sql_query(query, conn)
            conn.close()
            
            if high_risk_students.empty:
                print("No high-risk students found for guardian notifications.")
                return []
            
            notifications = []
            for _, student in high_risk_students.iterrows():
                message = f"Dear {student['guardian_name']},\n\n"
                message += f"We would like to inform you that {student['student_name']} has been "
                message += f"identified as high risk for academic challenges. "
                message += f"Current risk score: {student['overall_risk_score']:.1f}/100.\n\n"
                message += f"Primary concerns: {student['reasons']}\n\n"
                message += "Please contact the student's mentor to discuss support strategies."
                
                notifications.append({
                    'guardian_name': student['guardian_name'],
                    'guardian_phone': student['guardian_phone'],
                    'student_name': student['student_name'],
                    'student_id': student['student_id'],
                    'message': message
                })
            
            return notifications
            
        except Exception as e:
            print(f"Error generating guardian notifications: {e}")
            return []
    
    def save_notifications_to_db(self, notifications, notification_type):
        """Save notifications to database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            for notification in notifications:
                if notification_type == 'mentor':
                    cursor.execute('''
                        INSERT INTO notifications 
                        (student_id, mentor_id, notification_type, message, sent_date, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        'ALL',
                        notification['mentor_id'],
                        'MENTOR_ALERT',
                        notification['message'],
                        datetime.now().strftime('%Y-%m-%d'),
                        'PENDING'
                    ))
                elif notification_type == 'guardian':
                    cursor.execute('''
                        INSERT INTO notifications 
                        (student_id, mentor_id, notification_type, message, sent_date, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        notification.get('student_id', 'UNKNOWN'),
                        'GUARDIAN',
                        'GUARDIAN_ALERT',
                        notification['message'],
                        datetime.now().strftime('%Y-%m-%d'),
                        'PENDING'
                    ))
            
            conn.commit()
            conn.close()
            print(f"Successfully saved {len(notifications)} {notification_type} notifications to database.")
            
        except Exception as e:
            print(f"Error saving notifications to database: {e}")
    
    def send_notifications(self):
        """Generate and save all notifications"""
        try:
            print("Generating mentor notifications...")
            mentor_notifications = self.generate_mentor_notifications()
            self.save_notifications_to_db(mentor_notifications, 'mentor')
            
            print("Generating guardian notifications...")
            guardian_notifications = self.generate_guardian_notifications()
            self.save_notifications_to_db(guardian_notifications, 'guardian')
            
            total_notifications = len(mentor_notifications) + len(guardian_notifications)
            print(f"Successfully generated {total_notifications} total notifications")
            
            return total_notifications
            
        except Exception as e:
            print(f"Error in send_notifications: {e}")
            return 0