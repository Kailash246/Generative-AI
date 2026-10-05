import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6c757d"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Mini Project Report | Local GitHub Repository Code Explainer")
            self.setStrokeColor(colors.HexColor("#dee2e6"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
        
        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#dee2e6"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        
        self.drawString(54, 32, "Generative AI Coursework - Mini Project")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_pdf(filename="Mini_Project_Report_Local_GitHub_Code_Explainer.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Color Palette
    c_primary = colors.HexColor("#1A365D")    # Deep Navy
    c_secondary = colors.HexColor("#0D9488")  # Teal Accent
    c_dark = colors.HexColor("#2D3748")       # Charcoal Body Text
    c_bg_box = colors.HexColor("#F8FAFC")     # Light Card Background
    c_border = colors.HexColor("#CBD5E1")     # Clean Slate Border

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    th_style = ParagraphStyle(
        'TH_Style',
        parent=body_style,
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TD_Style',
        parent=body_style,
        fontSize=8,
        leading=11,
        spaceAfter=0
    )

    story = []

    # Title & Subtitle Banner
    story.append(Paragraph("Local GitHub Repository Code Explainer", title_style))
    story.append(Paragraph("A Local Generative AI Application for Automated Codebase Analysis & Explanation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=c_primary, spaceBefore=0, spaceAfter=8))

    # Meta Overview Box
    meta_data = [
        [
            Paragraph("<b>Domain:</b> Local GenAI / Full-Stack Application", body_style),
            Paragraph("<b>Stack:</b> FastAPI + Streamlit + Transformers", body_style)
        ],
        [
            Paragraph("<b>Inference:</b> 100% Local (CPU / CUDA / Ollama)", body_style),
            Paragraph("<b>Target Input:</b> GitHub Repository URL", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[245, 255])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_box),
        ('BOX', (0, 0), (-1, -1), 0.75, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # 1. Executive Summary & Objective
    story.append(Paragraph("1. Executive Summary & Motivation", h1_style))
    story.append(Paragraph(
        "Understanding unfamiliar source code repositories is one of the most common friction points for developers, students, and engineers onboarding to new projects. While cloud-based LLMs exist, they often present data privacy risks with proprietary code, require paid API keys, and require persistent internet connections.",
        body_style
    ))
    story.append(Paragraph(
        "This project implements a complete, self-contained <b>Local GenAI Code Explainer</b>. Given any public GitHub URL, the application shallowly clones the repository, filters out irrelevant files, extracts key architecture entrypoints, prepares an optimized context prompt, and runs local inference using lightweight open-source models (such as Qwen 2.5, SmolLM2, or Ollama) to generate a structured, plain-language breakdown of the codebase.",
        body_style
    ))

    # 2. System Architecture & End-to-End Pipeline
    story.append(Paragraph("2. System Architecture & End-to-End Pipeline", h1_style))
    story.append(Paragraph(
        "The architecture follows a clear 5-stage sequential pipeline:",
        body_style
    ))

    pipeline_raw = [
        ("Step", "Component", "Key Functionality & Tech"),
        (
            "1",
            "<b>Repo Ingestion</b>",
            "Clones target GitHub repo shallowly (<code>depth=1</code>) via GitPython into a local cache directory to minimize network and disk overhead."
        ),
        (
            "2",
            "<b>Code Processing</b>",
            "Scans file tree, filters binary files, lockfiles, and virtual environments, detects languages, and extracts entrypoint source code (e.g. <code>app.py</code>, <code>main.py</code>, configs)."
        ),
        (
            "3",
            "<b>Local LLM Engine</b>",
            "Formats context with file trees and code snippets, then runs local generation via Hugging Face Transformers (<code>Qwen/Qwen2.5-0.5B-Instruct</code>) or local Ollama."
        ),
        (
            "4",
            "<b>FastAPI Backend</b>",
            "Exposes high-performance REST endpoints (<code>/api/explain</code>, <code>/api/models</code>, <code>/api/health</code>) with Pydantic schema validation and CORS."
        ),
        (
            "5",
            "<b>Streamlit Frontend</b>",
            "Provides a clean, interactive user dashboard featuring live progress indicators, structured explanations, ASCII tree views, code inspection, and markdown export."
        )
    ]

    pipeline_cells = []
    for r_idx, row in enumerate(pipeline_raw):
        row_cells = []
        for c_idx, cell in enumerate(row):
            st_use = th_style if r_idx == 0 else td_style
            row_cells.append(Paragraph(cell, st_use))
        pipeline_cells.append(row_cells)

    p_table = Table(pipeline_cells, colWidths=[36, 104, 360])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_box]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 6))

    # 3. Technical Highlights & Design Decisions
    story.append(Paragraph("3. Technical Highlights & Design Decisions", h1_style))
    
    story.append(Paragraph("<b>A. Context Window Budgeting & Priority Filtering:</b>", h2_style))
    story.append(Paragraph(
        "Small local LLMs (0.5B to 1.5B parameters) have tight context budgets. Ingesting whole repositories unfiltered would cause memory exhaustion and slow generation. The Repo Processor solves this via:",
        body_style
    ))
    story.append(Paragraph("• <b>Exclusion Lists:</b> Strips out <code>.git</code>, <code>node_modules</code>, <code>__pycache__</code>, <code>.venv</code>, build artifacts, images, and lockfiles (<code>package-lock.json</code>, <code>poetry.lock</code>).", bullet_style))
    story.append(Paragraph("• <b>Semantic Priority Scoring:</b> Ranks files by architecture relevance: <code>README.md</code> (score 0), configs & dependencies like <code>requirements.txt</code> (score 1), entrypoints like <code>app.py</code> / <code>main.py</code> (score 2), and general source files (score 3).", bullet_style))
    story.append(Paragraph("• <b>Smart Truncation:</b> Limits individual file excerpts to the top 100-150 lines and enforces an overall context budget (12,000 characters).", bullet_style))

    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>B. Zero-Cloud Local Inference & CPU Multi-Threading:</b>", h2_style))
    story.append(Paragraph(
        "To enable smooth execution on laptops without dedicated GPUs, the LLM engine dynamically configures PyTorch CPU multi-threading (<code>torch.set_num_threads</code> based on available CPU cores) and employs float32 execution with greedy/low-temperature sampling.",
        body_style
    ))

    story.append(Spacer(1, 6))

    # 4. Sample Demonstration & Output
    story.append(Paragraph("4. Sample Demonstration & Output", h1_style))
    story.append(Paragraph(
        "When provided with a sample repository (e.g., a Streamlit/Python data dashboard), the application successfully cloned, scanned, and produced the following structured output completely locally:",
        body_style
    ))

    sample_output_text = """<b>Project Overview:</b><br/>
This project is an interactive data visualization web application that analyzes and maps historical Uber taxi pickup patterns across New York City.<br/><br/>
<b>Key Features:</b><br/>
• Displays geographic pickup distributions on interactive 3D map layers.<br/>
• Provides hourly filtering sliders to inspect peak transit hours.<br/>
• Visualizes data using HexagonLayer density mapping.<br/>
• Caches large datasets locally for ultra-fast UI updates.<br/><br/>
<b>Main Technologies:</b><br/>
• <b>Python:</b> Core application runtime.<br/>
• <b>Streamlit:</b> Web application interface and reactive widgets.<br/>
• <b>PyDeck &amp; Altair:</b> Geospatial 3D maps and statistical charts.<br/>
• <b>Pandas &amp; NumPy:</b> Data filtering and timestamp manipulation.<br/><br/>
<b>How It Works:</b><br/>
1. The user selects a specific time or hour on the Streamlit slider widget.<br/>
2. The Python backend filters the raw Uber pickup dataset in memory.<br/>
3. PyDeck computes coordinates and renders the geographic map view.<br/>
4. The frontend renders the visual summary instantly for the user."""

    sample_box = [
        [Paragraph(sample_output_text, callout_style)]
    ]
    s_table = Table(sample_box, colWidths=[500])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_box),
        ('BOX', (0, 0), (-1, -1), 1, c_secondary),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 6))

    # 5. Project Evaluation & Key Learnings
    story.append(Paragraph("5. Project Evaluation & Key Learnings", h1_style))
    
    learnings_raw = [
        ("Category", "Observations & Outcomes"),
        (
            "<b>Inference Speed</b>",
            "Shallow cloning takes ~1-2s. Local inference with Qwen2.5-0.5B on CPU generates complete explanations in ~15-30s with CPU multi-threading."
        ),
        (
            "<b>Explanation Quality</b>",
            "Combining directory tree context with README headers and entrypoint source code gives small models sufficient semantic signal to accurately describe architecture."
        ),
        (
            "<b>Modularity</b>",
            "Decoupling the FastAPI backend and Streamlit frontend allows replacing the local model provider (Hugging Face / Ollama) without modifying UI logic."
        ),
        (
            "<b>Data Privacy</b>",
            "Zero external API calls are made during inference; proprietary and internal code repositories can be safely analyzed offline."
        )
    ]

    learnings_cells = []
    for r_idx, row in enumerate(learnings_raw):
        row_cells = []
        for c_idx, cell in enumerate(row):
            st_use = th_style if r_idx == 0 else td_style
            row_cells.append(Paragraph(cell, st_use))
        learnings_cells.append(row_cells)

    l_table = Table(learnings_cells, colWidths=[105, 395])
    l_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_box]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(l_table)
    story.append(Spacer(1, 6))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion", h1_style))
    story.append(Paragraph(
        "The Local GitHub Repository Code Explainer successfully demonstrates how small, open-source language models can be coupled with intelligent preprocessing pipelines to deliver tangible developer productivity tools. By executing 100% locally, the solution delivers privacy, cost-efficiency, and simplicity in explaining modern software codebases.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF report generated successfully: {filename}")

if __name__ == "__main__":
    out_name = sys.argv[1] if len(sys.argv) > 1 else "Mini_Project_Report_Local_GitHub_Code_Explainer.pdf"
    build_pdf(out_name)
