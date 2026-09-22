import os
from collections import defaultdict
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.config import NiboRoutes

# The reference NIBO reports (relatorios/*_layout.pdf) are landscape A4 - a
# portrait page is too narrow for a 7/8-column table and gets its content
# clipped at the page edge.
PAGE_SIZE = landscape(A4)
MARGIN = 30
PAGE_WIDTH = PAGE_SIZE[0] - 2 * MARGIN

_BASE_STYLES = getSampleStyleSheet()
CELL_STYLE = ParagraphStyle("cell", parent=_BASE_STYLES["Normal"], fontSize=8, leading=10)
HEADER_STYLE = ParagraphStyle("header", parent=CELL_STYLE, fontName="Helvetica-Bold")
COMPANY_STYLE = ParagraphStyle("company", parent=_BASE_STYLES["Normal"], fontSize=13, leading=15)
META_STYLE = ParagraphStyle("meta", parent=_BASE_STYLES["Normal"], fontSize=8, alignment=TA_RIGHT)
SUBTITLE_STYLE = ParagraphStyle("subtitle", parent=_BASE_STYLES["Normal"], fontSize=11, leading=13)

TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
    ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#CCCCCC")),
    ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ("ALIGN", (-2, 0), (-1, -1), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
])

TITLE_BLOCK_STYLE = TableStyle([
    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
])


def format_currency(value: float | None, is_expense: bool) -> str:
    """Format a number as Brazilian currency; expenses are wrapped in parentheses."""
    amount = value or 0
    formatted = f"{abs(amount):,.2f}".translate(str.maketrans(",.", ".,"))
    return f"({formatted})" if is_expense else formatted


def format_date(value: str | None) -> str:
    """Convert a NIBO ISO date/datetime string into DD/MM/YYYY."""
    if not value:
        return ""
    return datetime.fromisoformat(value[:10]).strftime("%d/%m/%Y")


def _wrap_cell(value: Any) -> Paragraph:
    """Wrap a cell value in a Paragraph so long text wraps instead of overflowing the column."""
    return Paragraph("" if value is None else str(value), CELL_STYLE)


# Each entry describes one of the 4 reports: which file/title to use, its
# column headers/widths, how to build a row from a mapped item (see
# src/userful/map_dict.py), and which two columns feed the "Total" row.
# costCenter is unverified against real data - none of the current clients'
# NIBO items have cost centers set, so the column renders empty for them.
REPORT_SPECS: dict[NiboRoutes, dict[str, Any]] = {
    NiboRoutes.CONTAS_A_PAGAR: {
        "file_name": "contas_a_pagar",
        "title": "Contas a pagar",
        "is_expense": True,
        "headers": [
            "Vencimento", "Nome", "Descrição", "Categoria",
            "Centro de custo", "Valor categoria/centro de custo", "Valor em aberto",
        ],
        "col_widths": [70, 140, 180, 120, 100, 90, 81],
        "row": lambda item, is_expense: [
            format_date(item.get("dueDate")),
            item.get("name"),
            item.get("description"),
            item.get("category"),
            item.get("costCenter"),
            format_currency(item.get("categoryValue"), is_expense),
            format_currency(item.get("openValue"), is_expense),
        ],
        "totals": lambda item: (item.get("categoryValue") or 0, item.get("openValue") or 0),
    },
    NiboRoutes.CONTAS_A_RECEBER: {
        "file_name": "contas_a_receber",
        "title": "Contas a receber",
        "is_expense": False,
        "headers": [
            "Vencimento", "Nome", "Descrição", "Categoria",
            "Centro de custo", "Valor categoria/centro de custo", "Valor em aberto",
        ],
        "col_widths": [70, 140, 180, 120, 100, 90, 81],
        "row": lambda item, is_expense: [
            format_date(item.get("dueDate")),
            item.get("name"),
            item.get("description"),
            item.get("category"),
            item.get("costCenter"),
            format_currency(item.get("categoryValue"), is_expense),
            format_currency(item.get("openValue"), is_expense),
        ],
        "totals": lambda item: (item.get("categoryValue") or 0, item.get("openValue") or 0),
    },
    NiboRoutes.CONTAS_PAGAS: {
        "file_name": "contas_pagas",
        "title": "Contas pagas",
        "is_expense": True,
        "headers": [
            "Pagamento", "Nome", "Descrição", "Categoria",
            "Centro de custo", "Conta", "Valor categoria/centro de custo", "Valor pago",
        ],
        "col_widths": [65, 120, 150, 100, 90, 90, 85, 81],
        "row": lambda item, is_expense: [
            format_date(item.get("date")),
            item.get("name"),
            item.get("description"),
            item.get("categories"),
            item.get("costCenter"),
            item.get("account"),
            format_currency(item.get("categoryValue"), is_expense),
            format_currency(item.get("value"), is_expense),
        ],
        "totals": lambda item: (item.get("categoryValue") or 0, item.get("value") or 0),
    },
    NiboRoutes.CONTAS_RECEBIDAS: {
        "file_name": "contas_recebidas",
        "title": "Contas recebidas",
        "is_expense": False,
        "headers": [
            "Recebimento", "Nome", "Descrição", "Categoria",
            "Centro de custo", "Conta", "Valor categoria/centro de custo", "Valor recebido",
        ],
        "col_widths": [65, 120, 150, 100, 90, 90, 85, 81],
        "row": lambda item, is_expense: [
            format_date(item.get("date")),
            item.get("name"),
            item.get("description"),
            item.get("categories"),
            item.get("costCenter"),
            item.get("account"),
            format_currency(item.get("categoryValue"), is_expense),
            format_currency(item.get("value"), is_expense),
        ],
        "totals": lambda item: (item.get("categoryValue") or 0, item.get("value") or 0),
    },
}


