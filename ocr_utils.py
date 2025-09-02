import pytesseract
from PIL import Image
import re

# If tesseract is not in PATH, set it explicitly:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path: str) -> str:
    """Extract raw text from a prescription image using OCR."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def parse_prescription(text: str):
    """
    Extract medicines and dosages from OCR text.
    Very basic regex parser for hackathon MVP.
    Example OCR line: "Paracetamol 500 mg"
    Returns: list of dicts [{name, dosage, unit}]
    """
    medicines = []
    pattern = re.compile(r"([A-Za-z]+)\s*(\d+)\s*(mg|ml|g)?", re.IGNORECASE)

    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            name, dosage, unit = match.groups()
            medicines.append({
                "name": name.capitalize(),
                "dosage": int(dosage),
                "unit": unit if unit else "mg"  
            })
    return medicines

# Example quick test
if __name__ == "__main__":
    text = extract_text_from_image("sample_prescription.jpg")
    print("OCR Output:", text)
    meds = parse_prescription(text)
    print("Parsed:", meds)
