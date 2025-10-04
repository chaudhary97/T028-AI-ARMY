import os
import sys

print("Testing Student Dropout Prediction System...")
print("=" * 50)

# Test 1: Check database.py
print("\n1. Testing database.py...")
try:
    with open("database.py", "r") as f:
        content = f.read()
        if "class StudentDatabase" in content:
            print("   ✓ StudentDatabase class found")
        else:
            print("   ✗ StudentDatabase class NOT found")
            
    from database import StudentDatabase
    print("   ✓ Successfully imported StudentDatabase")
    
    # Test instantiation
    db = StudentDatabase()
    print("   ✓ Successfully created StudentDatabase instance")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Check other imports
print("\n2. Testing other imports...")
try:
    from ml_model import DropoutPredictor
    print("   ✓ Successfully imported DropoutPredictor")
except ImportError as e:
    print(f"   ✗ Error importing DropoutPredictor: {e}")

try:
    from notification_system import NotificationSystem
    print("   ✓ Successfully imported NotificationSystem")
except ImportError as e:
    print(f"   ✗ Error importing NotificationSystem: {e}")

try:
    from dashboard import run_dashboard
    print("   ✓ Successfully imported run_dashboard")
except ImportError as e:
    print(f"   ✗ Error importing dashboard: {e}")

print("\n" + "=" * 50)
print("Testing completed!")