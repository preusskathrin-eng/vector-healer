import vtracer
import sys

def run_vectorization(input_path, output_path):
    print(f"Phase 1: Extracting high-detail vectors from {input_path}...")
    
    # Advanced settings for maximum detail retention
    vtracer.convert_image_to_svg_py(
        input_path, 
        output_path,
        mode='spline',
        colormode='color',
        hierarchical='stacked',
        color_precision=8,
        layer_difference=8,
        filter_speckle=4,
        path_precision=4,
        corner_threshold=30,
        length_threshold=3.0
    )
    print(f"Done. Raw SVG saved to {output_path}")

if __name__ == "__main__":
    run_vectorization("input.jpg", "01_raw_output.svg")
