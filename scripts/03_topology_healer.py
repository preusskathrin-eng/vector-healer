import svgelements as se
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union, orient
import sys
import os

def wkt_to_svg_d(shape, precision=2):
    """Converts geometry to SVG path data with adjustable precision."""
    if shape.is_empty:
        return ""
    
    def fmt(val): return f"{val:.{precision}f}".rstrip('0').rstrip('.')

    def get_path(poly):
        # Ensure exterior is CCW and interior is CW for proper SVG rendering
        poly = orient(poly, sign=1.0)
        coords = list(poly.exterior.coords)
        if not coords: return ""
        d = f"M {fmt(coords[0][0])},{fmt(coords[0][1])} "
        for x, y in coords[1:]:
            d += f"L {fmt(x)},{fmt(y)} "
        
        # Handle holes (interiors)
        for interior in poly.interiors:
            icoords = list(interior.coords)
            d += f"M {fmt(icoords[0][0])},{fmt(icoords[0][1])} "
            for ix, iy in icoords[1:]:
                d += f"L {fmt(ix)},{fmt(iy)} "
        return d + "Z "

    if hasattr(shape, 'geoms'):
        return "".join([get_path(g) for g in shape.geoms])
    else:
        return get_path(shape)

def robust_merge(polygons, color_code):
    """Merges polygons with error handling and topology repair."""
    if not polygons: return None
    
    # Step 1: Validate and repair individual polygons
    valid_polys = []
    for p in polygons:
        if p.is_valid:
            valid_polys.append(p)
        else:
            repaired = p.buffer(0)
            if not repaired.is_empty:
                valid_polys.append(repaired)

    try:
        # Step 2: Attempt standard union (fast)
        u = unary_union(valid_polys)
        # Apply microscopic dilation/erosion to close gaps
        return u.buffer(0.0001).buffer(-0.0001) 
    except Exception as e:
        print(f"  [!] Detailed repair needed for {color_code}: {e}")
        # Step 3: Incremental union for high-complexity areas (e.g., fur)
        result = valid_polys[0]
        for next_p in valid_polys[1:]:
            try:
                # Slight expansion prevents 'Side Location Conflicts'
                result = result.buffer(0.001).union(next_p.buffer(0.001)).buffer(-0.001)
            except:
                continue
        return result

def process_svg(input_path, output_path):
    print(f"\n--- Topology Healer: {os.path.basename(input_path)} ---")
    svg = se.SVG.parse(input_path)
    vb = f'viewBox="0 0 {svg.width} {svg.height}"' if svg.width else ""
    
    color_groups = {}
    for el in svg.elements():
        if isinstance(el, se.Path):
            fill = el.fill.hex if el.fill else "None"
            if fill not in color_groups: color_groups[fill] = []
            color_groups[fill].append(el)

    print(f"Processing {len(color_groups)} color groups...")
    final_data = []

    for color, paths in color_groups.items():
        if color == "None": continue
        
        polygons = []
        for p in paths:
            # High-res sampling (12 segments) for smooth details like eyes
            points = [(seg.end.x, seg.end.y) for seg in p.segments(12)]
            if len(points) > 2:
                polygons.append(Polygon(points))
        
        if polygons:
            merged_geom = robust_merge(polygons, color)
            
            if merged_geom and not merged_geom.is_empty:
                # THE LLAMA-EYE-FIX: Adaptive simplification
                # Keeps small details sharp while smoothing large background areas.
                tolerance = 0.01 if merged_geom.area < 40 else 0.1
                merged_geom = merged_geom.simplify(tolerance, preserve_topology=True)
                
                d_attr = wkt_to_svg_d(merged_geom, precision=2) 
                if d_attr:
                    final_data.append({
                        'area': merged_geom.area,
                        'tag': f'<path d="{d_attr}" fill="{color}" />'
                    })

    # Z-Order Sort: Largest area to back, smallest to front
    final_data.sort(key=lambda x: x['area'], reverse=True)
    print(f"Path reduction complete: {len(final_data)} optimized paths remaining.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" {vb}>\n')
        for item in final_data:
            f.write(f"  {item['tag']}\n")
        f.write('</svg>')
    print(f"--- Export successful: {output_path} ---\n")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_svg(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python 03_topology_healer.py input.svg output.svg")
