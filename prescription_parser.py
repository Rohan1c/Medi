# parser.py
import re
from typing import List, Dict

def parse_prescription_text(text: str) -> List[Dict[str, str]]:
    """
    Converts free-text prescription into structured list of dictionaries.
    Example input: "Paracetamol 500mg twice a day for 7 days; Ibuprofen 200mg once daily for 5 days"
    """
    items = text.split(";")  # split multiple prescriptions
    prescriptions = []
    
    for item in items:
        item = item.strip()
        if not item:
            continue
        
        # crude regex parsing
        match = re.match(r"(?P<medication>[a-zA-Z\s]+)\s(?P<dosage>\d+mg)\s(?P<frequency>.+?)\sfor\s(?P<duration>.+)", item)
        if match:
            prescriptions.append(match.groupdict())
        else:
            # fallback: store as medication only
            prescriptions.append({"medication": item, "dosage": "", "frequency": "", "duration": ""})
    
    return prescriptions
