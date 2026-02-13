# main.py
from fastapi import FastAPI, Request, Response
from core.titration import GDMEngine
from utils.parser import parse_message
from utils.sheets_sync import get_sheet_connection, log_entry
import datetime

app = FastAPI()
engine = GDMEngine() # The Brain

@app.get("/webhook")
async def verify(request: Request):
    # Meta Verification logic
    params = request.query_params
    return Response(content=params.get("hub.challenge"), media_type="text/plain")

@app.post("/webhook")
async def handle_message(request: Request):
    data = await request.json()
    # Extract phone and text...
    text = "G145" # Placeholder for extracted text
    
    # 1. Parse using Heuristics (<30 vs >=30)
    parsed = parse_message(text) 
    
    # 2. If Sugar, run Titration
    if parsed['type'] == 'sugar':
        # Retrieve last dose from Sheet...
        suggestion, note = engine.get_bolus_suggestion(parsed['value'], 8) # Example
        
        # 3. Log to Google Sheet
        row = ["Patient_1", str(datetime.datetime.now()), "71", parsed['label'], 
               parsed['value'], suggestion, "", "False", "1", "None", note]
        log_entry(row) # The Foundation
        
    return {"status": "success"}