# /// script
# dependencies = [
#     "pymupdf>=1.22.0",
#     "deep-translator>=1.11.4"
# ]
# ///

import os
import sys
import json
import subprocess
import fitz
from deep_translator import GoogleTranslator

def main():
    # 1. Create a dummy PDF with some text layout structures
    print("Step 1: Creating a multi-column styled dummy PDF...")
    doc = fitz.open()
    page = doc.new_page()
    
    # Draw block 1 (Left Column)
    rect1 = fitz.Rect(50, 50, 280, 200)
    text1 = (
        "Artificial Intelligence (AI) is transforming the world. "
        "Modern deep learning algorithms can process complex patterns "
        "and provide intelligent automation for many workflows."
    )
    page.draw_rect(rect1, color=(0.8, 0.8, 0.8), width=1) # Gray border
    page.insert_textbox(rect1, text1, fontsize=12, fontname="helv", color=(0.2, 0.2, 0.8)) # Blue text
    
    # Draw block 2 (Right Column)
    rect2 = fitz.Rect(300, 50, 530, 200)
    text2 = (
        "Preserving PDF layouts requires careful engineering. "
        "By measuring the dimensions of text bounding boxes and "
        "scaling the replacement CJK fonts, we ensure layout integrity."
    )
    page.draw_rect(rect2, color=(0.8, 0.8, 0.8), width=1) # Gray border
    page.insert_textbox(rect2, text2, fontsize=11, fontname="times-roman", color=(0.8, 0.2, 0.2)) # Red text
    
    dummy_pdf = "demo_dummy.pdf"
    doc.save(dummy_pdf)
    doc.close()
    print(f"Created dummy PDF: {dummy_pdf}")
    
    # 2. Extract layout to layout_raw.json
    print("\nStep 2: Extracting layout details...")
    raw_json = "layout_raw.json"
    subprocess.run([
        "python", "skills/pdf-translator/scripts/extract_layout.py",
        dummy_pdf, raw_json
    ], check=True)
    
    # 3. Simulate Agent Translation (Google Translate in this script)
    print("\nStep 3: Simulating translation of JSON contents...")
    with open(raw_json, "r", encoding="utf-8") as f:
        layout = json.load(f)
        
    translator = GoogleTranslator(source="en", target="zh-CN")
    
    for page_data in layout.get("pages", []):
        for block in page_data.get("blocks", []):
            original_text = block["text"]
            print(f"Translating: '{original_text[:30]}...'")
            translated = translator.translate(original_text)
            print(f"Result:      '{translated[:30]}...'")
            block["translated_text"] = translated
            
    translated_json = "layout_translated.json"
    with open(translated_json, "w", encoding="utf-8") as f:
        json.dump(layout, f, indent=2, ensure_ascii=False)
    print(f"Saved translated layout metadata to {translated_json}")
    
    # 4. Reconstruct PDF
    print("\nStep 4: Reconstructing the PDF with layout styling...")
    translated_pdf = "demo_translated.pdf"
    subprocess.run([
        "python", "skills/pdf-translator/scripts/reconstruct_pdf.py",
        dummy_pdf, translated_json, translated_pdf, "--lang", "zh-CN"
    ], check=True)
    
    print("\nDemo completed successfully!")
    print(f"Original PDF:      {os.path.abspath(dummy_pdf)}")
    print(f"Translated PDF:    {os.path.abspath(translated_pdf)}")
    
if __name__ == "__main__":
    main()
