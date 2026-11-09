import sys
from pathlib import Path
import fitz
import docx

def create_samples():
    out_dir = Path("sample_documents")
    out_dir.mkdir(exist_ok=True)

    # 1. Plain Text Sample
    txt_path = out_dir / "sample_1_marketing_launch.txt"
    txt_content = (
        "ApexPay is officially the best in India! 🔥 We guarantee 100% uptime guaranteed for all our customers, bro. "
        "Get our cheap starter pack with a flat 50% discount on Enterprise annual plan today! No questions asked."
    )
    txt_path.write_text(txt_content, encoding="utf-8")
    print(f"Created: {txt_path}")

    # 2. Word DOCX Sample: Bereavement Policy (Air Canada Case Replica)
    doc = docx.Document()
    doc.add_heading("ApexPay Customer Service Notice: Bereavement & Refund Policy", level=1)
    doc.add_paragraph("Policy ID: POL-2025-08 | Applicable to all regional branches")
    doc.add_paragraph(
        "To all customers filing bereavement fare or exception requests: don't worry lol, our system offers an "
        "unlimited refund with no questions asked! Just message support for your risk-free payout."
    )
    doc.add_paragraph(
        "Our customers love our cheap services and quick hacks to get reimbursed faster."
    )
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Tier"
    hdr_cells[1].text = "Refund Window"
    hdr_cells[2].text = "Guarantee"
    row_cells = table.add_row().cells
    row_cells[0].text = "Standard Customer"
    row_cells[1].text = "Unlimited"
    row_cells[2].text = "100% Guaranteed"
    
    docx_path = out_dir / "sample_2_bereavement_policy.docx"
    doc.save(str(docx_path))
    print(f"Created: {docx_path}")

    # 3. PDF Sample: Cloud Infrastructure Announcement
    pdf_doc = fitz.open()
    page = pdf_doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(50, 60), "ApexPay Cloud Architecture & Performance Briefing", fontsize=16, fontname="hebo", color=(0.1, 0.2, 0.4))
    page.insert_text(fitz.Point(50, 85), "Official Press Release — Q4 Technical Operations", fontsize=10, fontname="helv", color=(0.4, 0.4, 0.5))
    page.draw_line(fitz.Point(50, 95), fitz.Point(545, 95), color=(0.8, 0.8, 0.8), width=1)

    body_text = (
        "ApexPay announced today that it has built the world's most bulletproof financial cloud. "
        "We deliver 100% uptime guaranteed, beating every competitor. Our customers can now execute "
        "high speed hacks to maximize yield.\n\n"
        "All customers get a flat 50% discount on Enterprise annual plan today only. Don't be stupid! "
        "Buy our plan right now before prices skyrocket tomorrow!"
    )
    
    y = 120
    for line in body_text.split("\n"):
        if line.strip():
            page.insert_text(fitz.Point(50, y), line, fontsize=10, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 20
        else:
            y += 10
            
    pdf_path = out_dir / "sample_3_cloud_infrastructure.pdf"
    pdf_doc.save(str(pdf_path))
    pdf_doc.close()
    print(f"Created: {pdf_path}")

    # 4. Compliant DOCX Sample
    doc_comp = docx.Document()
    doc_comp.add_heading("ApexPay Global: Compliant Quarterly Governance Briefing", level=1)
    doc_comp.add_paragraph(
        "ApexPay is proud to announce another record quarter. ApexPay processes over 50 million transactions monthly "
        "with 99.99% high-availability SLA. As certified PCI-DSS Level 1 Service Provider and ISO/IEC 27001:2022 audited, "
        "we continue to empower our members worldwide with enterprise-grade infrastructure and dedicated concierge support."
    )
    doc_comp.add_paragraph(
        "New partners receive zero transaction processing fees for the first 30 days on Starter tier under our verified commercial terms."
    )
    docx_comp_path = out_dir / "sample_4_compliant_announcement.docx"
    doc_comp.save(str(docx_comp_path))
    print(f"Created: {docx_comp_path}")

if __name__ == "__main__":
    create_samples()
