# backend/parser.py
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from backend.models import ReceiptData
import os
from datetime import datetime

# Configure Tesseract and Poppler paths
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
POPPLER_PATH = r"C:/poppler/Library/bin"

KNOWN_VENDORS = ["Amazon", "Flipkart", "Reliance", "Big Bazaar", "Tata"]

def extract_text_from_file(file_path: str, filename: str) -> str:
    ext = filename.split('.')[-1].lower()
    text = ""

    if ext == 'pdf':
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        for image in images:
            image = image.convert("L")
            image = image.resize((1000, 1000))
            text += pytesseract.image_to_string(image, config='--psm 6')

    elif ext in ['jpg', 'png']:
        image = Image.open(file_path).convert("L")
        image = image.resize((1000, 1000))
        text = pytesseract.image_to_string(image, config='--psm 6')

    elif ext == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        print("📂 Raw TXT content:\n", text)  # ✅ Should print your file content

    print("📂 Raw TXT content:\n", text)
    return text

def extract_fields(text: str) -> dict:
    # Try to find vendor from known list
    vendor = next((v for v in KNOWN_VENDORS if v.lower() in text.lower()), "Unknown")

    # Match DD/MM/YYYY or DD-MM-YYYY
    date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)
    date = date_match.group(1).replace("/", "-") if date_match else datetime.today().strftime("%d-%m-%Y")

    # Match ₹, Rs, INR followed by amount
    amount_match = re.findall(r'(₹|Rs\.?|INR)?\s?(\d+[.,]?\d*)', text, re.IGNORECASE)
    print("💸 Amount matches:", amount_match)

    if amount_match:
        amount_str = amount_match[-1][1].replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0
    else:
        amount = 0.0

    fields = {
        "vendor": vendor,
        "date": date,
        "amount": amount,
        "category": vendor
    }

    print("🧾 Extracted Fields:", fields)
    return fields


def process_file(file_path: str, filename: str) -> dict:
    try:
        print(f"🚀 Processing file: {filename}")
        text = extract_text_from_file(file_path, filename)
        fields = extract_fields(text)
        validated = ReceiptData(**fields)
        return validated.dict()
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return None
