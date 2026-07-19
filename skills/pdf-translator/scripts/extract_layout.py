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

def extract_layout(pdf_path, output_json_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
        
    doc = fitz.open(pdf_path)
    data = {
        "pdf_path": os.path.abspath(pdf_path),
        "pages": []
    }
    
    for page_idx, page in enumerate(doc):
        page_data = {
            "page_index": page_idx,
            "width": page.rect.width,
            "height": page.rect.height,
            "blocks": []
        }
        
        # Extract text blocks as a dictionary
        text_dict = page.get_text("dict")
        block_idx = 0
        
        for block in text_dict.get("blocks", []):
            # Only process text blocks (type 0)
            if block.get("type") != 0:
                continue
                
            # Collect lines and spans
            lines_data = []
            block_text = []
            
            # We want to identify the dominant font properties of this block
            span_fonts = {}
            span_sizes = {}
            span_colors = {}
            
            for line in block.get("lines", []):
                line_text = []
                for span in line.get("spans", []):
                    txt = span.get("text", "")
                    line_text.append(txt)
                    
                    font = span.get("font", "helv")
                    size = span.get("size", 10.0)
                    color = span.get("color", 0)
                    
                    span_fonts[font] = span_fonts.get(font, 0) + len(txt)
                    span_sizes[size] = span_sizes.get(size, 0) + len(txt)
                    span_colors[color] = span_colors.get(color, 0) + len(txt)
                    
                full_line_text = "".join(line_text)
                block_text.append(full_line_text)
                
            full_block_text = "\n".join(block_text).strip()
            
            # Skip empty blocks
            if not full_block_text:
                continue
                
            # Find dominant styling
            dominant_font = max(span_fonts, key=span_fonts.get) if span_fonts else "helv"
            dominant_size = max(span_sizes, key=span_sizes.get) if span_sizes else 10.0
            dominant_color = max(span_colors, key=span_colors.get) if span_colors else 0
            
            page_data["blocks"].append({
                "block_id": f"p{page_idx}_b{block_idx}",
                "bbox": block.get("bbox"),  # [x0, y0, x1, y1]
                "text": full_block_text,
                "font": dominant_font,
                "size": dominant_size,
                "color": dominant_color,
            })
            block_idx += 1
            
        data["pages"].append(page_data)
        
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully extracted layout of {pdf_path} to {output_json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text blocks and layout details from PDF.")
    parser.add_argument("pdf", help="Path to input PDF file")
    parser.add_argument("output", help="Path to output JSON layout file")
    args = parser.parse_args()
    
    extract_layout(args.pdf, args.output)
