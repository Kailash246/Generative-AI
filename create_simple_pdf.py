import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

class SimpleNumberedCanvas(canvas.Canvas):
    """Simple standard header/footer with page numbers."""
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
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 9)
        self.setFillColor(colors.black)
        
        # Simple thin footer line
        self.setStrokeColor(colors.gray)
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        
        self.drawString(54, 32, "Mini Project Report: Local GitHub Repository Code Explainer")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_simple_pdf(filename="Mini_Project_Report_Local_GitHub_Code_Explainer.pdf"):
    # Standard margins (0.75 in / 54 pt)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Standard clean academic styles (Times-Roman based)
    title_style = ParagraphStyle(
        'MainTitle',
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        alignment=1, # Center
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'SubTitle',
        fontName='Times-Italic',
        fontSize=12,
        leading=15,
        alignment=1, # Center
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Simple',
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Simple',
        fontName='Times-Bold',
        fontSize=10.5,
        leading=13.5,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Simple',
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Simple',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=2
    )

    box_text_style = ParagraphStyle(
        'BoxText_Simple',
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        spaceAfter=0
    )

    code_block_style = ParagraphStyle(
        'CodeBlock',
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black
    )

    table_header_style = ParagraphStyle(
        'TH_Simple',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12,
        spaceAfter=0
    )

    table_cell_style = ParagraphStyle(
        'TD_Simple',
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        spaceAfter=0
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("MINI PROJECT REPORT", title_style))
    story.append(Paragraph("Local GitHub Repository Code Explainer", ParagraphStyle('Sub', parent=title_style, fontSize=15, leading=18)))
    story.append(Paragraph("Course: Generative AI | Semester 5", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=10))

    # 1. Objective
    story.append(Paragraph("1. Objective", h1_style))
    story.append(Paragraph(
        "The objective of this mini-project is to build a complete local GenAI application that accepts any public GitHub repository URL and automatically produces a simple-language, structured explanation of the codebase. The application demonstrates the complete end-to-end GenAI lifecycle running locally on the user's machine:",
        body_style
    ))
    story.append(Paragraph(
        "<b>GitHub Repository &rarr; Code Processing &rarr; Local LLM &rarr; Backend API &rarr; Frontend UI &rarr; Codebase Explanation</b>",
        ParagraphStyle('PipelineText', parent=body_style, alignment=1, spaceBefore=2, spaceAfter=6)
    ))

    # 2. Technology Stack
    story.append(Paragraph("2. Technology Stack", h1_style))
    
    tech_data = [
        [Paragraph("Component", table_header_style), Paragraph("Technology Used", table_header_style), Paragraph("Role & Description", table_header_style)],
        [Paragraph("Local GenAI", table_cell_style), Paragraph("Hugging Face Transformers / PyTorch", table_cell_style), Paragraph("Runs local open-source LLMs (Qwen 2.5 0.5B, SmolLM2, or Ollama) directly on CPU/GPU without cloud API dependencies.", table_cell_style)],
        [Paragraph("Backend", table_cell_style), Paragraph("FastAPI, Uvicorn, Pydantic", table_cell_style), Paragraph("Provides REST API endpoints for repository analysis, input validation, and asynchronous orchestration.", table_cell_style)],
        [Paragraph("Repository Processing", table_cell_style), Paragraph("GitPython & Python OS Handling", table_cell_style), Paragraph("Performs shallow repository cloning (depth=1), directory scanning, file filtering, and code snippet extraction.", table_cell_style)],
        [Paragraph("Frontend", table_cell_style), Paragraph("Streamlit", table_cell_style), Paragraph("Provides an interactive web dashboard for user inputs, live status tracking, file tree viewing, and markdown export.", table_cell_style)]
    ]
    t_tech = Table(tech_data, colWidths=[100, 140, 260])
    t_tech.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 8))

    # 3. System Workflow & Implementation Steps
    story.append(Paragraph("3. Step-by-Step Implementation", h1_style))
    story.append(Paragraph("The system implements the required core features through five distinct stages:", body_style))
    
    story.append(Paragraph("<b>Step 1: Shallow Repository Cloning (GitPython)</b>", h2_style))
    story.append(Paragraph(
        "The user enters a GitHub URL (e.g., <code>https://github.com/username/repository</code>). The backend uses GitPython to perform a shallow clone (<code>depth=1</code>) into a local cache. This downloads only the latest commit, minimizing network bandwidth and disk usage.",
        body_style
    ))

    story.append(Paragraph("<b>Step 2: File Filtering & Priority Extraction</b>", h2_style))
    story.append(Paragraph(
        "To fit within the local LLM's context window, the processor ignores binary files (images, videos, executables), virtual environments (<code>venv</code>, <code>__pycache__</code>, <code>node_modules</code>), and lock files (<code>package-lock.json</code>, <code>poetry.lock</code>). It builds an ASCII directory tree and extracts key files based on priority: README files, configuration files (<code>requirements.txt</code>, <code>package.json</code>), and entrypoint source files (<code>app.py</code>, <code>main.py</code>, <code>index.js</code>).",
        body_style
    ))

    story.append(Paragraph("<b>Step 3: Local LLM Prompting & Inference</b>", h2_style))
    story.append(Paragraph(
        "The assembled repository structure, dependency list, and source code excerpts are formatted into an instruction prompt. The local LLM (<code>Qwen/Qwen2.5-0.5B-Instruct</code>) generates a structured, plain-English summary covering Project Overview, Key Features, Main Technologies, and How It Works.",
        body_style
    ))

    story.append(Paragraph("<b>Step 4: FastAPI Backend Service</b>", h2_style))
    story.append(Paragraph(
        "FastAPI coordinates the cloning, processing, and LLM inference. It exposes endpoints: <code>POST /api/explain</code> (full analysis), <code>GET /api/models</code> (available models), and <code>GET /api/health</code> (server and hardware status).",
        body_style
    ))

    story.append(Paragraph("<b>Step 5: Streamlit Frontend Display</b>", h2_style))
    story.append(Paragraph(
        "The Streamlit frontend presents an intuitive interface where users can enter a URL or choose a sample repository. It renders the explanation, provides an ASCII tree view, allows viewing individual source code files with syntax highlighting, and provides a button to download the explanation as Markdown.",
        body_style
    ))

    story.append(Spacer(1, 6))

    # 4. Example Input and Generated Output
    story.append(Paragraph("4. Example Input & Output", h1_style))
    story.append(Paragraph("<b>Input:</b> <code>https://github.com/streamlit/demo-uber-nyc-pickups</code>", body_style))
    story.append(Paragraph("<b>Generated Local LLM Explanation:</b>", body_style))

    sample_output = """<b>Project Overview:</b><br/>
This project is an interactive data visualization web application that analyzes and maps historical Uber taxi pickup patterns across New York City.<br/><br/>
<b>Key Features:</b><br/>
The application allows users to:<br/>
• View and interact with Uber pickup data on a dynamic 3D map.<br/>
• Filter pickup activity by specific hours of the day using interactive sliders.<br/>
• Visualize geographic pickup density using hexagon layers.<br/>
• Cache large datasets locally for fast user interactions.<br/><br/>
<b>Main Technologies:</b><br/>
• <b>Python:</b> Core application programming language.<br/>
• <b>Streamlit:</b> Web frontend framework and reactive UI components.<br/>
• <b>PyDeck &amp; Altair:</b> 3D geospatial mapping and statistical data charts.<br/>
• <b>Pandas &amp; NumPy:</b> Data manipulation, filtering, and numerical processing.<br/><br/>
<b>How It Works:</b><br/>
1. The user opens the web application and selects an hour on the Streamlit slider widget.<br/>
2. The Python backend filters the raw Uber pickup records for the selected time window.<br/>
3. PyDeck computes coordinates and renders the geographic density map.<br/>
4. The frontend displays the updated map and summary charts directly to the user."""

    sample_table = Table([[Paragraph(sample_output, box_text_style)]], colWidths=[500])
    sample_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sample_table)
    story.append(Spacer(1, 8))

    # 5. How to Run
    story.append(Paragraph("5. Execution Instructions", h1_style))
    story.append(Paragraph("The application can be started using the following simple steps:", body_style))
    story.append(Paragraph("1. <b>Install Dependencies:</b> <code>pip install -r requirements.txt</code>", bullet_style))
    story.append(Paragraph("2. <b>Start Backend:</b> <code>python run_backend.py</code> (runs on <code>http://127.0.0.1:8000</code>)", bullet_style))
    story.append(Paragraph("3. <b>Start Frontend:</b> <code>python run_frontend.py</code> (opens in browser at <code>http://localhost:8501</code>)", bullet_style))
    story.append(Paragraph("4. <b>Or One-Click Launch (Windows):</b> Double-click <code>run_all.bat</code>", bullet_style))

    story.append(Spacer(1, 6))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion", h1_style))
    story.append(Paragraph(
        "This project successfully fulfills the requirement of building a local, private GenAI tool for code explanation. By combining shallow git cloning, intelligent file filtering, and small open-source language models running locally, the system provides quick and accurate summaries of unfamiliar codebases without requiring paid APIs or internet connectivity during inference.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=SimpleNumberedCanvas)
    print(f"[SUCCESS] Simple PDF generated: {filename}")

if __name__ == "__main__":
    out_name = sys.argv[1] if len(sys.argv) > 1 else "Mini_Project_Report_Local_GitHub_Code_Explainer.pdf"
    build_simple_pdf(out_name)
