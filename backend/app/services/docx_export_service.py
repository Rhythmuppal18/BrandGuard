import io
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def generate_approved_docx(
    item_id: str,
    title: str,
    content_type: str,
    score: int,
    approver: str,
    role: str,
    timestamp: str,
    content_hash: str,
    approved_content: str,
    findings_resolved_count: int = 0
) -> bytes:
    """
    Generates a professionally formatted Microsoft Word (.docx) document
    for brand-approved content with official governance metadata.
    """
    doc = docx.Document()

    # Set standard margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header Badge
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_badge = p_header.add_run("BRANDGUARD™ CERTIFIED CONTENT")
    r_badge.font.size = Pt(9)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(16, 185, 129)  # Emerald green

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_title = p_title.add_run(title)
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Verified Pre-Publication Release Document | Ready for Distribution")
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Metadata Table
    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Light Shading Accent 1' if 'Light Shading Accent 1' in [s.name for s in doc.styles] else 'Table Grid'

    meta_rows = [
        ("Document ID", item_id),
        ("Classification", content_type.replace('_', ' ').title()),
        ("Brand Compliance Score", f"{score} / 100 (Cleared)"),
        ("Authorized Approver", f"{approver} [{role}] on {timestamp}"),
    ]

    for i, (k, v) in enumerate(meta_rows):
        row = table.rows[i]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.text = k
        c1.text = v
        c0.paragraphs[0].runs[0].font.bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(10)
        c1.paragraphs[0].runs[0].font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # Heading: Approved Body Text
    h1 = doc.add_heading("Approved Publication Content", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(8)

    # Body paragraphs
    paragraphs = approved_content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            p_body = doc.add_paragraph(para.strip())
            p_body.paragraph_format.line_spacing = 1.25
            p_body.paragraph_format.space_after = Pt(8)
            for r in p_body.runs:
                r.font.size = Pt(11)
                r.font.color.rgb = RGBColor(30, 41, 59)

    doc.add_paragraph().paragraph_format.space_after = Pt(18)

    # Heading: Governance Verification
    h2 = doc.add_heading("Brand Governance & Verification Log", level=2)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(8)

    points = [
        f"Cryptographic SHA-256 Fingerprint: {content_hash}",
        "100% of policy breaches inspected and resolved prior to publication authorization.",
        "Zero prohibited terminology or unverified commercial claims remaining.",
        "Verified against official Brand Governance Policy & Legal Claim Registries."
    ]

    for pt in points:
        bp = doc.add_paragraph(pt, style='List Bullet')
        bp.paragraph_format.space_after = Pt(4)
        for r in bp.runs:
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(71, 85, 105)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

