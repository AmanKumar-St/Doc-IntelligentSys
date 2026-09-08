from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_sample_docs():
    output_dir = Path("data/uploads")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create DOCX: Employee Handbook
    docx_path = output_dir / "employee_handbook.docx"
    doc = Document()
    doc.add_heading("Apex Global Enterprise - Employee Handbook 2026", level=0)
    
    doc.add_heading("1. Paid Time Off and Leave Policy", level=1)
    doc.add_paragraph(
        "All full-time employees are allocated 22 days of paid annual leave per calendar year. "
        "Leave accumulates at a rate of 1.83 days per month worked. Employees may carry forward "
        "a maximum of 5 unused leave days into the next calendar year, which must be utilized before March 31st."
    )
    doc.add_paragraph(
        "Sick leave is granted at 12 days per year with full pay. For medical leaves extending beyond "
        "3 consecutive working days, a formal medical practitioner certificate is required upon return."
    )

    doc.add_heading("2. Remote Work & Equipment Reimbursement", level=1)
    doc.add_paragraph(
        "Apex Global supports a flexible hybrid work model. Employees in eligible technical and operational "
        "roles may work remotely up to 3 days per week with manager consent."
    )
    
    # Table in DOCX
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Expense Category"
    hdr_cells[1].text = "Annual Allowance"
    hdr_cells[2].text = "Approval Required"
    
    data = [
        ("Home Office Ergonomics Setup", "$1,000 one-time", "Manager Pre-approval"),
        ("Monthly Internet Subsidy", "$80 / month", "Automated Payroll"),
        ("Wellness & Fitness Stipend", "$500 / year", "Receipt Submission"),
    ]
    for cat, allow, apprv in data:
        row_cells = table.add_row().cells
        row_cells[0].text = cat
        row_cells[1].text = allow
        row_cells[2].text = apprv

    doc.add_heading("3. Core Working Hours & Overtime", level=1)
    doc.add_paragraph(
        "Standard working hours are 40 hours per week. Core collaboration hours across all timezones "
        "are established between 10:00 AM and 3:00 PM local office time."
    )
    doc.save(docx_path)
    print(f"Created DOCX: {docx_path}")

    # 2. Create PDF: Cloud API Reference Guide
    pdf_path = output_dir / "cloud_api_guide.pdf"
    pdf_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2563eb"),
    )
    body_style = styles['Normal']

    story.append(Paragraph("DocIntelligent Cloud API Architecture Guide", title_style))
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. Authentication Protocol", h2_style))
    story.append(Paragraph(
        "All requests to the DocIntelligent API must include a Bearer Token in the HTTP Authorization header: "
        "<code>Authorization: Bearer doc_sec_live_xxxxxx</code>. Tokens can be generated in the developer portal "
        "and rotate every 90 days for production security compliance.",
        body_style,
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Rate Limits and Quotas", h2_style))
    story.append(Paragraph(
        "The standard tier enforces a rate limit of 120 requests per minute per IP address and 5,000 total document queries per day. "
        "When limits are exceeded, the API returns HTTP 429 (Too Many Requests) with a <code>Retry-After</code> header in seconds.",
        body_style,
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. Webhook Delivery & Event Signatures", h2_style))
    story.append(Paragraph(
        "Async ingestion completion events are dispatched via HTTPS POST webhooks. Each payload includes an "
        "<code>X-DocIntelligent-Signature</code> HMAC-SHA256 signature calculated against the raw JSON payload "
        "using your webhook secret key.",
        body_style,
    ))
    pdf_doc.build(story)
    print(f"Created PDF: {pdf_path}")

    # 3. Create Markdown: Q3 Financial & Strategic Review
    md_path = output_dir / "q3_financial_report.md"
    md_content = """# Q3 Strategic & Financial Performance Report

## Executive Summary
DocIntelligent Platform reached $14.2M in Annual Recurring Revenue (ARR) in Q3, representing a 42% Year-over-Year growth rate. Gross profit margins expanded to 81.4% driven by vector database optimization and efficient inference provider routing.

## Revenue by Business Segment
| Business Segment | Q3 Revenue | YoY Growth | Net Revenue Retention (NRR) |
| :--- | :--- | :--- | :--- |
| Enterprise SaaS | $9.8M | +48% | 124% |
| Mid-Market | $3.6M | +32% | 108% |
| Developer API | $0.8M | +65% | 136% |

## Risk Factors & Strategic Mitigation
1. **Model Provider Outages**: Mitigated through multi-provider fallback orchestration across CodeCraft, OpenRouter, and UnoRouter.
2. **Data Privacy & Retention**: Enforced zero-retention data policies on external inference gateways and localized vector storage.
"""
    md_path.write_text(md_content, encoding="utf-8")
    print(f"Created Markdown: {md_path}")


if __name__ == "__main__":
    create_sample_docs()
