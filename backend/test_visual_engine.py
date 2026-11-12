import io
from PIL import Image, ImageDraw
from app.services.visual_engine import (
    hex_to_rgb, rgb_to_hex, rgb_to_lab, ciede2000,
    calculate_contrast_ratio, extract_dominant_colors,
    evaluate_palette_compliance, analyze_logo_geometry,
    evaluate_wcag_contrast, inspect_visual_asset
)

def test_ciede2000_mathematics():
    print("Testing CIEDE2000 Color Difference...")
    # Identical colors
    lab_cyan1 = rgb_to_lab(6, 182, 212)
    lab_cyan2 = rgb_to_lab(6, 182, 212)
    de_zero = ciede2000(lab_cyan1, lab_cyan2)
    assert de_zero == 0.0, f"Expected 0.0, got {de_zero}"

    # Very close shade (slight tint)
    lab_cyan_close = rgb_to_lab(10, 185, 215)
    de_close = ciede2000(lab_cyan1, lab_cyan_close)
    assert 0.1 <= de_close <= 2.0, f"Expected minor tolerance, got {de_close}"

    # Vastly different colors: Cyan vs Stark Red
    lab_red = rgb_to_lab(244, 63, 94)
    de_far = ciede2000(lab_cyan1, lab_red)
    assert de_far > 30.0, f"Expected large delta E, got {de_far}"
    print(f"  ✓ Zero distance: {de_zero}, Close delta: {de_close}, Opposing delta: {de_far}")

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

def test_synthetic_image_inspection():
    print("Testing Full Visual Inspection Pipeline on Synthetic Asset...")
    # Create synthetic test graphic: 600x600 square banner with brand cyan background & white emblem
    img = Image.new("RGB", (600, 600), color=(5, 8, 17))
    draw = ImageDraw.Draw(img)
    # Draw central emblem in brand cyan (#06B6D4)
    draw.rectangle([150, 150, 450, 450], fill=(6, 182, 212))
    # Draw stark white typography text box
    draw.rectangle([250, 250, 350, 350], fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    result = inspect_visual_asset(raw_bytes, "test_banner.png", target_logo_aspect=1.0)
    assert result["overall_visual_score"] >= 80, f"Expected score >= 80, got {result['overall_visual_score']}"
    assert result["logo_geometry"]["aspect_ratio_compliant"] is True
    assert len(result["extracted_dominant_colors"]) >= 3
    print(f"  ✓ Synthetic Banner Overall Score: {result['overall_visual_score']}/100")
    print(f"  ✓ Clearance Status: {result['clearance_status']}")
    print(f"  ✓ Dominant colors extracted: {[c['hex'] for c in result['extracted_dominant_colors']]}")

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
    test_ciede2000_mathematics()
    test_wcag_contrast_ratios()
    test_synthetic_image_inspection()
    test_corrupted_file_handling()
    print("========================================")
    print(" ALL PILLAR 1 VISUAL ENGINE TESTS PASSED!")
    print("========================================")

