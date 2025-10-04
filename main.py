import argparse
import sys
import os
import subprocess
import webbrowser
import time

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def import_modules(require_notifications=False):
    """Import all required modules with error handling"""
    try:
        from database import StudentDatabase
        print("✅ Successfully imported StudentDatabase")
    except ImportError as e:
        print(f"❌ Error importing StudentDatabase: {e}")
        return False
    
    try:
        from ml_model import DropoutPredictor
        print("✅ Successfully imported DropoutPredictor")
    except ImportError as e:
        print(f"❌ Error importing DropoutPredictor: {e}")
        return False
    
    if require_notifications:
        try:
            from notification_system import NotificationSystem
            print("✅ Successfully imported NotificationSystem")
        except ImportError as e:
            print(f"❌ Error importing NotificationSystem: {e}")
            return False
    
    return True

def launch_dashboard():
    """Launch Streamlit dashboard in a separate process"""
    print("📈 Launching dashboard...")
    print("🌐 Dashboard will open in your browser at: http://localhost:8501")
    print("⏳ Please wait a few seconds for the dashboard to load...")
    
    try:
        # Run streamlit as a separate process
        dashboard_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard.py", 
            "--server.port=8501",
            "--server.headless=true"
        ])
        
        # Wait a bit for the server to start
        time.sleep(5)
        
        # Open the browser
        webbrowser.open("http://localhost:8501")
        
        print("✅ Dashboard launched successfully!")
        print("💡 Press Ctrl+C in this terminal to stop the dashboard")
        
        return dashboard_process
        
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 You can manually run: streamlit run dashboard.py")
        return None

def main():
    parser = argparse.ArgumentParser(description='Student Dropout Prediction System')
    parser.add_argument('--init-db', action='store_true', help='Initialize database with sample data')
    parser.add_argument('--train-model', action='store_true', help='Train the ML model')
    parser.add_argument('--predict', action='store_true', help='Run predictions')
    parser.add_argument('--notify', action='store_true', help='Send notifications')
    parser.add_argument('--dashboard', action='store_true', help='Launch dashboard')
    
    args = parser.parse_args()
    
    require_notifications = args.notify
    
    if not import_modules(require_notifications):
        print("\n❌ Please fix the import errors first.")
        return
    
    from database import StudentDatabase
    from ml_model import DropoutPredictor
    
    if args.init_db:
        print("\n🗃️ Initializing database...")
        db = StudentDatabase()
        db.generate_sample_data(20)
        print("✅ Database initialized successfully!")
    
    if args.train_model:
        print("\n🤖 Training ML model...")
        predictor = DropoutPredictor()
        accuracy = predictor.train_model()
        print(f"✅ Model training completed with accuracy: {accuracy:.2f}")
    
    if args.predict:
        print("\n📊 Running risk predictions...")
        predictor = DropoutPredictor()
        predictions = predictor.predict_risk()
        predictor.save_predictions_to_db(predictions)
        print(f"✅ Risk assessment completed for {len(predictions)} students")
    
    if args.notify:
        print("\n📧 Sending notifications...")
        from notification_system import NotificationSystem
        notifier = NotificationSystem()
        count = notifier.send_notifications()
        print(f"✅ Notifications generated: {count}")
    
    if args.dashboard:
        launch_dashboard()

if __name__ == "__main__":
    print("🎓 Student Dropout Prediction System")
    print("=" * 50)
    
    if len(sys.argv) == 1:
        print("Running complete setup...")
        
        if not import_modules(require_notifications=True):
            print("\n❌ Please fix import errors before running the complete system.")
            print("\n💡 Try running individual components:")
            print("   python main.py --init-db")
            print("   python main.py --train-model") 
            print("   python main.py --predict")
            print("   streamlit run dashboard.py")
            sys.exit(1)
        
        try:
            from database import StudentDatabase
            from ml_model import DropoutPredictor
            
            print("\n1️⃣ Step 1: Initializing database...")
            db = StudentDatabase()
            db.generate_sample_data(30)
            
            print("\n2️⃣ Step 2: Training ML model...")
            predictor = DropoutPredictor()
            accuracy = predictor.train_model()
            
            print("\n3️⃣ Step 3: Running predictions...")
            predictions = predictor.predict_risk()
            predictor.save_predictions_to_db(predictions)
            print(f"✅ Predictions saved for {len(predictions)} students")
            
            print("\n4️⃣ Step 4: Generating notifications...")
            try:
                from notification_system import NotificationSystem
                notifier = NotificationSystem()
                count = notifier.send_notifications()
                print(f"✅ Notifications generated: {count}")
            except Exception as e:
                print(f"⚠️  Skipping notifications: {e}")
            
            print("\n5️⃣ Step 5: Launching dashboard...")
            print("🎉 All backend processes completed successfully!")
            print("💡 Now run the dashboard separately with: streamlit run dashboard.py")
            
        except Exception as e:
            print(f"\n❌ Error during setup: {e}")
            import traceback
            traceback.print_exc()
            print("\n💡 Try running individual components:")
            print("   python main.py --init-db")
            print("   python main.py --train-model")
            print("   python main.py --predict")
            print("   streamlit run dashboard.py")
    else:
        main()