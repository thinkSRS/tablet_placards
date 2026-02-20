#!/usr/bin/env python3
"""
Embed images as base64 data URIs in the HTML file
This creates a self-contained HTML file that works on Android tablets
"""

import base64
import os
import re
from pathlib import Path

def image_to_base64(image_path):
    """Convert image file to base64 data URI"""
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Determine MIME type from extension
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        mime_type = mime_types.get(ext, 'image/png')
        
        # Encode to base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
    except FileNotFoundError:
        print(f"Warning: Image not found: {image_path}")
        return None

def embed_images_in_html(html_file, output_file, images_dir='lowres_images'):
    """Read HTML and replace image src with base64 data URIs"""
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find all image references
    # Pattern 1: src="lowres_images/filename.ext"
    img_pattern = re.compile(r'src="lowres_images/([^"]+)"')
    
    def replace_image(match):
        filename = match.group(1)
        image_path = os.path.join(images_dir, filename)
        
        if os.path.exists(image_path):
            base64_uri = image_to_base64(image_path)
            if base64_uri:
                print(f"  ✓ Embedded: {filename}")
                return f'src="{base64_uri}"'
        else:
            print(f"  ✗ Not found: {filename}")
        
        return match.group(0)  # Return original if file not found
    
    # Replace all image sources
    print("Embedding product images...")
    html_content = img_pattern.sub(replace_image, html_content)
    
    # Handle the logo separately
    logo_pattern = re.compile(r'src="srs_logo_white\.png"')
    if os.path.exists('srs_logo_white.png'):
        logo_base64 = image_to_base64('srs_logo_white.png')
        if logo_base64:
            html_content = logo_pattern.sub(f'src="{logo_base64}"', html_content)
            print("  ✓ Embedded: srs_logo_white.png")
    else:
        print("  ✗ Logo not found: srs_logo_white.png")
    
    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✓ Created self-contained HTML: {output_file}")
    print(f"  File size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print("\nThis file can be copied directly to your Android tablet!")

def main():
    input_file = 'product_display.html'
    output_file = 'product_display_standalone.html'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        print("Make sure you run this script in the same directory as product_display.html")
        return
    
    embed_images_in_html(input_file, output_file)

if __name__ == '__main__':
    main()
