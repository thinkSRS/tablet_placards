#!/usr/bin/env python3
"""
Resize images to maximum width of 512px for faster web loading
Maintains aspect ratio and saves to lowres_images folder
"""

import os
from pathlib import Path
from PIL import Image

def resize_image(input_path, output_path, max_width=512):
    """
    Resize image if width > max_width, maintaining aspect ratio
    
    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        max_width: Maximum width in pixels (default: 512)
    """
    try:
        with Image.open(input_path) as img:
            original_width, original_height = img.size
            
            # Check if resize is needed
            if original_width <= max_width:
                print(f"✓ {input_path.name}: {original_width}x{original_height} - No resize needed")
                # Just copy the image
                img.save(output_path, quality=95, optimize=True)
                return False
            
            # Calculate new dimensions maintaining aspect ratio
            ratio = max_width / original_width
            new_width = max_width
            new_height = int(original_height * ratio)
            
            # Resize using high-quality Lanczos resampling
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            resized_img.save(output_path, quality=95, optimize=True)
            
            print(f"✓ {input_path.name}: {original_width}x{original_height} → {new_width}x{new_height}")
            return True
            
    except Exception as e:
        print(f"✗ Error processing {input_path.name}: {e}")
        return None

def main():
    """Process all images in the images folder"""
    # Setup paths
    script_dir = Path(__file__).parent
    images_dir = script_dir / "images"
    output_dir = script_dir / "lowres_images"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # Get all images
    image_files = [f for f in images_dir.glob('*') 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print("No images found in the images folder!")
        return
    
    print(f"Processing {len(image_files)} images from {images_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 70)
    
    # Process each image
    resized_count = 0
    copied_count = 0
    error_count = 0
    
    for image_file in sorted(image_files):
        output_file = output_dir / image_file.name
        result = resize_image(image_file, output_file)
        
        if result is True:
            resized_count += 1
        elif result is False:
            copied_count += 1
        else:
            error_count += 1
    
    # Summary
    print("-" * 70)
    print(f"\nSummary:")
    print(f"  Resized: {resized_count}")
    print(f"  Copied (no resize needed): {copied_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(image_files)}")
    print(f"\nLow-res images saved to: {output_dir}")

if __name__ == "__main__":
    main()
