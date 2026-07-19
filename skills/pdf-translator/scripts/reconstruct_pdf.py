# /// script
# dependencies = [
#     "pymupdf>=1.22.0"
# ]
# ///

import os
import sys
import json
import argparse
import fitz

def unpack_color(color_int):
    r = ((color_int >> 16) & 255) / 255.0
    g = ((color_int >> 8) & 255) / 255.0
    b = (color_int & 255) / 255.0
    return (r, g, b)

def find_best_font_size(text, rect, fontname, start_size, min_size=6):
    font_size = start_size
    while font_size >= min_size:
        # Test on temporary doc
        tmp_doc = fitz.open()
        tmp_page = tmp_doc.new_page(width=rect.x1 + 100, height=rect.y1 + 100)
        res = tmp_page.insert_textbox(rect, text, fontsize=font_size, fontname=fontname)
        tmp_doc.close()
        
        if res >= 0:
            return font_size
        font_size -= 0.5
    return min_size

def reconstruct_pdf(pdf_path, json_path, output_pdf_path, target_lang="zh-CN", font_name=None):
    if not os.path.exists(pdf_path):
        print(f"Error: Original PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(json_path):
        print(f"Error: JSON layout file not found: {json_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(json_path, 'r', encoding='utf-8') as f:
        layout_data = json.load(f)
        
    doc = fitz.open(pdf_path)
    
    # Map target language to appropriate built-in CJK fonts if font_name is not specified
    if font_name is None:
        lang = target_lang.lower()
        if "zh-tw" in lang or "zh-hk" in lang or "zh-hant" in lang:
            font_name = "china-ts"
        elif "zh" in lang:
            font_name = "china-ss"
        elif "ja" in lang:
            font_name = "japan-ss"
        elif "ko" in lang:
            font_name = "korea-ss"
        else:
            font_name = "helv"
            
    print(f"Using font: {font_name} for translation mapping.")
    
    # Store translated blocks by page index
    translated_blocks = {}
    for page_data in layout_data.get("pages", []):
        p_idx = page_data["page_index"]
        translated_blocks[p_idx] = {b["block_id"]: b for b in page_data.get("blocks", [])}
        
    for page_idx, page in enumerate(doc):
        if page_idx not in translated_blocks:
            continue
            
        page_dict = translated_blocks[page_idx]
        
        for block_id, block in page_dict.items():
            bbox = block["bbox"]
            rect = fitz.Rect(bbox)
            
            # The text to write (use translation, fallback to original if missing)
            text = block.get("translated_text", block.get("text", ""))
            if not text:
                continue
                
            # 1. Erase original text by drawing a white rectangle
            # We use standard white (1, 1, 1).
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0, overlay=True)
            
            # 2. Extract style parameters
            orig_size = block.get("size", 10.0)
            orig_color_int = block.get("color", 0)
            text_color = unpack_color(orig_color_int)
            
            # 3. Find optimal font size that fits in the bounding box
            best_size = find_best_font_size(text, rect, font_name, orig_size)
            
            # 4. Insert translated text
            page.insert_textbox(rect, text, fontsize=best_size, fontname=font_name, color=text_color)
            
    doc.save(output_pdf_path)
    doc.close()
    print(f"Successfully reconstructed PDF saved to {output_pdf_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconstruct translated PDF using original and JSON layout.")
    parser.add_argument("pdf", help="Path to original input PDF file")
    parser.add_argument("json", help="Path to translated JSON file")
    parser.add_argument("output", help="Path to output PDF file")
    parser.add_argument("--lang", default="zh-CN", help="Target language (default: zh-CN)")
    parser.add_argument("--font", default=None, help="Custom font name (e.g. china-ss, helv)")
    args = parser.parse_args()
    
    reconstruct_pdf(args.pdf, args.json, args.output, args.lang, args.font)
