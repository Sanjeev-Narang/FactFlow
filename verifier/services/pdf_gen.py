import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class DocumentPDFExportService:
    """
    Takes an UploadedDocument instance with its claims, structures them 
    into a clean report format, and returns an in-memory PDF byte stream.
    """

    def generate_report_pdf(self, doc_record) -> io.BytesIO:
        buffer = io.BytesIO()
        
        # 1. Page Template Settings
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        # 2. Build Typography Custom Styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#111827'),
            spaceAfter=6
        )
        
        meta_style = ParagraphStyle(
            'ReportMeta',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=20
        )
        
        claim_style = ParagraphStyle(
            'ClaimEntry',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6
        )
        
        verdict_style = ParagraphStyle(
            'VerdictEntry',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=14
        )

        elements = []

        # 3. Add Document Header Info
        elements.append(Paragraph(f"Fact-Check Analysis Summary", title_style))
        elements.append(Paragraph(f"<b>Source Document:</b> {doc_record.file_name} <br/><b>Generated At:</b> {doc_record.uploaded_at.strftime('%Y-%m-%d %H:%M:%S UTC')}", meta_style))
        elements.append(Spacer(1, 10))

        # 4. Map and Highlight Each Extracted Claim Content
        all_claims = doc_record.claims.all()
        
        if not all_claims.exists():
            elements.append(Paragraph("No verifiable factual statements were found in this document.", claim_style))
        else:
            for index, claim in enumerate(all_claims, 1):
                # Highlight Verdict color safely using clean code conditions
                verdict_color = '#16a34a'  # Green for Verified
                if claim.verdict == 'Inaccurate':
                    verdict_color = '#d97706'  # Amber
                elif claim.verdict == 'False':
                    verdict_color = '#dc2626'  # Red

                # Assemble HTML strings for paragraph mapping models
                claim_html = f"<b>[CLAIM #{index}] Claim:</b> {claim.extracted_claim}"
                verdict_html = f"<b>Verdict:</b> <font color='{verdict_color}'><b>{claim.verdict}</b></font><br/>" \
                               f"<b>Explanation:</b> {claim.explanation}"
                
                # Append corrected text metric row block if present
                if claim.corrected_fact:
                    verdict_html += f"<br/><b>Corrected Fact:</b> {claim.corrected_fact}"

                elements.append(Paragraph(claim_html, claim_style))
                elements.append(Paragraph(verdict_html, verdict_style))
                elements.append(Spacer(1, 8))

        # 5. Compile Everything and return stream back to volatile RAM
        doc.build(elements)
        buffer.seek(0)
        return buffer
