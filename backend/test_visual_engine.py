import io
from PIL import Image, ImageDraw
from app.services.visual_engine import (
    hex_to_rgb, rgb_to_hex, rgb_to_lab, ciede2000,
    calculate_contrast_ratio, extract_dominant_colors,
    evaluate_palette_compliance, analyze_logo_geometry,
    evaluate_wcag_contrast, inspect_visual_asset, parse_svg_asset
)

def test_ciede2000_sharma_reference_vectors():
    print("Testing CIEDE2000 against published Sharma 2005 Reference Vectors...")
    # Reference Pair 1 from Sharma et al. (2005) Table 4:
    # Lab1 = [50.0, 2.6772, -79.7751], Lab2 = [50.0, 0.0000, -82.7485] -> Expected ΔE00 = 2.0425
    lab1 = (50.0, 2.6772, -79.7751)
    lab2 = (50.0, 0.0000, -82.7485)
    de1 = ciede2000(lab1, lab2)
    assert abs(de1 - 2.0425) < 0.05, f"Pair 1 failed: got {de1}, expected 2.0425"

    # Reference Pair 2:
    # Lab1 = [50.0, 3.1571, -77.2803], Lab2 = [50.0, 0.0000, -82.7485] -> Expected ΔE00 = 2.8615
    lab3 = (50.0, 3.1571, -77.2803)
    de2 = ciede2000(lab3, lab2)
    assert abs(de2 - 2.8615) < 0.05, f"Pair 2 failed: got {de2}, expected 2.8615"

    # Reference Pair 3:
    # Lab1 = [50.0, 2.8361, -74.0200], Lab2 = [50.0, 0.0000, -82.7485] -> Expected ΔE00 = 3.4412
    lab4 = (50.0, 2.8361, -74.0200)
    de3 = ciede2000(lab4, lab2)
    assert abs(de3 - 3.4412) < 0.05, f"Pair 3 failed: got {de3}, expected 3.4412"

    print(f"  ✓ Sharma Vector 1: {de1} (Expected: 2.0425)")
    print(f"  ✓ Sharma Vector 2: {de2} (Expected: 2.8615)")
    print(f"  ✓ Sharma Vector 3: {de3} (Expected: 3.4412)")

def test_wcag_contrast_ratios():
    print("Testing WCAG 2.1 Contrast Calculations...")
    # Black on White: 21.0:1
    ratio_max = calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
    assert ratio_max == 21.0, f"Expected 21.0, got {ratio_max}"

    # White on Deep Navy (#050811): Should pass AAA (>= 7.0)
    ratio_navy = calculate_contrast_ratio((255, 255, 255), (5, 8, 17))
    assert ratio_navy >= 15.0, f"Expected >= 15.0, got {ratio_navy}"

    # Low contrast: Dark gray on Black
    ratio_low = calculate_contrast_ratio((40, 40, 40), (0, 0, 0))
    assert ratio_low < 3.0, f"Expected < 3.0, got {ratio_low}"
    print(f"  ✓ Max ratio: {ratio_max}:1, Brand text ratio: {ratio_navy}:1, Low ratio: {ratio_low}:1")

def test_logo_boundary_and_clear_space():
    print("Testing Geometric Logo Boundary & Clear Space Detection...")
    # Create an image with an off-center logo touching the left border (clear space violation)
    img_encroached = Image.new("RGB", (400, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img_encroached)
    # Draw logo at x=2, y=50 (encroaches left margin, min_margin = 2px)
    draw.rectangle([2, 50, 200, 250], fill=(37, 99, 235))

    geom_fail = analyze_logo_geometry(img_encroached, target_aspect_ratio=1.0, required_clear_space_pct=10.0)
    assert geom_fail["clear_space_compliant"] is False
    assert geom_fail["minimum_margin_px"] <= 2
    print(f"  ✓ Correctly flagged clear-space encroachment: {geom_fail['minimum_margin_px']}px < {geom_fail['required_margin_px']}px")

    # Create an image with centered logo and ample safe padding
    img_safe = Image.new("RGB", (400, 400), color=(255, 255, 255))
    draw_safe = ImageDraw.Draw(img_safe)
    draw_safe.rectangle([100, 100, 300, 300], fill=(37, 99, 235))

    geom_pass = analyze_logo_geometry(img_safe, target_aspect_ratio=1.0, required_clear_space_pct=10.0)
    assert geom_pass["clear_space_compliant"] is True
    assert geom_pass["minimum_margin_px"] >= 90
    print(f"  ✓ Verified safe-space margin: {geom_pass['minimum_margin_px']}px >= {geom_pass['required_margin_px']}px")

def test_svg_vector_asset_support():
    print("Testing Native SVG Vector Asset Ingestion & WCAG Validation...")
    svg_sample = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 300" width="500" height="300">
      <rect width="500" height="300" fill="#050811"/>
      <circle cx="150" cy="150" r="80" fill="#3B82F6"/>
      <text x="320" y="160" font-size="24" fill="#06B6D4">APEXPAY CLOUD</text>
    </svg>"""

    result = inspect_visual_asset(svg_sample.encode("utf-8"), "banner.svg", target_logo_aspect=None)
    assert result["format"] == "SVG"
    assert result["dimensions"]["width"] == 500
    assert result["dimensions"]["height"] == 300
    assert len(result["extracted_dominant_colors"]) >= 2
    assert result["wcag_accessibility"]["status"] == "PASS"
    print(f"  ✓ SVG Vector Inspection Successful: Format={result['format']}, Score={result['overall_visual_score']}")
    print(f"  ✓ Detected Colors: {[c['hex'] for c in result['extracted_dominant_colors']]}")

def test_corrupted_file_handling():
    print("Testing Corrupted Asset Validation...")
    corrupted_bytes = b"NOT_AN_IMAGE_RANDOM_GARBAGE_BYTES_12345"
    try:
        inspect_visual_asset(corrupted_bytes, "corrupt.png")
        assert False, "Should have raised ValueError on corrupted file"
    except ValueError as e:
        print(f"  ✓ Caught expected error gracefully: {str(e)[:50]}...")

if __name__ == "__main__":
    print("========================================")
    print(" RUNNING PILLAR 1 VISUAL ENGINE TESTS   ")
    print("========================================")
    test_ciede2000_sharma_reference_vectors()
    test_wcag_contrast_ratios()
    test_logo_boundary_and_clear_space()
    test_svg_vector_asset_support()
    test_corrupted_file_handling()
    print("========================================")
    print(" ALL PILLAR 1 VISUAL ENGINE TESTS PASSED!")
    print("========================================")
