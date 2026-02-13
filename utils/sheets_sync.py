# utils/sheets_sync.py
import gspread
from google.oauth2.service_account import Credentials

# 1. Setup the connection logic
def get_panini_sheet():
    # Replace with your actual Spreadsheet ID from the URL
    SHEET_ID = "1bU-09jKj_uIb_oz12Kx6VOEQ_ZxGZNqkx2ILX-UT3b0" 
    
    # Define the scope for Google Drive and Sheets
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Load your secret service account file
    creds = Credentials.from_service_account_file("service_account.json", scopes=scopes)
    client = gspread.authorize(creds)
    
    # Open the sheet and return the first worksheet
    return client.open_by_key(SHEET_ID).sheet1

# 2. Add a function to write new sugar logs
def log_sugar_entry(data_row):
    sheet = get_panini_sheet()
    sheet.append_row(data_row)
    return True