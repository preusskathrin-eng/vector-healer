import svgelements as se
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import sys
import os

def wkt_to_svg_d(shape):
    if shape.is_empty:
        return ""
    
   # 1. GEOMETRIC SIMPLIFICATION (The most important lever)
    # 0.3 is a good value: You can hardly see a difference, but it saves 40% points.
    shape = shape.simplify(0.3, preserve_topology=True)

    def get_path(poly):
        # 2. PRECISION REDUCTION: We round to 1 decimal place, which is more than enough for SVG rendering and reduces file size.
        def fmt(val): return f"{val:.1f}"
        
        coords = list(poly.exterior.coords)
        if not coords: return ""
        d = f"M {fmt(coords[0][0])},{fmt(coords[0][1])} "
        for x, y in coords[1:]:
            d += f"L {fmt(x)},{fmt(y)} "
        return d + "Z "

    if hasattr(shape, 'geoms'):
        return "".join([get_path(g) for g in shape.geoms])
    else:
        return get_path(shape)

def robust_merge(polygons):
    """Merges polygons incrementally and repairs topology errors."""
    if not polygons: return None
    
    try:
        u = unary_union(polygons)
        if u.is_valid: return u
    except:
        pass

    # If the quick fix fails: Incremental repair
    print("  -> Start incremental repair for this color group...")
    result = polygons[0].buffer(0)
    for i in range(1, len(polygons)):
        try:
            next_poly = polygons[i].buffer(0)
            result = result.union(next_poly)
        except:
            result = result.buffer(0.001).union(polygons[i].buffer(0.001))
    return result

def process_svg(input_path, output_path):
    print(f"--- Start process ---")
    svg = se.SVG.parse(input_path)
    
    color_groups = {}
    for el in svg.elements():
        if isinstance(el, se.Path):
            fill = el.fill.hex if el.fill else "None"
            if fill not in color_groups:
                color_groups[fill] = []
            color_groups[fill].append(el)

    final_data = []
    print(f"Colors to process: {len(color_groups)}")

    for color, paths in color_groups.items():
        if color == "None": continue
        print(f"Process {color} ({len(paths)} paths)...")
        
        polygons = []
        for p in paths:
            # Precision 6 for smooth curves (e.g. M4 Pro can handle this)
            points = [(seg.end.x, seg.end.y) for seg in p.segments(6)]
            if len(points) > 2:
                polygons.append(Polygon(points))
        
        if polygons:
            merged_geom = robust_merge(polygons)
            if merged_geom and not merged_geom.is_empty:
                d_attr = wkt_to_svg_d(merged_geom)
                if d_attr:
                    final_data.append({
                        'area': merged_geom.area,
                        'tag': f'<path d="{d_attr}" fill="{color}" stroke="none" />'
                    })

    # SORTING: Largest area first (background at the very bottom)
    final_data.sort(key=lambda x: x['area'], reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n')
        for item in final_data:
            f.write(f"  {item['tag']}\n")
        f.write('</svg>')
    
    print(f"--- Success! File saved: {output_path} ---")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_svg(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python3 04_web_distiller.py input.svg output.svg")
