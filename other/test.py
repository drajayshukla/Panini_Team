import sys
import os
import datetime

# 1. Manually add the project root to the Python path
# This ensures it works regardless of which folder you run it from
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Now try the import
try:
    from utils.sheets_sync import log_sugar_entry
    print("✅ Module 'utils' found successfully.")
except ImportError as e:
    print(f"❌ Still can't find 'utils'. Error: {e}")
    sys.exit(1)

# Mock a sugar log
test_data = ["TEST_PATIENT", str(datetime.datetime.now()), "71", "FBS", 105, 8, "", "False", "0", "None", "Testing connection"]

if log_sugar_entry(test_data):
    print("✅ Success! The data appeared in your Google Sheet.")
else:
    print("❌ Failed to connect.")