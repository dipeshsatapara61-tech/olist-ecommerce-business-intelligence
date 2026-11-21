import os
import sys
from pathlib import Path
from decimal import Decimal
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image, Preformatted, HRFlowable
)
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Image paths (using the user's uploaded dashboard images)
DASHBOARD_IMAGES = {
    'page_1': str(REPORTS_DIR / "Dashboard_Executive_Overview.png"),
    'page_2': str(REPORTS_DIR / "Dashboard_Sales_Analysis.png"),
    'page_3': str(REPORTS_DIR / "Dashboard_Seller_Customer.png"),
    'page_4': str(REPORTS_DIR / "Dashboard_Delivery_Ratings.png")
}

# ==============================================================================
# NUMBERED CANVAS WITH HEADER AND FOOTER
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
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
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, A4[1] - 30, A4[0] - 36, A4[1] - 30)
            self.drawString(36, A4[1] - 25, "Olist E-Commerce Business Intelligence & Analytics | Project Documentation")
            self.setFont("Helvetica", 7.5)
            self.drawRightString(A4[0] - 36, A4[1] - 25, "End-to-End Analytics Portfolio")
        
        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 32, A4[0] - 36, 32)
        
        self.setFont("Helvetica", 7.5)
        self.drawString(36, 22, "PostgreSQL • SQL • Python • Microsoft Power BI • DAX")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 22, page_text)
        self.restoreState()


# ==============================================================================
# PROFESSIONAL STYLES
# ==============================================================================
def get_doc_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverDocTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='CoverDocSubtitle',
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0284C7'),
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name='MajorSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.white,
        alignment=0
    ))
    styles.add(ParagraphStyle(
        name='SubSectionTitle',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='QuestionHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='BodyP',
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='BodyPBold',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='BulletP',
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor('#334155'),
        leftIndent=10,
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name='SQLCode',
        fontName='Courier',
        fontSize=6.2,
        leading=8.0,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        name='THead',
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.0,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TCell',
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.HexColor('#334155')
    ))
    styles.add(ParagraphStyle(
        name='TCellCenter',
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.HexColor('#334155'),
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='TCellBold',
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.8,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        name='ImageCaption',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0369A1'),
        alignment=1,
        spaceBefore=3,
        spaceAfter=5
    ))
    styles.add(ParagraphStyle(
        name='CalloutBoxText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0369A1')
    ))
    styles.add(ParagraphStyle(
        name='ArchitectureText',
        fontName='Courier-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor('#1E293B'),
        alignment=1
    ))
    return styles

# ==============================================================================
# UI COMPONENT HELPERS
# ==============================================================================
def make_banner(title_text, subtitle_text, styles):
    content = [
        [Paragraph(f"<b>{title_text.upper()}</b>", styles['MajorSectionTitle'])],
        [Paragraph(f"<font size=7.5 color='#BAE6FD'>{subtitle_text}</font>", styles['BodyP'])]
    ]
    t = Table(content, colWidths=[523.27])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0284C7')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def make_sql_card(code_text, styles):
    p = Preformatted(code_text.strip(), styles['SQLCode'])
    t = Table([[p]], colWidths=[523.27])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def make_callout(text, styles, title="Business Owner Decision / Key Action:"):
    p = Paragraph(f"<b>{title}</b> {text}", styles['CalloutBoxText'])
    t = Table([[p]], colWidths=[523.27])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F9FF')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#0284C7')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    return t

def make_question_table(meta_dict, styles):
    """Formats the metadata of a business question into an organized, 2-column table"""
    data = []
    for k, v in meta_dict.items():
        data.append([
            Paragraph(f"<b>{k}</b>", styles['TCellBold']),
            Paragraph(v, styles['TCell'])
        ])
    t = Table(data, colWidths=[130, 393.27])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t

