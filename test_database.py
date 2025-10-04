import os
import sys

# Check if database.py exists
if os.path.exists("database.py"):
    print("✓ database.py file exists")
    
    # Read the file content
    with open("database.py", "r") as f:
        content = f.read()
        print("File content:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Check if StudentDatabase class exists
        if "class StudentDatabase" in content:
            print("✓ StudentDatabase class found in file")
        else:
            print("✗ StudentDatabase class NOT found in file")
            
        # Check what classes are defined
        import re
        classes = re.findall(r'class\s+(\w+)', content)
        if classes:
            print(f"Classes found: {classes}")
        else:
            print("No classes found in file")
else:
    print("✗ database.py file does not exist")