# app/services/pdf.py
from fpdf import FPDF
from typing import List
from app.models.sale import Sale
from app.models.business import Business

def generate_sales_pdf(business: Business, sales: List[Sale], period_label: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"{business.name} - Sales Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # Subtitle
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Period: {period_label}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 10, "Date", border=1)
    pdf.cell(80, 10, "Item Name", border=1)
    pdf.cell(30, 10, "Qty", border=1, align="C")
    pdf.cell(40, 10, "Total (NGN)", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Table Rows
    pdf.set_font("Helvetica", "", 10)
    total_revenue = 0
    for sale in sales:
        date_str = sale.created_at.strftime("%Y-%m-%d")
        pdf.cell(40, 10, date_str, border=1)
        pdf.cell(80, 10, sale.item_name[:35], border=1)
        pdf.cell(30, 10, str(sale.quantity), border=1, align="C")
        pdf.cell(40, 10, f"{sale.total_amount:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
        total_revenue += sale.total_amount
        
    # Total Row
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(150, 10, "TOTAL REVENUE", border=1, align="R")
    pdf.cell(40, 10, f"N {total_revenue:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())