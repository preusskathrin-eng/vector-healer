# VectorHealer: AI-SVG Optimization Pipeline

### FROM 17,000 PATHS TO WEB-READY PRECISION

> **The Problem:** AI vectorizers often create "Path Chaos" — thousands of tiny, overlapping fragments, inconsistent colors, and massive file sizes (10MB+).
> **The Solution:** A 5-stage pipeline that uses color quantization and Shapely-based topology healing to reduce file size by up to 90% while maintaining visual integrity.

-----

## 🛠 THE 5-STAGE PIPELINE

### 01 | Raw Vectorization

Uses `vtracer` to convert `bird.png` into a high-detail SVG.

  * **Output:** `bird_vectorized.svg` (\~10MB)


### 02 | Color Quantization

Reduces 2,500+ nuances into a clean palette (e.g., 64-256 colors). This is the **Enabler** for merging paths.

  * **Output:** `bird_colors_merged.svg`
    

### 03 | Topology Healing (The Core)

Uses the Mac M4 Pro's power to merge adjacent polygons of the same color into solid shapes using `Shapely`.

  * **Output:** `bird_paths_merged.svg`
    
  

### 04 | Web Distillation

Douglas-Peucker simplification and coordinate rounding.

  * **Output:** `bird_web-optimized.svg` (\< 700KB)

-----

## 📈 VISUAL PROGRESSION

| Stage | Visual Result | File Size | Path Count |
| :--- | :--- | :--- | :--- |
| **Original** | <img src="examples/bird.png" alt="original picture" width="300"> | 2.23 MB | - |
| **Raw Vector** | <img src="examples/README_previews/bird_vectorized.png" alt="Bird vectorized with Python" width="300"> | 10.2 MB | 17,164 |
| **Quantized** | <img src="examples/README_previews/bird_colors_merged.png" alt="Bird after quantization" width="300"> | 10.2 MB | 17,164 |
| **Healed** | <img src="examples/README_previews/bird_paths_merged.png" alt="Bird with merged paths" width="300"> | 3.06 MB | 1,352 |
| **Optimized** | <img src="examples/README_previews/bird_web-optimized.png" alt="Optimized Bird" width="300"> | **667 KB** | **81** |

-----

## 🔧 FINE-TUNING & TROUBLESHOOTING

**"The result looks too blocky/abstract"**

  * Increase the `step` size in `02_color_quantizer.py` (e.g., from 16 to 8).
  * Reduce `simplify` tolerance in `03_topology_healer.py` (e.g., to 0.05).

**"Small details (eyes) are disappearing"**

  * Check the "Smart Simplify" logic in Script 03. Ensure the `area < 40` threshold is active to protect small polygons.

-----

---

### ⚠️ Design Suitability Note

> ### 🛑 Disclaimer: Design Suitability
> Please note that not all AI-generated designs are suitable for radical web distillation (Stage 04/05).
> 
> * **Ideal:** High-contrast shapes, flat illustrations, logos, and clear silhouettes (e.g., the Bird). These can be reduced by up to 95%.
> * **Challenging:** Fur textures, complex lighting particles, or hyper-detailed gradients (e.g., the Llama). 
> 
> **The Reason:** Extreme detail density can cause "polygon bleeding" (diagonal artifacts) during coordinate rounding. If your design "breaks" in the final stage, we recommend using the output from **Stage 03 (Topology Healed)**. It offers a professional, merged path structure while preserving the micro-details required for complex subjects.

---