# ==============================================================================
# BUILDER FUNCTION
# ==============================================================================
def build_pdf():
    pdf_path = REPORTS_DIR / "Olist_Ecommerce_Business_Intelligence_Project_Documentation.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38
    )
    styles = get_doc_styles()
    story = []

    # ==========================================================================
    # SECTION 1: PROJECT OVERVIEW & COMPLETE PROJECT INFORMATION (PAGE 1)
    # ==========================================================================
    story.append(Paragraph("Olist E-Commerce Business Intelligence & Analytics", styles['CoverDocTitle']))
    story.append(Paragraph("End-to-End Enterprise Analytics Project: Python ETL • PostgreSQL Database • Advanced SQL • Power BI Dashboard Suite • DAX Modeling", styles['CoverDocSubtitle']))
    
    story.append(make_banner("1. Project Overview & Comprehensive Information", "Strategic Context, Problem Statement, Objectives, Technology Stack & Architecture", styles))
    story.append(Spacer(1, 6))

    # Intro & Problem
    story.append(Paragraph("<b>Project Introduction:</b> This project represents a complete, production-grade Business Intelligence implementation analyzing Brazilian e-commerce operations using the Olist marketplace dataset (2016–2018). Operating as a major marketplace integrator connecting independent small-and-medium merchants to Brazil's leading e-commerce channels (such as Mercado Livre, B2W, and Amazon), Olist processes complex multi-party transactions. The project was engineered to transform dispersed, multi-table transactional records into an intuitive, centralized analytical system that empowers management and business owners to make decisive commercial and operational decisions.", styles['BodyP']))
    
    story.append(Paragraph("<b>Business Problem:</b> Without a centralized business intelligence platform, modern e-commerce leaders face critical blind spots across fragmented datasets: (1) Inability to monitor real-time gross revenue versus true net product earnings due to convoluted freight fees; (2) Limited visibility into extreme regional demand and supply asymmetries across Brazil's 27 states; (3) Lack of clarity regarding product category concentration and long-tail dragging margins; (4) Unmonitored carrier transit bottlenecks leading to customer dissatisfaction; and (5) Undetected customer retention deficits with low repeat purchase rates.", styles['BodyP']))

    # Objectives & Scope
    obj_scope_data = [
        [Paragraph("<b>Core Project Objectives</b>", styles['THead']), Paragraph("<b>Analytical Project Scope</b>", styles['THead'])],
        [
            Paragraph("• Analyze macro commercial performance & gross revenue trends.<br/>"
                      "• Track monthly order growth and seasonal sales spikes.<br/>"
                      "• Identify top-performing product categories via Pareto analysis.<br/>"
                      "• Evaluate merchant distribution and individual seller revenue.<br/>"
                      "• Uncover customer geographic concentration across states.<br/>"
                      "• Diagnose logistics fulfillment transit times & SLA compliance.<br/>"
                      "• Measure customer sentiment and review rating drivers.<br/>"
                      "• Provide actionable recommendations to maximize margins.", styles['TCell']),
            Paragraph("• <b>Financial Analytics:</b> Gross commercial volume, product sales vs. freight split, and Average Order Value (AOV).<br/>"
                      "• <b>Merchandise Analytics:</b> Category performance, price tiers, and freight-to-price ratios.<br/>"
                      "• <b>Customer Intelligence:</b> State/city demographics, repeat purchase rate, and customer acquisition trends.<br/>"
                      "• <b>Seller Intelligence:</b> Merchant regional concentration and sales rankings.<br/>"
                      "• <b>Logistics Analytics:</b> Transit SLA compliance, intra-state vs. cross-state speed, and carrier delays.<br/>"
                      "• <b>Customer Experience:</b> 1-to-5 star sentiment and delay correlation.", styles['TCell'])
        ]
    ]
    t_obj = Table(obj_scope_data, colWidths=[261, 262.27])
    t_obj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_obj)
    story.append(Spacer(1, 5))

    # Datasets & Tech Stack
    tech_data = [
        [Paragraph("<b>Original Relational Datasets (Olist Brazilian Public Data)</b>", styles['THead']), Paragraph("<b>Technologies & Tool Ecosystem</b>", styles['THead'])],
        [
            Paragraph("1. <code>olist_customers_dataset.csv</code> (99,441 records: customer token, zip, city, state)<br/>"
                      "2. <code>olist_orders_dataset.csv</code> (99,441 records: status, purchase/delivery dates)<br/>"
                      "3. <code>olist_order_items_dataset.csv</code> (112,650 items: order_id, product, seller, price, freight)<br/>"
                      "4. <code>olist_order_payments_dataset.csv</code> (103,886 records: type, installments, value)<br/>"
                      "5. <code>olist_order_reviews_dataset.csv</code> (99,224 records: score 1-5, comment, timestamps)<br/>"
                      "6. <code>olist_products_dataset.csv</code> (32,951 items: category, photos, weight, dimensions)<br/>"
                      "7. <code>olist_sellers_dataset.csv</code> (3,095 sellers: zip, city, state)<br/>"
                      "8. <code>olist_geolocation_dataset.csv</code> (1M raw GPS coordinates / 738K cleaned)<br/>"
                      "9. <code>product_category_name_translation.csv</code> (71 categories: Portuguese to English)", styles['TCell']),
            Paragraph("• <b>Python (Pandas, NumPy, SQLAlchemy, Psycopg2):</b> Data inspection, duplicate GPS coordinate deduplication, categorical string trimming, ISO timestamp standardization, and automated PostgreSQL loading.<br/>"
                      "• <b>PostgreSQL 18:</b> Robust relational database management, schema creation with primary/foreign keys, check constraints, and B-Tree performance indexing.<br/>"
                      "• <b>SQL:</b> Advanced business querying utilizing CTEs, window functions, aggregations, conditional filtering, and multi-table joins.<br/>"
                      "• <b>Microsoft Power BI Desktop:</b> Star-schema semantic data modeling, custom UI/UX design, interactive slicers, and executive visual reporting.<br/>"
                      "• <b>DAX (Data Analysis Expressions):</b> Dynamic business measures including gross revenue, delivery rates, and repeat customer retention.<br/>"
                      "• <b>Git & GitHub:</b> Repository version control, technical documentation, and portfolio hosting.", styles['TCell'])
        ]
    ]
    t_tech = Table(tech_data, colWidths=[261, 262.27])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 5))

    # Architecture Flowchart
    arch_flow = (
        "┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐\n"
        "│    Raw CSV Datasets     │  ──>  │  Python Data Cleaning   │  ──>  │   Processed Datasets    │\n"
        "│ (9 Relational CSV Files)│       │ (Deduplication/Dtypes)  │       │ (Cleaned CSV Directory) │\n"
        "└─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘\n"
        "                                                                                 │\n"
        "                                                                                 ▼\n"
        "┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐\n"
        "│ Power BI Model & DAX    │  <──  │   SQL Query Analysis    │  <──  │   PostgreSQL Database   │\n"
        "│(Star Schema/Measures)   │       │(20 Strategic Questions) │       │(Tables, PK/FK, Indexes) │\n"
        "└─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘\n"
        "             │\n"
        "             ▼\n"
        "┌─────────────────────────────────────────────────────────────────────────────────────────────┐\n"
        "│ 4 Interactive Dashboard Pages: Executive Overview • Sales & Products • Sellers • Delivery   │\n"
        "│                      ──> Data-Driven Business Insights & Decisions ──>                      │\n"
        "└─────────────────────────────────────────────────────────────────────────────────────────────┘"
    )
    story.append(Preformatted(arch_flow, styles['ArchitectureText']))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Project Deliverables:</b> Complete PostgreSQL database instance, 5 documentation guides, 3 exploratory Jupyter notebooks, 3 published executive PDF reports, DAX calculation library, and an interactive 4-page Power BI dashboard (`Dashboard.pbix`).", styles['BodyP']))

    # ==========================================================================
    # SECTION 2: PROJECT DEVELOPMENT PROCESS – BEFORE BUILDING (PAGE 2)
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("2. Project Development Process & Methodology", "The 16-Step Engineering Lifecycle: From Problem Formulation to Final Dashboard Validation", styles))
    story.append(Spacer(1, 6))

    dev_steps_data = [
        [Paragraph("<b>Step & Lifecycle Phase</b>", styles['THead']), Paragraph("<b>What Was Done</b>", styles['THead']), Paragraph("<b>Why It Was Necessary</b>", styles['THead']), Paragraph("<b>Tool Used</b>", styles['THead']), Paragraph("<b>Output Produced</b>", styles['THead'])],
        
        [Paragraph("<b>1. Requirement Identification</b>", styles['TCellBold']),
         Paragraph("Defined core business reporting requirements with management.", styles['TCell']),
         Paragraph("Ensures the dashboard directly addresses stakeholder decisions.", styles['TCell']),
         Paragraph("Business Analysis", styles['TCell']),
         Paragraph("Project KPI charter & requirements document.", styles['TCell'])],

        [Paragraph("<b>2. Problem Understanding</b>", styles['TCellBold']),
         Paragraph("Mapped e-commerce business model (Olist marketplace integration).", styles['TCell']),
         Paragraph("Essential to understand multi-seller fulfillment & buyer flows.", styles['TCell']),
         Paragraph("Domain Research", styles['TCell']),
         Paragraph("Conceptual business flow diagram.", styles['TCell'])],

        [Paragraph("<b>3. Dataset Collection</b>", styles['TCellBold']),
         Paragraph("Downloaded and organized 9 raw CSV files from Olist repository.", styles['TCell']),
         Paragraph("Establishes the raw data foundation for the project.", styles['TCell']),
         Paragraph("File System", styles['TCell']),
         Paragraph("<code>data/raw/</code> dataset repository.", styles['TCell'])],

        [Paragraph("<b>4. Dataset Exploration</b>", styles['TCellBold']),
         Paragraph("Inspected schemas, row counts, memory footprints, and datatypes.", styles['TCell']),
         Paragraph("Determines table structures and identifies initial anomalies.", styles['TCell']),
         Paragraph("Python / Pandas", styles['TCell']),
         Paragraph("<code>src/01_inspect_datasets.py</code> log report.", styles['TCell'])],

        [Paragraph("<b>5. Data Profiling & Quality</b>", styles['TCellBold']),
         Paragraph("Audited column completeness, uniqueness, and value distributions.", styles['TCell']),
         Paragraph("Quantifies missingness and identifies integrity bottlenecks.", styles['TCell']),
         Paragraph("Python / Pandas", styles['TCell']),
         Paragraph("<code>data_quality_summary.csv</code> report.", styles['TCell'])],

        [Paragraph("<b>6. Anomaly Investigation</b>", styles['TCellBold']),
         Paragraph("Investigated null timestamps, duplicate reviews, and repeated GPS.", styles['TCell']),
         Paragraph("Prevents dropping valid business records (e.g. textless reviews).", styles['TCell']),
         Paragraph("Python script", styles['TCell']),
         Paragraph("<code>src/03_investigate_data_issues.py</code>.", styles['TCell'])],

        [Paragraph("<b>7. Data Cleaning Pipeline</b>", styles['TCellBold']),
         Paragraph("Purged 261K duplicate GPS rows, cast 5-digit CEPs, parsed ISO dates.", styles['TCell']),
         Paragraph("Ensures data hygiene, spatial precision, and join reliability.", styles['TCell']),
         Paragraph("Python (Pandas)", styles['TCell']),
         Paragraph("9 cleaned datasets in <code>data/processed/cleaned/</code>.", styles['TCell'])],

        [Paragraph("<b>8. PostgreSQL Schema Design</b>", styles['TCellBold']),
         Paragraph("Engineered 3NF database schema with primary keys, FKs, and indexes.", styles['TCell']),
         Paragraph("Guarantees strict referential integrity and query optimization.", styles['TCell']),
         Paragraph("PostgreSQL / DDL", styles['TCell']),
         Paragraph("<code>database/SQL.sql</code> schema script.", styles['TCell'])],

        [Paragraph("<b>9. PostgreSQL Data Ingestion</b>", styles['TCellBold']),
         Paragraph("Automated batch loading of cleaned CSVs into PostgreSQL tables.", styles['TCell']),
         Paragraph("Transitions raw flat files into an enterprise relational engine.", styles['TCell']),
         Paragraph("Python / SQLAlchemy", styles['TCell']),
         Paragraph("Populated <code>olist_ecommerce</code> database.", styles['TCell'])],

        [Paragraph("<b>10. Relationship Validation</b>", styles['TCellBold']),
         Paragraph("Executed 9 SQL audits verifying 0 orphan records and valid keys.", styles['TCell']),
         Paragraph("Certifies zero data corruption before building analytical visuals.", styles['TCell']),
         Paragraph("SQL / PostgreSQL", styles['TCell']),
         Paragraph("<code>database/relationship_validation.sql</code>.", styles['TCell'])],

        [Paragraph("<b>11. SQL Business Queries</b>", styles['TCellBold']),
         Paragraph("Authored 16 core queries answering sales, delivery, and seller KPIs.", styles['TCell']),
         Paragraph("Validates business figures and provides analytical benchmark.", styles['TCell']),
         Paragraph("SQL (CTEs/Windows)", styles['TCell']),
         Paragraph("<code>database/analysis_queries.sql</code>.", styles['TCell'])],

        [Paragraph("<b>12. Power BI Database Setup</b>", styles['TCellBold']),
         Paragraph("Connected Power BI Desktop to PostgreSQL via Npgsql connector.", styles['TCell']),
         Paragraph("Enables dynamic data refresh directly from database tables.", styles['TCell']),
         Paragraph("Power BI Connector", styles['TCell']),
         Paragraph("Connected Power BI data source pipeline.", styles['TCell'])],

        [Paragraph("<b>13. Data Modeling (Star Schema)</b>", styles['TCellBold']),
         Paragraph("Modeled 1-to-many relationships centered on `orders` and `order_items`.", styles['TCell']),
         Paragraph("Prevents circular joins and ensures accurate bidirectional slicing.", styles['TCell']),
         Paragraph("Power BI Model View", styles['TCell']),
         Paragraph("Star-schema dimensional data model.", styles['TCell'])],

        [Paragraph("<b>14. DAX Measures Creation</b>", styles['TCellBold']),
         Paragraph("Calculated Total Revenue, AOV, On-Time Rate, and Repeat Customers.", styles['TCell']),
         Paragraph("Ensures consistent business logic across all dashboard pages.", styles['TCell']),
         Paragraph("Power BI DAX", styles['TCell']),
         Paragraph("<code>DAX_Measures_Reference.dax</code> library.", styles['TCell'])],

        [Paragraph("<b>15. 4-Page Dashboard Design</b>", styles['TCellBold']),
         Paragraph("Constructed modern dark-navy UI with KPI cards, charts, and slicers.", styles['TCell']),
         Paragraph("Delivers an intuitive, 5-second executive decision experience.", styles['TCell']),
         Paragraph("Power BI Visuals", styles['TCell']),
         Paragraph("<code>Dashboard.pbix</code> 4-page workbook.", styles['TCell'])],

        [Paragraph("<b>16. Testing & Final Validation</b>", styles['TCellBold']),
         Paragraph("Reconciled dashboard totals against SQL database query outputs.", styles['TCell']),
         Paragraph("Guarantees 100% financial accuracy (R$ 15.84M gross sales).", styles['TCell']),
         Paragraph("SQL vs Power BI", styles['TCell']),
         Paragraph("Validated production dashboard suite.", styles['TCell'])]
    ]
    t_dev = Table(dev_steps_data, colWidths=[90, 115, 125, 80, 113.27])
    t_dev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_dev)
    story.append(Spacer(1, 6))

    # Project Repository Structure Table
    story.append(Paragraph("<b>Project Repository Folder Structure & Artifact Roles</b>", styles['SubSectionTitle']))
    repo_data = [
        [Paragraph("<b>Directory / Path</b>", styles['THead']), Paragraph("<b>Description & Technical Purpose</b>", styles['THead'])],
        [Paragraph("<code>dashboard/</code>", styles['TCellBold']), Paragraph("Contains the compiled <code>Dashboard.pbix</code>, custom dark theme JSON, and DAX calculation references.", styles['TCell'])],
        [Paragraph("<code>data/raw/ & processed/</code>", styles['TCellBold']), Paragraph("Separates original immutable CSV files from cleaned, deduplicated production CSV datasets.", styles['TCell'])],
        [Paragraph("<code>database/</code>", styles['TCellBold']), Paragraph("Contains <code>SQL.sql</code> (DDL/schema), <code>relationship_validation.sql</code>, and <code>analysis_queries.sql</code>.", styles['TCell'])],
        [Paragraph("<code>docs/</code>", styles['TCellBold']), Paragraph("Complete technical guides: 01 Project Overview, 02 Data Dictionary, 03 Cleaning Methodology, 04 Insights, 05 Dashboard Guide.", styles['TCell'])],
        [Paragraph("<code>notebooks/</code>", styles['TCellBold']), Paragraph("Jupyter notebooks: 01 Exploratory Data Analysis, 02 Sales & Products, 03 Customer & Logistics.", styles['TCell'])],
        [Paragraph("<code>reports/</code>", styles['TCellBold']), Paragraph("Executive project PDF reports and high-resolution PNG captures of all 4 dashboard pages.", styles['TCell'])],
        [Paragraph("<code>src/</code>", styles['TCellBold']), Paragraph("Automated Python scripts for data inspection, quality profiling, cleaning, PostgreSQL ingestion, and PDF generation.", styles['TCell'])],
    ]
    t_repo = Table(repo_data, colWidths=[120, 403.27])
    t_repo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_repo)

    # ==========================================================================
    # SECTION 3: DASHBOARD 1 – EXECUTIVE OVERVIEW (PAGE 3)
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("3. Dashboard Page 01: Executive Overview", "Macro Business Health, Top-Line Revenue, Order Fulfillment, Payment Mix & Growth Trends", styles))
    story.append(Spacer(1, 4))

    # Actual Dashboard Screenshot
    if Path(DASHBOARD_IMAGES['page_1']).exists():
        im_p1 = Image(DASHBOARD_IMAGES['page_1'], width=520, height=288)
        story.append(im_p1)
        story.append(Paragraph("<b>Figure 1: Power BI Executive Overview Dashboard</b> — Displays top-line KPI cards, Monthly Revenue Trend, Order Status Breakdown, Payment Mix, Top 5 Categories, Monthly Order Volume, and Performance Summary Table.", styles['ImageCaption']))
    
    story.append(Paragraph("<b>Visible Dashboard Components & Layout:</b><br/>"
                           "• <b>Top KPI Cards:</b> Total Revenue (<b>R$ 15.84M</b>), Total Orders (<b>99K / 99,441</b>), Unique Customers (<b>96K / 96,096</b>), Total Products (<b>33K / 32,951</b>), Total Sellers (<b>3,095</b>), Average Order Value (<b>R$ 160.58</b>).<br/>"
                           "• <b>Charts & Tables:</b> Monthly Revenue Trend Line, Order Status Donut Chart (97.02% Delivered), Revenue by Payment Type Donut Chart, Top 5 Product Categories Bar Chart, Monthly Order Volume Column Chart, and Performance Summary Matrix.<br/>"
                           "• <b>Interactive Sidebar:</b> Date Range Slider (2016-09-04 to 2018-10-17), State Filter, Category Filter, and Payment Method Filter.", styles['BodyP']))
    story.append(Spacer(1, 4))

    # 5 Business Questions for Page 1
    story.append(Paragraph("<b>Executive Overview — 5 Core Strategic Business Questions:</b>", styles['SubSectionTitle']))

    # Q1
    q1_dict = {
        "1. Business Objective": "Determine overall gross commercial volume, order count, unique customer reach, and average order value.",
        "2. Why It Matters": "Provides business owners with the fundamental macro baseline of operational scale and commercial revenue.",
        "3. Required Tables": "<code>orders</code>, <code>order_items</code>, <code>customers</code>",
        "4. SQL Approach": "Join orders and items to aggregate total price and freight value, counting distinct order IDs and customer unique IDs.",
        "5. Power BI Visual": "Top KPI Cards (Single Value Display with Navy Blue Card Containers)",
        "6. Core Metric / KPI": "<b>Gross Revenue: R$ 15,843,553.24 | Total Orders: 99,441 | Customers: 96,096 | AOV: R$ 160.58</b>",
        "7. Interpretation": "The platform has processed nearly 100K orders with a healthy R$ 160.58 AOV across 96K customers.",
        "8. Business Action": "Maintain baseline operations while focusing margin expansion on high-AOV product categories."
    }
    story.append(Paragraph("<b>Q1: How much total revenue is the business generating, and how many orders are being placed?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q1_dict, styles))
    story.append(make_sql_card("""SELECT ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue, COUNT(DISTINCT o.order_id) AS total_orders,
       COUNT(DISTINCT c.customer_unique_id) AS unique_customers, ROUND(SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.order_id), 2) AS aov
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id JOIN customers c ON o.customer_id = c.customer_id;""", styles))
    story.append(Spacer(1, 4))

    # Q2
    q2_dict = {
        "1. Business Objective": "Analyze month-over-month sales velocity to identify seasonality, peak demand, and lowest revenue troughs.",
        "2. Why It Matters": "Enables proactive inventory stocking, logistics carrier capacity planning, and targeted marketing campaigns.",
        "3. Required Tables": "<code>orders</code>, <code>order_items</code>",
        "4. SQL Approach": "Truncate purchase timestamps to month, aggregate total sales, and calculate MoM percentage change via LAG().",
        "5. Power BI Visual": "Monthly Revenue Trend (Line Chart with smooth spline and data labels)",
        "6. Core Metric / KPI": "<b>Peak Month: November 2017 (Black Friday, R$ 1.19M) | 2018 Scale: Averaging >R$ 1.0M monthly</b>",
        "7. Interpretation": "Extreme seasonal spikes occur in November (Black Friday) and May (Mother's Day); late 2016 represents initial rollout.",
        "8. Business Action": "Negotiate temporary 3PL logistics surges and merchant inventory buffers 60 days prior to Q4 Black Friday."
    }
    story.append(Paragraph("<b>Q2: How is monthly revenue performing, and which months generate highest and lowest revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q2_dict, styles))
    story.append(make_sql_card("""SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS month, ROUND(SUM(oi.price + oi.freight_value), 2) AS monthly_revenue,
       ROUND((SUM(oi.price + oi.freight_value) - LAG(SUM(oi.price + oi.freight_value)) OVER (ORDER BY TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM'))) / 
       NULLIF(LAG(SUM(oi.price + oi.freight_value)) OVER (ORDER BY TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')), 0) * 100, 2) AS mom_growth_pct
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY 1 ORDER BY 1;""", styles))
    story.append(Spacer(1, 4))

    # Q3
    q3_dict = {
        "1. Business Objective": "Evaluate order fulfillment efficiency by quantifying delivered, canceled, and in-transit orders.",
        "2. Why It Matters": "Identifies lost revenue from order cancellations and ensures logistics pipeline health.",
        "3. Required Tables": "<code>orders</code>",
        "4. SQL Approach": "Group orders by `order_status` and calculate percentage of total orders.",
        "5. Power BI Visual": "Order Status Breakdown (Donut Chart with percentage data callouts)",
        "6. Core Metric / KPI": "<b>Delivered Orders: 96,478 (97.02%) | Canceled: 625 (0.63%) | Shipped/In-Transit: 1,107 (1.11%)</b>",
        "7. Interpretation": "Over 97% of all logged orders successfully reach customers; cancellation rates are well below industry benchmarks.",
        "8. Business Action": "Audit cancellation root causes (inventory stockouts vs. payment fraud) to reclaim up to R$ 100K in canceled sales."
    }
    story.append(Paragraph("<b>Q3: What percentage of orders are successfully delivered, canceled, or still processing?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q3_dict, styles))
    story.append(make_sql_card("""SELECT order_status, COUNT(*) AS total_orders, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM orders GROUP BY order_status ORDER BY total_orders DESC;""", styles))
    story.append(Spacer(1, 4))

    # Q4
    q4_dict = {
        "1. Business Objective": "Assess revenue contribution and consumer financing behavior across payment instruments.",
        "2. Why It Matters": "Brazilian retail requires flexible installment credit; transaction fees vary significantly by payment rail.",
        "3. Required Tables": "<code>payments</code>",
        "4. SQL Approach": "Aggregate total payment value and compute average installments per payment type.",
        "5. Power BI Visual": "Revenue by Payment Type (Donut Chart & Installment Bar Chart)",
        "6. Core Metric / KPI": "<b>Credit Card: 78.34% (R$ 12.54M, 3.5 avg installments) | Boleto: 17.92% (R$ 2.87M, 1 installment)</b>",
        "7. Interpretation": "Credit card financing is the dominant purchase driver; Boleto cash vouchers introduce 48h payment clearance latency.",
        "8. Business Action": "Offer cash discounts for Pix/Boleto to reduce interchange fees and eliminate installment chargeback risk."
    }
    story.append(Paragraph("<b>Q4: Which payment methods contribute the most to total revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q4_dict, styles))
    story.append(make_sql_card("""SELECT payment_type, COUNT(order_id) AS transactions, ROUND(SUM(payment_value), 2) AS total_val,
       ROUND(SUM(payment_value) * 100.0 / SUM(SUM(payment_value)) OVER (), 2) AS share_pct, ROUND(AVG(payment_installments), 1) AS avg_inst
FROM payments GROUP BY payment_type ORDER BY total_val DESC;""", styles))
    story.append(Spacer(1, 4))

    # Q5
    q5_dict = {
        "1. Business Objective": "Identify the top 5 product categories driving gross sales to prioritize merchant recruitment.",
        "2. Why It Matters": "Concentrating marketing and supply chain resources on key categories maximizes revenue return.",
        "3. Required Tables": "<code>order_items</code>, <code>products</code>, <code>category_translation</code>",
        "4. SQL Approach": "Join items with products and category translations, grouping by English category and ranking by gross revenue.",
        "5. Power BI Visual": "Top 5 Categories by Revenue (Horizontal Bar Chart with revenue data labels)",
        "6. Core Metric / KPI": "<b>Top 5 Categories Generate >40% of Total Sales: Health & Beauty (R$ 1.44M), Watches & Gifts (R$ 1.31M)</b>",
        "7. Interpretation": "Health & Beauty, Watches, Bed Bath Table, Sports, and Computers generate the vast majority of platform volume.",
        "8. Business Action": "Partner with premier national distributors in Health & Beauty and Watches to secure exclusive product bundles."
    }
    story.append(Paragraph("<b>Q5: Which product categories generate the highest revenue and contribute most to business growth?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q5_dict, styles))
    story.append(make_sql_card("""SELECT COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1 ORDER BY total_revenue DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))
    story.append(make_callout("Business owners use Page 01 to monitor executive health in under 5 seconds, confirming high fulfillment rates (97%), steady revenue growth, and credit card reliance while anchoring category expansion on Health & Beauty and Watches.", styles))

    # ==========================================================================
    # SECTION 4: DASHBOARD 2 – SALES & PRODUCT ANALYSIS (PAGE 4)
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("4. Dashboard Page 02: Sales & Product Analysis", "Merchandise Commercial Margins, Category Pareto Rankings, Freight Contribution & Price Tiers", styles))
    story.append(Spacer(1, 4))

    # Actual Dashboard Screenshot
    if Path(DASHBOARD_IMAGES['page_2']).exists():
        im_p2 = Image(DASHBOARD_IMAGES['page_2'], width=520, height=288)
        story.append(im_p2)
        story.append(Paragraph("<b>Figure 2: Power BI Sales & Product Analysis Dashboard</b> — Features Product Sales vs Freight split, Monthly Revenue Trajectory, Product Sales vs Freight Comparison, Category Share Treemap, Top 10 Product Categories, and Detailed Category Matrix.", styles['ImageCaption']))

    story.append(Paragraph("<b>Visible Dashboard Components & Layout:</b><br/>"
                           "• <b>KPI Cards:</b> Product Sales (<b>R$ 13.59M</b>), Total Freight (<b>R$ 2.25M</b>), Total Revenue (<b>R$ 15.84M</b>), Total Products (<b>33K</b>), Total Orders (<b>99K</b>), Average Order Value (<b>R$ 160.58</b>).<br/>"
                           "• <b>Visuals:</b> Monthly Revenue Trajectory Line Chart, Product Sales vs Freight Dual Bar Chart, Category Share Treemap, Top 10 Product Categories Horizontal Bar Chart, Category Breakdown Tabular Matrix, and Sales Financials Scorecard.<br/>"
                           "• <b>Key Insight Banner:</b> 'Health & Beauty and Watches generate highest revenue. Freight contributes 14.2% (R$ 2.25M) of gross revenue. Strong seasonal surges observed in May and November.'", styles['BodyP']))
    story.append(Spacer(1, 4))

    # 5 Business Questions for Page 2
    story.append(Paragraph("<b>Sales & Product Analysis — 5 Core Strategic Business Questions:</b>", styles['SubSectionTitle']))

    # Q6
    q6_dict = {
        "1. Business Objective": "Determine total product merchandise sales excluding freight to assess pure catalog commercial value.",
        "2. Why It Matters": "Distinguishes actual merchandise sales from logistics shipping revenue to measure true retail margin.",
        "3. Required Tables": "<code>order_items</code>, <code>products</code>, <code>category_translation</code>",
        "4. SQL Approach": "Sum `price` separately from `freight_value` grouped by category, sorting by product sales.",
        "5. Power BI Visual": "Product Sales vs. Total Freight (Side-by-side comparative Bar Chart)",
        "6. Core Metric / KPI": "<b>Pure Product Sales: R$ 13,591,643.70 (85.79% of gross) | Freight: R$ 2,251,909.54 (14.21%)</b>",
        "7. Interpretation": "Over 85% of customer expenditure goes toward product retail price; freight represents a significant 14.2% add-on.",
        "8. Business Action": "Evaluate subsidizing freight on high-margin items to boost overall cart conversion rates."
    }
    story.append(Paragraph("<b>Q6: Which product categories generate the highest sales revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q6_dict, styles))
    story.append(make_sql_card("""SELECT COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
       ROUND(SUM(oi.price), 2) AS product_sales, ROUND(SUM(oi.freight_value), 2) AS freight_fees
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1 ORDER BY product_sales DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q7
    q7_dict = {
        "1. Business Objective": "Rank the top 10 categories to examine the Pareto distribution and cumulative commercial contribution.",
        "2. Why It Matters": "Applies the 80/20 rule to focus inventory management and merchandising campaigns on primary revenue drivers.",
        "3. Required Tables": "<code>order_items</code>, <code>products</code>, <code>category_translation</code>",
        "4. SQL Approach": "Group by category, aggregate gross revenue, and compute running cumulative revenue share.",
        "5. Power BI Visual": "Top 10 Product Categories (Horizontal Bar Chart & Category Share Treemap)",
        "6. Core Metric / KPI": "<b>Top 10 Categories generate over 63% of gross commercial revenue across 71 total categories</b>",
        "7. Interpretation": "A small cluster of 10 categories (Health/Beauty, Watches, Bed/Bath, Sports, Computers, Furniture, Housewares, Auto, Toys, Garden) dominates sales.",
        "8. Business Action": "Streamline vendor onboarding and negotiate bulk shipping discounts specifically for these top 10 categories."
    }
    story.append(Paragraph("<b>Q7: What are the top 10 product categories contributing to total revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q7_dict, styles))
    story.append(make_sql_card("""SELECT COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
       COUNT(oi.order_item_id) AS units_sold, ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
       ROUND(SUM(oi.price + oi.freight_value) * 100.0 / (SELECT SUM(price + freight_value) FROM order_items), 2) AS pct_share
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1 ORDER BY total_revenue DESC LIMIT 10;""", styles))
    story.append(Spacer(1, 4))

    # Q8
    q8_dict = {
        "1. Business Objective": "Determine the freight ratio across merchandise lines to identify shipping cost friction.",
        "2. Why It Matters": "Excessive freight fees suppress conversion, increase cart abandonment, and reduce seller competitiveness.",
        "3. Required Tables": "<code>order_items</code>, <code>products</code>, <code>category_translation</code>",
        "4. SQL Approach": "Compute `freight_value / (price + freight_value)` ratio per category, filtering for categories with >= 100 units.",
        "5. Power BI Visual": "Product Sales vs Freight (Comparative stacked bar visual)",
        "6. Core Metric / KPI": "<b>Bulky Items (Furniture/Christmas): Freight exceeds 25-27% of total price | Small Items (Watches): Freight < 8%</b>",
        "7. Interpretation": "Heavier, bulky items suffer disproportionately high shipping friction, eroding consumer willingness to buy online.",
        "8. Business Action": "Introduce regional warehousing and flat-rate bulky shipping partnerships to lower freight burdens on furniture and appliances."
    }
    story.append(Paragraph("<b>Q8: How are product sales and freight charges contributing to total revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q8_dict, styles))
    story.append(make_sql_card("""SELECT COALESCE(ct.product_category_name_english, p.product_category_name) AS category,
       ROUND(SUM(oi.price), 2) AS product_sales, ROUND(SUM(oi.freight_value), 2) AS freight_fees,
       ROUND(SUM(oi.freight_value) * 100.0 / NULLIF(SUM(oi.price + oi.freight_value), 0), 2) AS freight_burden_pct
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1 HAVING COUNT(oi.order_item_id) >= 100 ORDER BY freight_burden_pct DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q9
    q9_dict = {
        "1. Business Objective": "Track monthly trajectory of product merchandise value over the 2-year operational window.",
        "2. Why It Matters": "Distinguishes organic product demand expansion from shipping inflation or fee changes.",
        "3. Required Tables": "<code>orders</code>, <code>order_items</code>",
        "4. SQL Approach": "Aggregate product sales by monthly bucket across all completed orders.",
        "5. Power BI Visual": "Monthly Revenue Trajectory (Area / Line Chart)",
        "6. Core Metric / KPI": "<b>Product Sales grew from R$ 40K in late 2016 to averaging R$ 850K+ monthly in 2018</b>",
        "7. Interpretation": "The platform achieved rapid scale during 2017, stabilizing into a mature marketplace processing ~R$ 1M gross monthly.",
        "8. Business Action": "Leverage consistent monthly volume to negotiate lower payment gateway processing fees with acquirers."
    }
    story.append(Paragraph("<b>Q9: How does monthly product sales revenue change over time?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q9_dict, styles))
    story.append(make_sql_card("""SELECT TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS month, ROUND(SUM(oi.price), 2) AS monthly_product_sales
FROM orders o JOIN order_items oi ON o.order_id = oi.order_id GROUP BY 1 ORDER BY 1;""", styles))
    story.append(Spacer(1, 4))

    # Q10
    q10_dict = {
        "1. Business Objective": "Identify the extreme ends of catalog contribution (highest vs. long-tail lowest performing categories).",
        "2. Why It Matters": "Enables catalog rationalization, removing inactive or unprofitable merchandise to optimize search indexing.",
        "3. Required Tables": "<code>order_items</code>, <code>products</code>, <code>category_translation</code>",
        "4. SQL Approach": "Union top 5 and bottom 5 categories by total revenue to highlight performance divergence.",
        "5. Power BI Visual": "Category Share Treemap & Category Breakdown Table",
        "6. Core Metric / KPI": "<b>Top Category (Health & Beauty): R$ 1.44M | Bottom 10 Categories combined: < R$ 50,000 (<0.3%)</b>",
        "7. Interpretation": "The bottom 30 categories generate negligible volume, creating operational catalog clutter with minimal return.",
        "8. Business Action": "Discontinue vendor onboarding incentives for bottom-tier niche categories and redirect budget to top 10 categories."
    }
    story.append(Paragraph("<b>Q10: Which product categories have the highest and lowest contribution to total sales?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q10_dict, styles))
    story.append(make_sql_card("""(SELECT COALESCE(ct.product_category_name_english, 'Other') AS category, ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue, 'Top Tier' AS tier
 FROM order_items oi JOIN products p ON oi.product_id = p.product_id LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
 GROUP BY 1 ORDER BY revenue DESC LIMIT 3)
UNION ALL
(SELECT COALESCE(ct.product_category_name_english, 'Other'), ROUND(SUM(oi.price + oi.freight_value), 2), 'Bottom Tier'
 FROM order_items oi JOIN products p ON oi.product_id = p.product_id LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
 GROUP BY 1 ORDER BY revenue ASC LIMIT 3);""", styles))
    story.append(Spacer(1, 4))
    story.append(make_callout("Business owners use Page 02 to optimize product catalog strategy, recognizing that freight comprises 14.2% of ticket prices and focusing marketing spend on the 10 core categories that drive 63% of gross platform revenue.", styles))

    # ==========================================================================
    # SECTION 5: DASHBOARD 3 – SELLER & CUSTOMER ANALYSIS (PAGE 5)
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("5. Dashboard Page 03: Seller & Customer Analysis", "Geographic Demographics, Regional Supply vs Demand Flows, Top Merchant Performance & Customer Growth", styles))
    story.append(Spacer(1, 4))

    # Actual Dashboard Screenshot
    if Path(DASHBOARD_IMAGES['page_3']).exists():
        im_p3 = Image(DASHBOARD_IMAGES['page_3'], width=520, height=288)
        story.append(im_p3)
        story.append(Paragraph("<b>Figure 3: Power BI Seller & Customer Analysis Dashboard</b> — Highlights Top Sellers by Revenue, Customers by Geographic State, Seller Regional Concentration Treemap, Monthly Customer Growth, Seller Details, and Geographic Breakdown Table.", styles['ImageCaption']))

    story.append(Paragraph("<b>Visible Dashboard Components & Layout:</b><br/>"
                           "• <b>KPI Cards:</b> Total Sellers (<b>3,095</b>), Total Customers (<b>96K / 96,096</b>), Total Orders (<b>99K</b>), Total Revenue (<b>R$ 15.84M</b>), Average Review Score (<b>4.09</b>), Average Order Value (<b>R$ 160.58</b>).<br/>"
                           "• <b>Visuals:</b> Top Sellers by Total Revenue Bar Chart, Customers by Geographic State Bar Chart (SP dominating), Seller Regional Concentration Treemap, Monthly Customer Growth Line Chart, Seller Details Table, and Geographic Breakdown Table.<br/>"
                           "• <b>Key Insight Banner:</b> 'São Paulo (SP) represents 41.7% of all customers and 37.4% of total revenue. Active seller network spans 3,095 sellers with top seller generating R$ 229.5K. Southeast region drives >70% of volume.'", styles['BodyP']))
    story.append(Spacer(1, 4))

    # 5 Business Questions for Page 3
    story.append(Paragraph("<b>Seller & Customer Analysis — 5 Core Strategic Business Questions:</b>", styles['SubSectionTitle']))

    # Q11
    q11_dict = {
        "1. Business Objective": "Identify the top-earning independent merchants to assess seller revenue concentration and partnership value.",
        "2. Why It Matters": "Protects key revenue channels by identifying the high-volume merchants that drive platform turnover.",
        "3. Required Tables": "<code>sellers</code>, <code>order_items</code>",
        "4. SQL Approach": "Group by `seller_id`, summing line item price and freight, sorting in descending order.",
        "5. Power BI Visual": "Top Sellers by Total Revenue (Horizontal Bar Chart with anonymized seller IDs)",
        "6. Core Metric / KPI": "<b>Top Seller: R$ 249.6K gross revenue (1,156 units sold) | Top 10 sellers average > R$ 150K each</b>",
        "7. Interpretation": "While the merchant network is diverse (3,095 sellers), a core group of top merchants generates high order density.",
        "8. Business Action": "Assign dedicated key-account managers and priority logistics support to the top 25 merchants to prevent churn."
    }
    story.append(Paragraph("<b>Q11: Who are the top-performing sellers based on total revenue generated?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q11_dict, styles))
    story.append(make_sql_card("""SELECT s.seller_id, s.seller_city, s.seller_state, COUNT(oi.order_item_id) AS units_sold,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM sellers s JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state ORDER BY total_revenue DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q12
    q12_dict = {
        "1. Business Objective": "Determine customer geographic density across Brazilian states to map demand concentration.",
        "2. Why It Matters": "Informs regional advertising allocation, localized marketing copy, and carrier route negotiations.",
        "3. Required Tables": "<code>customers</code>",
        "4. SQL Approach": "Count unique customer IDs grouped by `customer_state`, calculating percentage share.",
        "5. Power BI Visual": "Customers by Geographic State (Bar Chart & Geographic Breakdown Table)",
        "6. Core Metric / KPI": "<b>São Paulo (SP): 40,302 customers (41.98%) | Rio de Janeiro (RJ): 12,384 (12.85%) | MG: 11,259 (11.63%)</b>",
        "7. Interpretation": "Over 66% of all consumers are concentrated in just three Southeastern states (SP, RJ, MG).",
        "8. Business Action": "Focus digital ad spend on SP and RJ, while offering targeted shipping discounts in underserved states like Bahia and PR."
    }
    story.append(Paragraph("<b>Q12: Which Brazilian states have the highest number of customers?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q12_dict, styles))
    story.append(make_sql_card("""SELECT customer_state, COUNT(DISTINCT customer_unique_id) AS unique_customers,
       ROUND(COUNT(DISTINCT customer_unique_id) * 100.0 / (SELECT COUNT(DISTINCT customer_unique_id) FROM customers), 2) AS customer_share_pct
FROM customers GROUP BY customer_state ORDER BY unique_customers DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q13
    q13_dict = {
        "1. Business Objective": "Identify the primary commercial regions generating the majority of platform orders and financial revenue.",
        "2. Why It Matters": "Aligns physical logistics capacity and fulfillment hubs with actual geographic consumption centers.",
        "3. Required Tables": "<code>orders</code>, <code>customers</code>, <code>order_items</code>",
        "4. SQL Approach": "Group order items by customer state to compute order count and total gross sales.",
        "5. Power BI Visual": "Geographic Breakdown Table (State, Total Customers, Total Orders, Total Revenue)",
        "6. Core Metric / KPI": "<b>São Paulo alone accounts for R$ 5,921,678.12 (37.38% of total platform revenue) across 41,746 orders</b>",
        "7. Interpretation": "The Southeast region represents over 70% of gross commercial volume, creating extreme operational regional asymmetry.",
        "8. Business Action": "Establish localized same-day delivery networks throughout the greater São Paulo and Rio metropolitan regions."
    }
    story.append(Paragraph("<b>Q13: Which geographical regions contribute the most to total orders and revenue?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q13_dict, styles))
    story.append(make_sql_card("""SELECT c.customer_state, COUNT(DISTINCT o.order_id) AS total_orders,
       ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
       ROUND(SUM(oi.price + oi.freight_value) * 100.0 / (SELECT SUM(price + freight_value) FROM order_items), 2) AS rev_share_pct
FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state ORDER BY total_revenue DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q14
    q14_dict = {
        "1. Business Objective": "Track monthly new customer acquisition trajectories to evaluate platform customer base expansion.",
        "2. Why It Matters": "Assesses marketplace growth health and validates marketing campaign acquisition effectiveness.",
        "3. Required Tables": "<code>customers</code>, <code>orders</code>",
        "4. SQL Approach": "Identify first purchase month per customer unique ID and aggregate monthly new customer cohorts.",
        "5. Power BI Visual": "Monthly Customer Growth (Line Chart showing monthly acquisition ramp-up)",
        "6. Core Metric / KPI": "<b>Monthly acquisitions peaked at >7,000 new customers in November 2017, averaging ~6,000 monthly in 2018</b>",
        "7. Interpretation": "Customer acquisition follows an exponential curve through 2017, establishing a large cumulative base of 96K buyers.",
        "8. Business Action": "Shift strategic focus from pure top-of-funnel acquisition to post-purchase retention and repurchase incentive programs."
    }
    story.append(Paragraph("<b>Q14: How is the customer base growing month over month?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q14_dict, styles))
    story.append(make_sql_card("""WITH first_orders AS (
    SELECT c.customer_unique_id, MIN(TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM')) AS cohort_month
    FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY 1
)
SELECT cohort_month, COUNT(*) AS new_customers FROM first_orders GROUP BY 1 ORDER BY 1;""", styles))
    story.append(Spacer(1, 4))

    # Q15
    q15_dict = {
        "1. Business Objective": "Assess the geographical concentration of Olist's merchant supplier network.",
        "2. Why It Matters": "Supply concentration in one state creates long-distance shipping hurdles when delivering to distant states.",
        "3. Required Tables": "<code>sellers</code>",
        "4. SQL Approach": "Group sellers by `seller_state`, computing merchant count and national percentage share.",
        "5. Power BI Visual": "Seller Regional Concentration (Treemap visual sized by seller count)",
        "6. Core Metric / KPI": "<b>Over 70.8% of all merchants (1,849 sellers) are physically based in São Paulo (SP)</b>",
        "7. Interpretation": "Supplier geography is heavily clustered in São Paulo; fulfilling orders to Northeast/North states requires long-haul transit.",
        "8. Business Action": "Recruit regional merchants in Minas Gerais, Paraná, and Bahia to shorten delivery radiuses for non-SP buyers."
    }
    story.append(Paragraph("<b>Q15: How concentrated is the seller network across different geographical regions?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q15_dict, styles))
    story.append(make_sql_card("""SELECT seller_state, COUNT(*) AS total_sellers,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sellers), 2) AS seller_share_pct
FROM sellers GROUP BY seller_state ORDER BY total_sellers DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))
    story.append(make_callout("Business owners use Page 03 to identify regional expansion opportunities, recognizing that 70% of merchants and 42% of buyers reside in São Paulo, indicating high ROI in establishing regional cross-docking fulfillment centers in the Northeast.", styles))

    # ==========================================================================
    # SECTION 6: DASHBOARD 4 – DELIVERY & CUSTOMER SATISFACTION (PAGE 6)
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("6. Dashboard Page 04: Delivery & Customer Satisfaction", "Fulfillment SLA Diagnostics, Transit Times by State, Review Score Breakdown & Sentiment Correlation", styles))
    story.append(Spacer(1, 4))

    # Actual Dashboard Screenshot
    if Path(DASHBOARD_IMAGES['page_4']).exists():
        im_p4 = Image(DASHBOARD_IMAGES['page_4'], width=520, height=288)
        story.append(im_p4)
        story.append(Paragraph("<b>Figure 4: Power BI Delivery & Customer Satisfaction Dashboard</b> — Displays Review Score Distribution, Orders by State, Order Status Donut, Monthly Delivered Volume, Monthly Satisfaction Trend, and State-Level Delivery SLA Table.", styles['ImageCaption']))

    story.append(Paragraph("<b>Visible Dashboard Components & Layout:</b><br/>"
                           "• <b>KPI Cards:</b> Total Orders (<b>99K</b>), Delivered Orders (<b>96K</b>), Total Customers (<b>96K</b>), Average Review Score (<b>4.09</b>), Total Products (<b>33K</b>), Total Revenue (<b>R$ 15.84M</b>).<br/>"
                           "• <b>Visuals:</b> Review Score Distribution (1-5 Star Bar Chart with massive 5-star peak), Orders by State Bar Chart, Order Status Donut (97.02% Delivered), Monthly Delivered Volume Line Chart, Monthly Satisfaction Trend Line Chart, and Delivery Performance by State Matrix.<br/>"
                           "• <b>Key Insight Banner:</b> '91.89% on-time delivery rate (88,644 on-time orders). Overall customer satisfaction is strong at 4.09 / 5.0 with 57.8% 5-star ratings. Delivery speed directly correlates with high review ratings.'", styles['BodyP']))
    story.append(Spacer(1, 4))

    # 5 Business Questions for Page 4
    story.append(Paragraph("<b>Delivery & Satisfaction — 5 Core Strategic Business Questions:</b>", styles['SubSectionTitle']))

    # Q16
    q16_dict = {
        "1. Business Objective": "Determine the overall fulfillment completion percentage across all customer orders.",
        "2. Why It Matters": "Represents the primary operational health indicator of the marketplace logistics network.",
        "3. Required Tables": "<code>orders</code>",
        "4. SQL Approach": "Calculate the ratio of orders with `order_status = 'delivered'` against total logged orders.",
        "5. Power BI Visual": "Delivered Orders KPI Card & Order Status Donut Chart",
        "6. Core Metric / KPI": "<b>96,478 Delivered Orders out of 99,441 Total Orders (97.02% completion rate)</b>",
        "7. Interpretation": "Logistics fulfillment is exceptionally stable, with only 2.98% of orders in-transit, processing, or canceled.",
        "8. Business Action": "Standardize carrier dispatch automated alerts to monitor in-transit orders approaching SLA thresholds."
    }
    story.append(Paragraph("<b>Q16: What percentage of total orders have been successfully delivered?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q16_dict, styles))
    story.append(make_sql_card("""SELECT COUNT(*) AS total_orders, COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered_orders,
       ROUND(COUNT(*) FILTER (WHERE order_status = 'delivered') * 100.0 / COUNT(*), 2) AS fulfillment_pct
FROM orders;""", styles))
    story.append(Spacer(1, 4))

    # Q17
    q17_dict = {
        "1. Business Objective": "Measure overall platform customer satisfaction and evaluate customer review sentiment.",
        "2. Why It Matters": "Customer satisfaction directly dictates word-of-mouth referral, seller rating trust, and platform retention.",
        "3. Required Tables": "<code>reviews</code>",
        "4. SQL Approach": "Compute arithmetic average of `review_score` across all 99,224 submitted customer reviews.",
        "5. Power BI Visual": "Average Review Score KPI Card (4.09 Large Callout)",
        "6. Core Metric / KPI": "<b>Overall Platform Average Review Score: 4.09 / 5.00 Stars</b>",
        "7. Interpretation": "Platform customer sentiment is healthy, exceeding the e-commerce marketplace benchmark of 4.00 stars.",
        "8. Business Action": "Introduce automated feedback requests for satisfied buyers to amplify positive marketplace seller reviews."
    }
    story.append(Paragraph("<b>Q17: What is the average customer review score, and how satisfied are customers?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q17_dict, styles))
    story.append(make_sql_card("""SELECT ROUND(AVG(review_score), 2) AS avg_review_score, COUNT(*) AS total_reviews FROM reviews;""", styles))
    story.append(Spacer(1, 4))

    # Q18
    q18_dict = {
        "1. Business Objective": "Quantify the proportion of top-tier 5-star ratings versus negative 1-star complaints.",
        "2. Why It Matters": "Identifies rating polarization and quantifies the exact share of highly delighted customers.",
        "3. Required Tables": "<code>reviews</code>",
        "4. SQL Approach": "Group by `review_score` (1 to 5), calculating review volume and percentage distribution.",
        "5. Power BI Visual": "Review Score Distribution (Bar Chart showing dominant 5-star column)",
        "6. Core Metric / KPI": "<b>5-Star Reviews: 57,328 (57.78%) | 1-Star Reviews: 11,424 (11.51%) | 4-Star: 19.29%</b>",
        "7. Interpretation": "Over 77% of reviews award 4 or 5 stars; 1-star reviews are concentrated around delivery delays.",
        "8. Business Action": "Route 1-star review tickets automatically to customer support for rapid appeasement vouchers."
    }
    story.append(Paragraph("<b>Q18: What percentage of customers give a 5-star rating?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q18_dict, styles))
    story.append(make_sql_card("""SELECT review_score, COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM reviews GROUP BY review_score ORDER BY review_score DESC;""", styles))
    story.append(Spacer(1, 4))

    # Q19
    q19_dict = {
        "1. Business Objective": "Benchmark logistics transit speed and on-time arrival performance across Brazilian states.",
        "2. Why It Matters": "Exposes regional logistics bottlenecks and carrier SLA failures across distant federal territories.",
        "3. Required Tables": "<code>orders</code>, <code>customers</code>",
        "4. SQL Approach": "Compute actual transit days (`delivered - purchase`) and on-time percentage per `customer_state`.",
        "5. Power BI Visual": "Delivery Performance by State (Matrix Table with actual vs. estimated days)",
        "6. Core Metric / KPI": "<b>SP: 8.8 avg days (94.11% on-time) | RJ: 14.9 avg days (90.2% on-time) | BA: 15.3 avg days (91.1% on-time)</b>",
        "7. Interpretation": "Intra-state Southeast shipments deliver in ~8 days; Northern states (RR, AP, AM) require 20-28 days transit.",
        "8. Business Action": "Calibrate realistic estimated delivery SLA buffers on checkout for North/Northeast destinations to prevent false expectations."
    }
    story.append(Paragraph("<b>Q19: Which Brazilian states have the highest and lowest delivery performance?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q19_dict, styles))
    story.append(make_sql_card("""SELECT c.customer_state, COUNT(o.order_id) AS orders,
       ROUND(AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400)::NUMERIC, 1) AS actual_days,
       ROUND(COUNT(*) FILTER (WHERE o.order_delivered_customer_date <= o.order_estimated_delivery_date) * 100.0 / COUNT(*), 2) AS on_time_pct
FROM orders o JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state ORDER BY orders DESC LIMIT 5;""", styles))
    story.append(Spacer(1, 4))

    # Q20
    q20_dict = {
        "1. Business Objective": "Correlate delivery delay severity directly with customer satisfaction review scores.",
        "2. Why It Matters": "Mathematically proves that logistics delivery speed is the single greatest driver of customer sentiment.",
        "3. Required Tables": "<code>orders</code>, <code>reviews</code>",
        "4. SQL Approach": "Categorize delivery timeliness (Early >5d, On-Time, Delayed 1-5d, Delayed >5d) and calculate avg review score.",
        "5. Power BI Visual": "Monthly Satisfaction Trend & Timeliness Correlation Breakdown",
        "6. Core Metric / KPI": "<b>Delivered Early: 4.31 Avg Rating (6.5% 1-star) | Delayed >5 Days: 1.35 Avg Rating (78.4% 1-star)</b>",
        "7. Interpretation": "A delivery delay past the promised SLA instantly collapses customer satisfaction from 4.31 to 1.35 stars.",
        "8. Business Action": "Institute carrier penalty clauses for delivery delays exceeding SLA and send proactive delay apology notifications."
    }
    story.append(Paragraph("<b>Q20: How do monthly delivery performance and customer satisfaction change over time?</b>", styles['QuestionHeader']))
    story.append(make_question_table(q20_dict, styles))
    story.append(make_sql_card("""WITH timeliness AS (
    SELECT o.order_id, r.review_score,
           CASE WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On-Time / Early'
                ELSE 'Delayed Past SLA' END AS outcome
    FROM orders o JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
)
SELECT outcome, COUNT(*) AS orders, ROUND(AVG(review_score), 2) AS avg_score,
       ROUND(COUNT(*) FILTER (WHERE review_score = 1) * 100.0 / COUNT(*), 2) AS one_star_pct
FROM timeliness GROUP BY outcome;""", styles))
    story.append(Spacer(1, 4))
    story.append(make_callout("Business owners use Page 04 to safeguard brand reputation, discovering that on-time delivery yields a 4.31 satisfaction rating, while unmitigated delays past SLA cause review scores to plummet to 1.35, proving logistics execution directly controls customer retention.", styles))

    # ==========================================================================
    # FINAL SECTION: PROJECT RESULTS, KEY FINDINGS AND CONCLUSION
    # ==========================================================================
    story.append(PageBreak())
    story.append(make_banner("7. Project Results, Strategic Insights & Conclusion", "Executive Summary of Achievements, Business Findings, Recommendations, Skills & Roadmap", styles))
    story.append(Spacer(1, 6))

    # Final Project Results
    story.append(Paragraph("<b>1. Final Project Results & Deliverables:</b>", styles['SubSectionTitle']))
    story.append(Paragraph("This project successfully architected and delivered an end-to-end Business Intelligence solution that converts 1.48 million raw transactional events into actionable commercial clarity. Deliverables include:<br/>"
                           "• A fully normalized, production-grade <b>PostgreSQL 18 database</b> storing 1.22M cleaned records across 9 relational tables with zero orphan records.<br/>"
                           "• An advanced <b>SQL query suite</b> containing 20 strategic queries answering core commercial, seller, and fulfillment questions.<br/>"
                           "• A high-performance <b>Star-Schema Power BI semantic data model</b> powered by custom DAX measures.<br/>"
                           "• A publication-quality, <b>4-page interactive Power BI dashboard suite</b> designed in an executive navy theme (`Dashboard.pbix`).", styles['BodyP']))

    # Key Business Insights Table
    story.append(Paragraph("<b>2. Key Business Insights Matrix:</b>", styles['SubSectionTitle']))
    insights_data = [
        [Paragraph("<b>Domain</b>", styles['THead']), Paragraph("<b>Key Empirical Finding</b>", styles['THead']), Paragraph("<b>Business Impact & Strategic Meaning</b>", styles['THead'])],
        [Paragraph("<b>Revenue</b>", styles['TCellBold']), Paragraph("R$ 15.84M Gross Revenue across 99,441 orders with an AOV of R$ 160.58.", styles['TCell']), Paragraph("Healthy commercial scale with strong baseline transaction volumes.", styles['TCell'])],
        [Paragraph("<b>Seasonality</b>", styles['TCellBold']), Paragraph("November Black Friday (R$ 1.19M) and May Mother's Day are peak surges.", styles['TCell']), Paragraph("Demand is heavily seasonal; requires proactive carrier buffer contracts.", styles['TCell'])],
        [Paragraph("<b>Categories</b>", styles['TCellBold']), Paragraph("Top 10 categories generate 63% of revenue (Health/Beauty & Watches lead).", styles['TCell']), Paragraph("Pareto concentration confirms high ROI in key category partnerships.", styles['TCell'])],
        [Paragraph("<b>Freight</b>", styles['TCellBold']), Paragraph("Freight contributes 14.2% (R$ 2.25M), exceeding 25% on bulky goods.", styles['TCell']), Paragraph("Shipping cost is a major conversion hurdle for furniture and home goods.", styles['TCell'])],
        [Paragraph("<b>Geography</b>", styles['TCellBold']), Paragraph("São Paulo represents 41.7% of customers, 37.4% of sales, and 70.8% of sellers.", styles['TCell']), Paragraph("Extreme Southeast concentration creates cross-country shipping challenges.", styles['TCell'])],
        [Paragraph("<b>Payments</b>", styles['TCellBold']), Paragraph("Credit card captures 78.3% of revenue with 3.5 avg installments.", styles['TCell']), Paragraph("Financing flexibility is mandatory for Brazilian e-commerce conversion.", styles['TCell'])],
        [Paragraph("<b>Fulfillment</b>", styles['TCellBold']), Paragraph("97.02% order completion rate; 91.89% on-time delivery benchmark.", styles['TCell']), Paragraph("Operations are generally robust, but distant states suffer lead times.", styles['TCell'])],
        [Paragraph("<b>Sentiment</b>", styles['TCellBold']), Paragraph("4.09 / 5.00 average rating with 57.8% 5-star ratings; delays destroy scores.", styles['TCell']), Paragraph("Delays past SLA cause review scores to collapse from 4.31 to 1.35 stars.", styles['TCell'])],
    ]
    t_ins = Table(insights_data, colWidths=[70, 220, 233.27])
    t_ins.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8FAFC')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ins)
    story.append(Spacer(1, 5))

    # Business Recommendations
    story.append(Paragraph("<b>3. Actionable Business Recommendations:</b><br/>"
                           "1. <b>Establish Regional 3PL Cross-Docking Hubs:</b> Pre-position top-selling Health & Beauty and Watches inventory in Bahia (BA) and Pernambuco (PE) to slash Northeast transit times from 21 days to under 5 days.<br/>"
                           "2. <b>Dynamic SLA Calibration at Checkout:</b> Replace static postal buffers with machine learning transit predictions to set accurate delivery expectations and eliminate customer churn.<br/>"
                           "3. <b>Post-Purchase Retention Workflows:</b> With a repeat purchase rate of only 3.12%, establish automated email re-engagement vouchers to build long-term customer lifetime value (LTV).<br/>"
                           "4. <b>Subsidized Freight Thresholds on High-AOV Items:</b> Offer free shipping promotions for orders exceeding R$ 250 in categories where margins can absorb logistics costs.", styles['BodyP']))

    # Skills, Challenges & Future Improvements
    story.append(Paragraph("<b>4. Skills Demonstrated:</b> Advanced SQL (CTEs, Window Functions, Aggregate Joins) • PostgreSQL Database Administration & DDL • Python Data Engineering & Cleaning (Pandas) • Power BI Data Modeling & DAX Calculation • Business Analysis & Stakeholder Reporting • Data Storytelling.", styles['BodyP']))
    story.append(Paragraph("<b>5. Challenges Overcome:</b> Deduplicated 261,831 redundant GPS records without spatial loss; resolved 5-digit Brazilian CEP string truncation; preserved operational null timestamps without skewing delivery metrics; audited composite primary keys to achieve 100% referential integrity.", styles['BodyP']))
    story.append(Paragraph("<b>6. Future Scope:</b> Real-time streaming ETL integration with Apache Kafka, machine learning demand forecasting for peak Black Friday surges, and automated RFM (Recency, Frequency, Monetary) customer segmentation.", styles['BodyP']))

    # Conclusion
    story.append(Paragraph("<b>7. Conclusion:</b><br/>"
                           "This project demonstrates the complete end-to-end analytics lifecycle from raw, noisy transaction data to polished C-suite business intelligence. By uniting data engineering rigor in Python and PostgreSQL with executive visual storytelling in Power BI, the project provides business owners with the exact tools needed to maximize revenue, streamline shipping operations, and protect customer satisfaction.", styles['BodyP']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master Project Documentation PDF generated successfully: {pdf_path.name}")


if __name__ == "__main__":
    build_pdf()
