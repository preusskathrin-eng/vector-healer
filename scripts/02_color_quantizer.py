import re
import os
import sys

def quantize_color(hex_color, step=32):
    """
    Calculates the nearest 'grid color' for a hex value.
    Rounding to fixed intervals eliminates micro-nuances.
    """
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB components
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Quantization: Rounding to the center of the interval.
    # Prevents colors from turning 'black' if they are just below the step value.
    q_r = min(255, (r // step) * step + (step // 2))
    q_g = min(255, (g // step) * step + (step // 2))
    q_b = min(255, (b // step) * step + (step // 2))
    
    return f"#{q_r:02x}{q_g:02x}{q_b:02x}"

def process_svg(input_path, output_path, step=16):
    """
    Reads an SVG file as text, identifies all hex color codes,
    and replaces them with their quantized equivalents.
    """
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    print(f"--- Color Quantization: {os.path.basename(input_path)} ---")
    
    with open(input_path, "r", encoding="utf-8") as f:
        svg_data = f.read()

    # Find all 6-digit hex colors (matches #ffffff etc.)
    found_colors = set(re.findall(r'#[0-9a-fA-F]{6}', svg_data))
    
    # Create mapping table: Original -> New Quantized Color
    color_map = {c: quantize_color(c, step) for c in found_colors}
    
    # Iterate through the XML content and replace colors
    for original, replacement in color_map.items():
        svg_data = svg_data.replace(original, replacement)
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_data)
    
    reduced_count = len(set(color_map.values()))
    print(f"Input:  {len(found_colors)} unique nuances")
    print(f"Output: {reduced_count} clean colors (Step size: {step})")
    print(f"Success: Quantized SVG saved to {output_path}\n")

if __name__ == "__main__":
    # Usage via command line or default values
    if len(sys.argv) > 2:
        process_svg(sys.argv[1], sys.argv[2], step=16)
    else:
        # Generic placeholders for GitHub repository
        INPUT_FILE = "input_vectorized.svg"
        OUTPUT_FILE = "output_quantized.svg"
        process_svg(INPUT_FILE, OUTPUT_FILE, step=16)
