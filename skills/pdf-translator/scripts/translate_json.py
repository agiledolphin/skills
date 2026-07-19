# /// script
# dependencies = [
#     "deep-translator>=1.11.4"
# ]
# ///

import os
import sys
import json
from deep_translator import GoogleTranslator

def translate_json(input_json, output_json, target_lang="zh-CN"):
    if not os.path.exists(input_json):
        print(f"Error: Input JSON not found: {input_json}", file=sys.stderr)
        sys.exit(1)
        
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Standardize language code for deep-translator
    lang_map = {
        "zh-cn": "zh-CN",
        "zh": "zh-CN",
        "zh-tw": "zh-TW",
        "ja": "ja",
        "ko": "ko"
    }
    tgt = lang_map.get(target_lang.lower(), target_lang)
    
    translator = GoogleTranslator(source="auto", target=tgt)
    
    pages = data.get("pages", [])
    total_pages = len(pages)
    
    print(f"Starting translation of {total_pages} pages into {tgt}...")
    
    # Track progress and translate
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        print(f"Processing Page {page_idx + 1}/{total_pages} (contains {len(blocks)} blocks)...")
        
        for block in blocks:
            text = block.get("text", "").strip()
            if not text:
                continue
                
            # If the text is purely numeric or special characters, skip translation
            if text.isdigit() or len(text) <= 1:
                block["translated_text"] = text
                continue
                
            try:
                translated = translator.translate(text)
                block["translated_text"] = translated
            except Exception as e:
                print(f"Warning: Failed to translate block {block.get('block_id')}: {e}")
                # Fallback to original text if translation fails
                block["translated_text"] = text
                
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nTranslation successfully saved to {output_json}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Translate text blocks inside a layout JSON file.")
    parser.add_argument("input", help="Path to input raw JSON layout file")
    parser.add_argument("output", help="Path to output translated JSON file")
    parser.add_argument("--lang", default="zh-CN", help="Target language (default: zh-CN)")
    args = parser.parse_args()
    
    translate_json(args.input, args.output, args.lang)