def _build_title_block(company_name: str, generated_at: str) -> Table:
    """Build the borderless header bar: company name on the left, timestamp on the right."""
    company = Paragraph(f"<b>{company_name.upper()}</b>", COMPANY_STYLE)
    meta = Paragraph(f"<b>Gerado em:</b> {generated_at}", META_STYLE)
    block = Table([[company, meta]], colWidths=[PAGE_WIDTH * 0.7, PAGE_WIDTH * 0.3])
    block.setStyle(TITLE_BLOCK_STYLE)
    return block


def _build_report(
    items: list[dict[str, Any]],
    spec: dict[str, Any],
    company_name: str,
    generated_at: str,
    file_path: str,
) -> None:
    """Render a single PDF report for one route (one company, one account type)."""
    doc = SimpleDocTemplate(
        file_path,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
    )

    is_expense = spec["is_expense"]
    rows = [[Paragraph(header, HEADER_STYLE) for header in spec["headers"]]]
    total_category_value = 0
    total_final_value = 0
    for item in items:
        rows.append([_wrap_cell(cell) for cell in spec["row"](item, is_expense)])
        category_value, final_value = spec["totals"](item)
        total_category_value += category_value
        total_final_value += final_value

    total_row = ["Total"] + [""] * (len(spec["headers"]) - 3) + [
        format_currency(total_category_value, is_expense),
        format_currency(total_final_value, is_expense),
    ]
    rows.append(total_row)

    table = Table(rows, colWidths=spec["col_widths"], repeatRows=1)
    table.setStyle(TABLE_STYLE)

    doc.build([
        _build_title_block(company_name, generated_at),
        Spacer(1, 6),
        Paragraph(f"<b>{spec['title']}</b>", SUBTITLE_STYLE),
        Spacer(1, 10),
        table,
    ])


def generate_reports(data: list[dict[str, Any]], company_name: str, output_dir: str = "relatorios") -> str:
    """Generate the 4 NIBO reports (contas a pagar/a receber/pagas/recebidas) for one company.

    Groups the already-mapped items (see src/userful/map_dict.py) by route and
    writes one PDF per route into `<output_dir>/<company_name>/`.
    """
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    company_dir = os.path.join(output_dir, company_name.replace(" ", "_"))
    os.makedirs(company_dir, exist_ok=True)
    filename: str = []

    items_by_route: dict[NiboRoutes, list[dict[str, Any]]] = defaultdict(list)
    for item in data:
        if item is not None:
            items_by_route[item["route"]].append(item)

    for route, spec in REPORT_SPECS.items():
        file_path = os.path.join(company_dir, f"{spec['file_name']}.pdf")
        _build_report(items_by_route.get(route, []), spec, company_name, generated_at, file_path)
        filename.append(file_path)

    return filename 