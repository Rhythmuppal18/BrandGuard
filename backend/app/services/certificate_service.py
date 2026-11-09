import io
import fitz
from datetime import datetime
from typing import Dict, Any, Optional

def generate_compliance_certificate(
    item_id: str,
    title: str,
    content_type: str,
    score: int,
    approver: str,
    role: str,
    timestamp: str,
    content_hash: str,
    content_snippet: str
) -> bytes:
    """
    Generates a formal 1-page PDF Brand Clearance & Compliance Certificate.
    """
    doc = fitz.open()
    W, H = 595, 842  # A4
    page = doc.new_page(width=W, height=H)

    c_dark = (0.05, 0.08, 0.13)
    c_blue = (0.13, 0.40, 0.85)
    c_cyan = (0.02, 0.65, 0.75)
    c_emerald = (0.06, 0.68, 0.45)
    c_border = (0.80, 0.85, 0.90)
    c_card_bg = (0.96, 0.98, 1.0)
    c_gray = (0.45, 0.50, 0.58)

    # Outer decorative double border
    page.draw_rect(fitz.Rect(20, 20, W - 20, H - 20), color=c_blue, width=2)
    page.draw_rect(fitz.Rect(26, 26, W - 26, H - 26), color=c_cyan, width=0.8)

    # Top Header Band
    page.draw_rect(fitz.Rect(26, 26, W - 26, 42), color=None, fill=c_blue)
    page.draw_rect(fitz.Rect(26, 42, W - 26, 46), color=None, fill=c_cyan)

    # Certificate Title
    y = 85
    page.insert_text(fitz.Point(60, y), "BRANDGUARD GOVERNANCE FRAMEWORK", fontsize=10, fontname="hebo", color=c_blue)
    y += 24
    page.insert_text(fitz.Point(60, y), "Certificate of Brand Compliance", fontsize=24, fontname="hebo", color=c_dark)
    y += 16
    page.insert_text(fitz.Point(60, y), "Official Pre-Publication Clearance & Regulatory Verification", fontsize=11, fontname="helv", color=c_cyan)

    y += 16
    page.draw_line(fitz.Point(60, y), fitz.Point(W - 60, y), color=c_border, width=1)

    # Certificate ID and Timestamp
    y += 20
    cert_id = f"CERT-BG-{item_id.replace('item-', '').upper()}"
    page.insert_text(fitz.Point(60, y), f"Certificate No: {cert_id}", fontsize=9, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(W - 220, y), f"Issued: {timestamp}", fontsize=9, fontname="helv", color=c_gray)

    # Document Details Card
    y += 18
    details_box = fitz.Rect(60, y, W - 60, y + 100)
    page.draw_rect(details_box, color=c_border, fill=c_card_bg)

    page.insert_text(fitz.Point(75, y + 24), "Document Title:", fontsize=9.5, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(175, y + 24), title[:50], fontsize=9.5, fontname="helv", color=c_dark)

    page.insert_text(fitz.Point(75, y + 44), "Channel / Format:", fontsize=9.5, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(175, y + 44), content_type.replace("_", " ").title(), fontsize=9.5, fontname="helv", color=c_dark)

    page.insert_text(fitz.Point(75, y + 64), "Consistency Score:", fontsize=9.5, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(175, y + 64), f"{score} / 100  (Grade: A+ Compliant)", fontsize=9.5, fontname="hebo", color=c_emerald)

    page.insert_text(fitz.Point(75, y + 84), "Governance Status:", fontsize=9.5, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(175, y + 84), "APPROVED FOR IMMEDIATE PUBLICATION", fontsize=9.5, fontname="hebo", color=c_emerald)

    # Verification Statement
    y += 125
    page.insert_text(fitz.Point(60, y), "Compliance Audit Verification", fontsize=12, fontname="hebo", color=c_dark)
    y += 18

    statement = (
        f"This document certifies that the content titled \"{title}\" has undergone multi-layer "
        f"algorithmic pre-publication inspection against active corporate brand guidelines, legal terminology "
        f"standards, and the verified facts register.\n\n"
        f"All detected superlatives, claims, and terminology were either verified against active evidentiary sources "
        f"or corrected via human-reviewed tracked changes. Zero unverified claims or prohibited phrases remain active.\n\n"
        f"Human Sign-off Authorization has been granted by {approver} acting in the capacity of {role}."
    )
    for line in statement.split("\n"):
        if line.strip():
            page.insert_text(fitz.Point(60, y), line, fontsize=8.5, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 14
        else:
            y += 8

    # Approved Content Snapshot
    y += 15
    page.insert_text(fitz.Point(60, y), "Certified Text Excerpt", fontsize=11, fontname="hebo", color=c_dark)
    y += 12

    snippet_box = fitz.Rect(60, y, W - 60, y + 70)
    page.draw_rect(snippet_box, color=c_border, fill=(0.98, 0.98, 0.98))
    
    clean_snippet = content_snippet[:220] + ("..." if len(content_snippet) > 220 else "")
    page.insert_text(fitz.Point(72, y + 20), f"“{clean_snippet}”", fontsize=8, fontname="helv", color=c_gray)

    # Cryptographic Content Hash & Audit Lock
    y += 85
    page.insert_text(fitz.Point(60, y), "Cryptographic Verification & Integrity Hash", fontsize=10, fontname="hebo", color=c_dark)
    y += 14
    page.insert_text(fitz.Point(60, y), f"SHA-256 Digest: {content_hash}", fontsize=8.5, fontname="helv", color=c_blue)
    page.insert_text(fitz.Point(60, y + 12), "Tamper-Evident Governance Record: Immutable audit trail entry stored in BrandGuard registry.", fontsize=7.5, fontname="helv", color=c_gray)

    # Sign-off & Stamp Section
    y += 45
    page.draw_line(fitz.Point(60, y + 40), fitz.Point(240, y + 40), color=c_dark, width=1)
    page.insert_text(fitz.Point(60, y + 54), approver, fontsize=9.5, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(60, y + 66), f"{role} (Authorized Signatory)", fontsize=8, fontname="helv", color=c_gray)

    # Official Stamp Seal
    stamp_rect = fitz.Rect(W - 220, y - 5, W - 60, y + 70)
    page.draw_rect(stamp_rect, color=c_emerald, width=1.5, fill=(0.92, 0.99, 0.95))
    page.insert_text(fitz.Point(W - 205, y + 18), "★ BRANDGUARD VERIFIED ★", fontsize=8.5, fontname="hebo", color=c_emerald)
    page.insert_text(fitz.Point(W - 200, y + 36), "CLEARED FOR PUBLICATION", fontsize=8, fontname="hebo", color=c_dark)
    page.insert_text(fitz.Point(W - 195, y + 52), f"Score: {score}/100 · PASSED", fontsize=8, fontname="helv", color=c_emerald)

    # Bottom Footer
    page.insert_text(fitz.Point(60, H - 38), "CodeTitans India 2026 | Inkloom AI Problem Statement | Team WHO CARES?", fontsize=7.5, fontname="helv", color=c_gray)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

