from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "diagrams"

# ---------------------------------------------------------------------------
# Palette and constants
# ---------------------------------------------------------------------------
INK = "0F172A"
MUTED = "475569"
SUBTLE = "64748B"
LINE = "CBD5E1"
SOFT = "F8FAFC"
BLUE = "1D4ED8"
BLUE_DARK = "1E3A8A"
BLUE_SOFT = "EFF6FF"
TEAL = "0F766E"
TEAL_SOFT = "F0FDFA"
AMBER = "B45309"
AMBER_SOFT = "FFFBEB"
ROSE = "BE123C"
ROSE_SOFT = "FFF1F2"
GREEN = "15803D"
GREEN_SOFT = "F0FDF4"
NAVY = "0F172A"
WHITE = "FFFFFF"

PAGE_W = 16.8  # cm, usable width
BODY_FONT = "Arial"
MONO_FONT = "Courier New"

INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def set_run_shading(run, fill: str) -> None:
    rPr = run._element.get_or_add_rPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    rPr.append(shd)


def set_letter_spacing(run, twips: int) -> None:
    rPr = run._element.get_or_add_rPr()
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:val"), str(twips))
    rPr.append(spacing)


def set_cell_shading(cell, fill: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_margins(table, top=70, left=100, bottom=70, right=100) -> None:
    tblPr = table._tbl.tblPr
    for existing in tblPr.findall(qn("w:tblCellMar")):
        tblPr.remove(existing)
    mar = OxmlElement("w:tblCellMar")
    for edge, value in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:w"), str(value))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)


def set_table_borders(table, color=LINE, size=4, inside=True) -> None:
    tblPr = table._tbl.tblPr
    for existing in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(existing)
    borders = OxmlElement("w:tblBorders")
    edges = ["top", "left", "bottom", "right"]
    if inside:
        edges += ["insideH", "insideV"]
    for edge in edges:
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tblPr.append(borders)


def set_table_width(table, width_cm: float) -> None:
    tblPr = table._tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        for existing in tblPr.findall(qn(tag)):
            tblPr.remove(existing)
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), str(int(width_cm * 567)))
    tblW.set(qn("w:type"), "dxa")
    tblPr.append(tblW)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)


def set_repeat_table_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def set_row_cant_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    cantSplit = OxmlElement("w:cantSplit")
    cantSplit.set(qn("w:val"), "true")
    trPr.append(cantSplit)


def add_hyperlink(paragraph, url: str, text: str, color: str = BLUE) -> None:
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(c)
    rPr.append(u)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_field(paragraph, instr: str, placeholder: str = "1") -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text_el = OxmlElement("w:t")
    text_el.text = placeholder
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr_el)
    run._r.append(fld_sep)
    run._r.append(text_el)
    run._r.append(fld_end)


def set_paragraph_bottom_border(paragraph, color=LINE, size=8, space=4) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), str(space))
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


class Builder:
    def __init__(self) -> None:
        self.doc = Document()
        self._setup_page()
        self._setup_styles()
        self._setup_header_footer()
        self._setup_properties()
        self._prev_table = False

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _setup_page(self) -> None:
        section = self.doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.1)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.0)
        section.header_distance = Cm(0.9)
        section.footer_distance = Cm(0.8)
        section.gutter = Cm(0)

    def _setup_styles(self) -> None:
        normal = self.doc.styles["Normal"]
        normal.font.name = BODY_FONT
        normal.font.size = Pt(10.5)
        normal.font.color.rgb = rgb("1F2937")
        normal.paragraph_format.line_spacing = 1.14
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        normal.paragraph_format.widow_control = True

        h1 = self.doc.styles["Heading 1"]
        h1.font.name = BODY_FONT
        h1.font.size = Pt(18)
        h1.font.bold = True
        h1.font.color.rgb = rgb(INK)
        h1.paragraph_format.space_before = Pt(4)
        h1.paragraph_format.space_after = Pt(8)
        h1.paragraph_format.keep_with_next = True
        h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        h2 = self.doc.styles["Heading 2"]
        h2.font.name = BODY_FONT
        h2.font.size = Pt(13)
        h2.font.bold = True
        h2.font.color.rgb = rgb(BLUE)
        h2.paragraph_format.space_before = Pt(13)
        h2.paragraph_format.space_after = Pt(4)
        h2.paragraph_format.keep_with_next = True
        h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        h3 = self.doc.styles["Heading 3"]
        h3.font.name = BODY_FONT
        h3.font.size = Pt(10.8)
        h3.font.bold = True
        h3.font.color.rgb = rgb("334155")
        h3.paragraph_format.space_before = Pt(9)
        h3.paragraph_format.space_after = Pt(3)
        h3.paragraph_format.keep_with_next = True
        h3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        for style_name in ("List Bullet", "List Bullet 2"):
            st = self.doc.styles[style_name]
            st.font.name = BODY_FONT
            st.font.size = Pt(10.2)
            st.paragraph_format.space_after = Pt(3)
            st.paragraph_format.line_spacing = 1.08

        caption = self.doc.styles["Caption"]
        caption.font.name = BODY_FONT
        caption.font.size = Pt(8.6)
        caption.font.italic = True
        caption.font.color.rgb = rgb(SUBTLE)
        caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption.paragraph_format.space_before = Pt(3)
        caption.paragraph_format.space_after = Pt(10)

        # Word's default heading styles carry a theme font; force it.
        for name in ("Heading 1", "Heading 2", "Heading 3"):
            rPr = self.doc.styles[name].element.get_or_add_rPr()
            rFonts = rPr.find(qn("w:rFonts"))
            if rFonts is None:
                rFonts = OxmlElement("w:rFonts")
                rPr.append(rFonts)
            for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rFonts.set(qn(attr), BODY_FONT)

    def _setup_header_footer(self) -> None:
        section = self.doc.sections[0]
        header = section.header
        p = header.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run("Production truck monitoring — MVP plan and architecture  ·  v0.1  ·  October 2026")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        set_paragraph_bottom_border(p, LINE, 6, 4)

        footer = section.footer
        p = footer.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Internal project document  ·  Page ")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        add_field(p, "PAGE", "1")
        r = p.add_run(" of ")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        add_field(p, "NUMPAGES", "1")
        for run in p.runs:
            run.font.name = BODY_FONT
            run.font.size = Pt(8)
            run.font.color.rgb = rgb(SUBTLE)

    def _setup_properties(self) -> None:
        cp = self.doc.core_properties
        cp.title = "Production truck monitoring — MVP plan and architecture"
        cp.subject = "File-first React MVP for displaying truck positions on a map"
        cp.author = "Project team"
        cp.last_modified_by = "Project team"
        cp.category = "Architecture / MVP plan"
        cp.comments = "MVP 0.1. File-backed snapshot, Leaflet map, Magma-ready adapter seam."
        cp.keywords = "React, TypeScript, Leaflet, Magma, MVP, positioning, telemetry"
        cp.created = datetime(2026, 10, 28, 16, 0)
        cp.modified = datetime(2026, 10, 28, 16, 0)
        cp.revision = 1

        settings = self.doc.settings.element
        update = OxmlElement("w:updateFields")
        update.set(qn("w:val"), "true")
        settings.append(update)

    # ------------------------------------------------------------------
    # Text primitives
    # ------------------------------------------------------------------
    def _before_table_block(self) -> None:
        """Keep two adjacent tables from merging, without a trailing spacer."""
        if self._prev_table:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            p.paragraph_format.line_spacing = Pt(1)
            r = p.add_run(" ")
            r.font.size = Pt(1)
        self._prev_table = False

    def _add_inline(self, paragraph, text: str, size: float | None = None,
                    color: str | None = None, bold: bool = False,
                    italic: bool = False) -> None:
        for token in INLINE_RE.split(text):
            if not token:
                continue
            if token.startswith("**") and token.endswith("**"):
                run = paragraph.add_run(token[2:-2])
                run.bold = True
                if size:
                    run.font.size = Pt(size)
                if color:
                    run.font.color.rgb = rgb(color)
            elif token.startswith("`") and token.endswith("`"):
                run = paragraph.add_run(token[1:-1])
                run.font.name = MONO_FONT
                run.font.size = Pt((size or 10.2) - 0.7)
                run.font.color.rgb = rgb("0F172A")
                set_run_shading(run, "F1F5F9")
            else:
                run = paragraph.add_run(token)
                run.bold = bold
                run.italic = italic
                if size:
                    run.font.size = Pt(size)
                if color:
                    run.font.color.rgb = rgb(color)

    def p(self, text: str = "", size: float | None = None, color: str | None = None,
          bold: bool = False, italic: bool = False,
          align: WD_ALIGN_PARAGRAPH | None = None,
          space_after: float | None = None, space_before: float | None = None,
          keep_with_next: bool = False, style: str | None = None) -> object:
        self._prev_table = False
        paragraph = self.doc.add_paragraph(style=style) if style else self.doc.add_paragraph()
        self._add_inline(paragraph, text, size=size, color=color, bold=bold, italic=italic)
        pf = paragraph.paragraph_format
        if align is not None:
            pf.alignment = align
        if space_after is not None:
            pf.space_after = Pt(space_after)
        if space_before is not None:
            pf.space_before = Pt(space_before)
        if keep_with_next:
            pf.keep_with_next = True
        return paragraph

    def h1(self, text: str, new_page: bool = True) -> None:
        self._prev_table = False
        heading = self.doc.add_heading(text, level=1)
        if new_page:
            heading.paragraph_format.page_break_before = True
        set_paragraph_bottom_border(heading, "D6DEE8", 6, 5)
        heading.paragraph_format.space_before = Pt(0 if new_page else 4)

    def h2(self, text: str) -> None:
        self._prev_table = False
        self.doc.add_heading(text, level=2)

    def h3(self, text: str) -> None:
        self._prev_table = False
        self.doc.add_heading(text, level=3)

    def bullets(self, items: list[str], level: int = 1) -> None:
        self._prev_table = False
        style = "List Bullet" if level == 1 else "List Bullet 2"
        for item in items:
            p = self.doc.add_paragraph(style=style)
            self._add_inline(p, item)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.left_indent = Cm(0.55 if level == 1 else 1.1)
            p.paragraph_format.first_line_indent = Cm(-0.3)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    def numbered(self, items: list[str], start: int = 1) -> None:
        self._prev_table = False
        for i, item in enumerate(items, start=start):
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.65)
            p.paragraph_format.first_line_indent = Cm(-0.55)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(f"{i}.\t")
            r.bold = True
            r.font.color.rgb = rgb(BLUE)
            p.paragraph_format.tab_stops.add_tab_stop(Cm(0.65))
            self._add_inline(p, item)

    def step(self, number: int, title: str, body: str) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.first_line_indent = Cm(-0.8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"Step {number}. ")
        r.bold = True
        r.font.color.rgb = rgb(BLUE)
        self._add_inline(p, f"**{title}**")
        self.p(body, space_after=5)

    def page_break(self) -> None:
        self.doc.add_page_break()

    # ------------------------------------------------------------------
    # Tables, callouts, code, figures
    # ------------------------------------------------------------------
    def table(self, headers: list[str], rows: list[list[str]], widths: list[float],
              font_size: float = 8.7, header_fill: str = NAVY,
              first_col_bold: bool = False, zebra: bool = True,
              align_center_cols: list[int] | None = None) -> object:
        self._before_table_block()
        table = self.doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_width(table, sum(widths))
        for i, width in enumerate(widths):
            table.columns[i].width = Cm(width)
        set_table_borders(table, LINE, 4)
        set_cell_margins(table, 64, 90, 64, 90)

        hdr = table.rows[0]
        set_repeat_table_header(hdr)
        set_row_cant_split(hdr)
        for i, header in enumerate(headers):
            cell = hdr.cells[i]
            cell.width = Cm(widths[i])
            set_cell_shading(cell, header_fill)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(header)
            r.bold = True
            r.font.size = Pt(font_size)
            r.font.name = BODY_FONT
            r.font.color.rgb = rgb(WHITE)

        for row_index, row in enumerate(rows):
            tr = table.add_row()
            set_row_cant_split(tr)
            for col_index, value in enumerate(row):
                cell = tr.cells[col_index]
                cell.width = Cm(widths[col_index])
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                if zebra and row_index % 2 == 1:
                    set_cell_shading(cell, SOFT)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER
                    if align_center_cols and col_index in align_center_cols
                    else WD_ALIGN_PARAGRAPH.LEFT
                )
                self._add_inline(p, str(value), size=font_size,
                                 bold=(first_col_bold and col_index == 0))
        self._prev_table = True
        return table

    def callout(self, title: str, body: str, kind: str = "info") -> None:
        self._before_table_block()
        fills = {
            "info": (BLUE_SOFT, BLUE),
            "warning": (AMBER_SOFT, AMBER),
            "success": (GREEN_SOFT, GREEN),
            "danger": (ROSE_SOFT, ROSE),
        }
        fill, accent = fills[kind]
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_width(table, PAGE_W)
        set_cell_margins(table, 110, 150, 110, 150)
        cell = table.rows[0].cells[0]
        cell.width = Cm(PAGE_W)
        set_cell_shading(cell, fill)
        # Remove all borders, then add a thick left border.
        tblPr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            if edge == "left":
                el.set(qn("w:val"), "single")
                el.set(qn("w:sz"), "24")
                el.set(qn("w:color"), accent)
            else:
                el.set(qn("w:val"), "nil")
            el.set(qn("w:space"), "0")
            borders.append(el)
        tblPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title)
        r.bold = True
        r.font.size = Pt(9.4)
        r.font.color.rgb = rgb(accent)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.08
        self._add_inline(p2, body, size=9.1, color="334155")
        set_row_cant_split(table.rows[0])
        self._prev_table = True

    def code(self, code: str, caption: str | None = None) -> None:
        self._before_table_block()
        if caption:
            p = self.p(caption, size=8.2, color=SUBTLE, italic=True, space_after=2,
                       keep_with_next=True)
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_width(table, PAGE_W)
        set_table_borders(table, "E2E8F0", 4, inside=False)
        set_cell_margins(table, 100, 130, 100, 130)
        cell = table.rows[0].cells[0]
        cell.width = Cm(PAGE_W)
        set_cell_shading(cell, "F8FAFC")
        lines = code.strip("\n").split("\n")
        first = True
        for line in lines:
            p = cell.paragraphs[0] if first else cell.add_paragraph()
            first = False
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            p.paragraph_format.line_spacing = Pt(9.4)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(line if line else " ")
            r.font.name = MONO_FONT
            r.font.size = Pt(7.4)
            r.font.color.rgb = rgb("0F172A")
        self._prev_table = True

    def figure(self, filename: str, caption: str, alt: str, width: float = 16.4) -> None:
        self._prev_table = False
        p = self.doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run()
        run.add_picture(str(FIG / filename), width=Cm(width))
        try:
            inline = self.doc.inline_shapes[-1]
            docPr = inline._inline.docPr
            docPr.set("descr", alt)
            docPr.set("title", caption[:120])
        except Exception:
            pass
        cap = self.doc.add_paragraph(caption, style="Caption")
        cap.paragraph_format.keep_with_next = False

    # ------------------------------------------------------------------
    # Front matter
    # ------------------------------------------------------------------
    def cover(self) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_table_width(table, PAGE_W)
        set_cell_margins(table, 260, 260, 240, 240)
        cell = table.rows[0].cells[0]
        cell.width = Cm(PAGE_W)
        set_cell_shading(cell, NAVY)
        table.rows[0].height = Cm(7.4)
        table.rows[0].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        # Remove borders.
        tblPr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "nil")
            borders.append(el)
        tblPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(18)
        r = p.add_run("PROJECT BLUEPRINT  /  MVP 0.1")
        r.font.name = BODY_FONT
        r.font.size = Pt(8.5)
        r.bold = True
        r.font.color.rgb = rgb("93C5FD")
        set_letter_spacing(r, 30)

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 0.95
        r = p.add_run("Production truck")
        r.font.name = BODY_FONT
        r.font.size = Pt(31)
        r.bold = True
        r.font.color.rgb = rgb(WHITE)

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = 0.95
        r = p.add_run("monitoring")
        r.font.name = BODY_FONT
        r.font.size = Pt(31)
        r.bold = True
        r.font.color.rgb = rgb(WHITE)

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run("MVP plan and architecture")
        r.font.name = BODY_FONT
        r.font.size = Pt(18)
        r.font.color.rgb = rgb("E2E8F0")

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run("A file-first React map, designed to grow into Magma")
        r.font.name = BODY_FONT
        r.font.size = Pt(10.5)
        r.font.color.rgb = rgb("CBD5E1")

        # Blue accent bar
        accent = self.doc.add_table(rows=1, cols=1)
        accent.alignment = WD_TABLE_ALIGNMENT.CENTER
        accent.autofit = False
        set_table_width(accent, PAGE_W)
        cell2 = accent.rows[0].cells[0]
        cell2.width = Cm(PAGE_W)
        set_cell_shading(cell2, BLUE)
        accent.rows[0].height = Cm(0.16)
        accent.rows[0].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        cell2.paragraphs[0].paragraph_format.space_after = Pt(0)
        cell2.paragraphs[0].add_run(" ").font.size = Pt(1)

        self.p("", size=5, space_after=4)

        meta = [
            ("Document type", "MVP project plan and architecture"),
            ("Status", "Draft for review"),
            ("Version / date", "0.1  ·  28 October 2026"),
            ("Audience", "Project team, frontend developer, integrator"),
            ("MVP scope", "Coordinates from a file, shown on a map"),
        ]
        t = self.doc.add_table(rows=0, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.autofit = False
        set_table_width(t, PAGE_W)
        t.columns[0].width = Cm(3.7)
        t.columns[1].width = Cm(13.1)
        set_cell_margins(t, 70, 0, 70, 100)
        tblPr = t._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "nil")
            borders.append(el)
        tblPr.append(borders)
        for label, value in meta:
            row = t.add_row()
            row.cells[0].width = Cm(3.7)
            row.cells[1].width = Cm(13.1)
            p = row.cells[0].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(label)
            r.font.name = BODY_FONT
            r.font.size = Pt(8.3)
            r.font.color.rgb = rgb(SUBTLE)
            p = row.cells[1].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(value)
            r.font.name = BODY_FONT
            r.font.size = Pt(9.2)
            r.font.color.rgb = rgb("1F2937")

        self.p("", size=8, space_after=4)
        self.callout(
            "The one idea to remember",
            "The file is not the architecture. The architecture is a stable snapshot contract plus a replaceable "
            "source adapter. Replace the file with an API or Magma later without rewriting the map, the domain model, "
            "or the screen.",
            "info",
        )

        self.p("", size=18, space_after=0)
        p = self.p("October 2026  ·  Internal project document", size=8.8, color=SUBTLE, space_after=0)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self.page_break()

    def contents(self) -> None:
        p = self.p("Contents", size=24, color=INK, bold=True, space_after=2)
        set_paragraph_bottom_border(p, BLUE, 12, 6)
        self.p("", size=4, space_after=6)

        p = self.doc.add_paragraph()
        run = p.add_run()
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = 'TOC \\o "1-2" \\h \\z \\u'
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        placeholder = OxmlElement("w:t")
        placeholder.text = "Right-click here and choose Update Field to build the table of contents."
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        run._r.append(fld_begin)
        run._r.append(instr)
        run._r.append(fld_sep)
        run._r.append(placeholder)
        run._r.append(fld_end)

        self.p("", size=6, space_after=6)
        self.callout(
            "How to use the table of contents",
            "This is a live Word field. Right-click it and choose Update Field → Update entire table after opening "
            "the document. Page numbers are generated by Word, not typed by hand.",
            "warning",
        )

        self.p("", size=4, space_after=2)
        self.p("How to read this document", size=12.5, color=INK, bold=True, space_after=4)
        self.table(
            ["Reader", "Read first", "Why"],
            [
                ["Manager / customer", "Executive summary; chapters 1–2, 10–11", "Scope, acceptance criteria, effort, risks"],
                ["Frontend developer", "Chapters 3–9 and 13", "Architecture, contract, map, step-by-step build"],
                ["Integrator / backend", "Chapters 4, 6, 8, 12", "Data contract, file handover, Magma evolution"],
                ["Reviewer", "2.4, 9.3, 11", "Acceptance criteria, definition of done, risk register"],
            ],
            [3.8, 5.8, 7.2],
            font_size=8.6,
            first_col_bold=True,
        )
        self.page_break()

    # ------------------------------------------------------------------
    # Executive summary
    # ------------------------------------------------------------------
    def executive_summary(self) -> None:
        self.h1("Executive summary", new_page=False)
        self.p(
            "This document defines MVP 0.1 of a dispatcher-facing web application that shows production trucks on a "
            "map. The positions are **not computed in the browser**. They arrive as a ready-to-use JSON snapshot "
            "produced by a positioning service. The MVP's job is to prove the user experience and freeze the contract "
            "between the positioning world and the UI. Magma, MQTT, RSSI measurements, and the multilateration engine "
            "are deliberately outside this increment."
        )
        self.p(
            "The architecture is a small React single-page application with one replaceable seam: `FleetRepository`. "
            "The first implementation reads `/data/fleet.snapshot.json` every second. A later implementation can read "
            "the same contract from an HTTP API or a WebSocket without changing the map, the domain model, or the "
            "screen. This is what makes the solution **Magma-ready without making the MVP Magma-dependent**."
        )
        self.p(
            "Expected effort is **8–10 working days for one frontend developer**, or two calendar weeks including "
            "review and demo. The deliverable is a working demo, a versioned data contract, a test suite, deployment "
            "instructions, and a backlog for the next phase. No backend, database, or radio hardware is required to "
            "finish MVP 0.1."
        )

        self.table(
            ["At a glance", "MVP 0.1"],
            [
                ["Product goal", "A dispatcher opens one page and sees every production truck as a dot on a site map."],
                ["In scope", "JSON snapshot → polling → validation → map with stations, truck dots, status, selection, error and stale states."],
                ["Out of scope", "RSSI processing, multilateration, Magma, MQTT, database, history, auth, geofences, station CRUD."],
                ["Primary user", "Dispatcher / shop-floor manager; secondary user is the integrator who produces the file."],
                ["Stack", "React + TypeScript + Vite · TanStack Query · Zod · Leaflet + OpenStreetMap."],
                ["Key decision", "One snapshot contract and one source port; file adapter now, API/WebSocket adapter later."],
                ["Duration", "8–10 working days; two calendar weeks with review and buffer."],
                ["Success signal", "A five-truck demo that moves, survives a broken file, and passes the acceptance checklist."],
            ],
            [3.8, 13.0],
            font_size=8.8,
            first_col_bold=True,
        )

        self.callout(
            "What this document is not",
            "It is not a positioning-algorithm specification, a Magma installation guide, or a production operations "
            "manual. It is the plan and architecture for the first working increment, plus the seams that let the next "
            "increments happen without a rewrite.",
            "warning",
        )

        self.p("Five decisions that shape everything", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.numbered([
            "**File-first, not backend-first.** The first increment proves the screen and the contract without waiting for radio hardware, Magma, or a database.",
            "**Contract-first.** The JSON schema is reviewed and versioned before the first component is written. The producer and the UI can then evolve independently.",
            "**One port, one adapter.** `FleetRepository` is the only seam between the UI and the data source. It is small enough to understand in five minutes.",
            "**Map is not the source of truth.** Leaflet draws what the domain gives it. Replacing Leaflet with MapLibre or Yandex Maps must not touch the data layer.",
            "**Fail soft and honest.** A broken or stale file never blanks the map. The UI keeps the last good snapshot and says exactly how old it is.",
        ])

        self.p("What the reader should remember", size=12.5, color=INK, bold=True, space_before=2, space_after=4)
        self.bullets([
            "The browser never reads an arbitrary local file; the snapshot is served by the same web server as the app.",
            "The snapshot is a **full picture**, not a stream of deltas. Polling a full snapshot is the simplest reliable MVP.",
            "TypeScript types disappear at runtime; **Zod validates** what actually arrives.",
            "The map is a renderer. All data fetching, validation, and staleness rules live outside it.",
            "Magma is a future **server-side** data source, never a browser dependency.",
        ])

        self.p("MVP success metrics", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.table(
            ["Metric", "Target", "What it proves"],
            [
                ["Time to first useful map", "≤ 2.5 s on the corporate LAN", "The demo is not fragile"],
                ["Snapshot freshness", "≤ 2 s from `generatedAt` to the screen", "The dispatcher can trust “live”"],
                ["Fleet capacity", "100 trucks at 1 Hz", "Headroom for the pilot"],
                ["Failure transparency", "Every tested failure has a visible state", "No silent stale data"],
                ["Source swap effort", "≤ 1 day to add an HTTP adapter", "The architecture is real, not theoretical"],
            ],
            [4.4, 5.2, 7.2],
            font_size=8.5,
            first_col_bold=True,
        )


    # ------------------------------------------------------------------
    # Chapter 1
    # ------------------------------------------------------------------
    def chapter_1(self) -> None:
        self.h1("1. The problem and the MVP bet")
        self.p(
            "A production site is a poor environment for satellite navigation. Workshops, warehouses, metal structures, "
            "and roofs block or reflect GPS and GLONASS signals. The project therefore uses its own radio infrastructure: "
            "two or more base stations with precisely surveyed coordinates, and trucks whose on-board modem measures the "
            "signal it receives from those stations."
        )
        self.p(
            "The physical idea is simple. A radio signal gets weaker with distance. If the attenuation model for the site "
            "is known, each signal-strength measurement becomes an estimate of the distance between the truck and one base "
            "station. With three or more stations, the intersection of those distances gives a position by "
            "**multilateration**. With two stations the result is weaker and may be ambiguous, so the positioning engine "
            "uses additional constraints or falls back to a lower-accuracy method."
        )
        self.p(
            "The browser's role begins **after** that coordinate exists. The browser does not read radio measurements, "
            "does not calibrate the propagation model, and does not solve the multilateration problem. It receives a "
            "coordinate, a timestamp, and a quality indicator, and turns them into a dot on a map that a dispatcher can "
            "trust."
        )

        self.h2("1.1 What the dispatcher actually needs")
        self.p(
            "The product reference is the familiar map of moving buses: a site plan, coloured dots, a selected object, "
            "and an honest indication of when the data was last refreshed. The dispatcher does not need a physics "
            "dashboard. They need to answer four questions in a few seconds:"
        )
        self.bullets([
            "**Where is each truck now?** A dot on the map, with a name or asset code.",
            "**Is the data current?** A visible last-update time and a stale-data warning when the producer stops.",
            "**How much should I trust this dot?** An accuracy radius, a positioning method, and a status colour.",
            "**Which truck is this?** A click reveals the asset card and the last known details.",
        ])
        self.p(
            "This is why the MVP is a **visualisation product**, not a positioning product. The positioning project has "
            "its own risks and its own test bench. The visualisation project can start now, against a file, and be ready "
            "when the first real coordinate arrives."
        )

        self.h2("1.2 Why file-first is the right first bet")
        self.p(
            "A file sounds modest, but it is a deliberate architectural choice. It removes every dependency that could "
            "delay the first demo: no backend, no database, no radio hardware, no Magma deployment, no MQTT broker. At "
            "the same time it forces the team to define the one thing that will survive every later change: the snapshot "
            "contract."
        )
        self.numbered([
            "**It de-risks the unknown.** The radio and Magma work can proceed in parallel; the UI team is not blocked.",
            "**It produces a demo in days, not months.** The customer sees moving dots and can give feedback on the screen while the physics is still being calibrated.",
            "**It creates a golden fixture.** The same file becomes the test fixture for the repository, the map, the error states, and the future API contract.",
            "**It exposes the integration boundary early.** The producer learns what the consumer needs; the consumer learns what the producer can supply.",
            "**It makes the later swap cheap.** A file adapter and an HTTP adapter implement the same five-line interface.",
        ])

        self.h2("1.3 Assumptions and interpretations")
        self.p(
            "The request contains one ambiguous term: “magama”. This document interprets it as **Magma**, the open-source "
            "mobile core project (Access Gateway + Orchestrator) used to run a private LTE network. If the team meant a "
            "different framework, the architecture still applies: Magma is only the future source of events and "
            "measurements, and it sits behind the same server-side adapter."
        )
        self.table(
            ["Assumption", "Why it matters", "Confirm before build"],
            [
                ["“Magama” means Magma, the mobile core", "Explains the future integration path and the vocabulary in chapter 12", "Project lead / network team"],
                ["Coordinates are WGS84 latitude and longitude", "Leaflet and the file contract use decimal degrees; local metres need conversion upstream", "Positioning engineer"],
                ["An external process writes the snapshot file", "The browser cannot read an arbitrary path on disk; the file must be served by the web server", "Integrator"],
                ["Refresh rate is about 1 Hz; up to 100 trucks", "Sets polling interval, file size, and rendering strategy", "Product owner"],
                ["The site has internet access for map tiles during the demo", "OpenStreetMap tiles are an external dependency; a site plan image is the offline fallback", "IT / security"],
                ["The MVP is deployed inside the corporate perimeter", "No auth in MVP; the whole app is protected by network access or a reverse proxy", "Security"],
                ["UI copy is English for the first demo", "The architecture is language-neutral; Russian labels are a copy change, not a redesign", "Customer"],
            ],
            [4.6, 7.4, 4.8],
            font_size=8.4,
            first_col_bold=True,
        )

        self.callout(
            "Two stations are not a full fix",
            "Two distance circles usually intersect at two points, and real measurements are noisy. A two-station solution "
            "can be usable only with extra constraints (site geometry, previous position, timing advance, serving-cell "
            "sector). The UI must therefore show the method and the accuracy radius, not a falsely precise dot.",
            "warning",
        )

        self.h2("1.4 Definition of done in one sentence")
        self.callout(
            "MVP 0.1 is done when…",
            "…a dispatcher opens one page, sees every truck from the served snapshot as a correctly placed dot, can click "
            "a dot to identify the truck, and can tell from the screen whether the data is live, stale, or broken — "
            "without a backend, database, or Magma connection.",
            "success",
        )

        self.h2("1.5 If an assumption is wrong")
        self.table(
            ["Change", "Impact on MVP", "Response"],
            [
                ["Coordinates arrive as local metres (x/y), not lat/lon", "Dots will be offset or outside the map", "Convert to WGS84 in the producer; if impossible, add one documented conversion module and a site origin"],
                ["Yandex Maps is mandatory", "Leaflet is not the required renderer", "Keep the map component isolated; add a Yandex map adapter after the MVP; do not couple data to Leaflet"],
                ["The site is fully offline", "Public OSM tiles will not load", "Use a site-plan image overlay or a local tile server; dots still work on a blank background"],
                ["Fleet grows to 1,000+ trucks", "A 1 Hz full snapshot and DOM markers become heavy", "Move to an API/WebSocket and a canvas/cluster layer; the contract stays"],
                ["Magma must be connected in the first sprint", "Adds network, credentials, and backend work", "Treat it as Phase 2; do not put Magma in the browser to save time"],
            ],
            [4.8, 5.4, 6.6],
            font_size=8.4,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Chapter 2
    # ------------------------------------------------------------------
    def chapter_2(self) -> None:
        self.h1("2. MVP scope and acceptance criteria")
        self.p(
            "Scope is a promise. Everything in this chapter is demonstrated at the MVP review; everything outside it is "
            "explicitly deferred, even if it looks easy. The boundary is drawn so that the team can finish a trustworthy "
            "screen without waiting for the radio stack."
        )

        self.h2("2.1 In scope")
        self.table(
            ["Capability", "MVP behaviour", "Why it is included"],
            [
                ["Static React application", "One page, production build, served by Nginx or any static host", "The delivery vehicle"],
                ["Site map", "Leaflet map centred on the site, OSM tiles or a site-plan image overlay", "The dispatcher's mental model"],
                ["Base station markers", "Known stations shown with names and status", "Reference points and coverage context"],
                ["Truck dots", "One dot per truck, coloured by status, positioned by lat/lon", "The core user value"],
                ["Snapshot polling", "Fetch the JSON file every 1 s; keep the last good snapshot", "Movement without a backend"],
                ["Selection and details", "Click a dot or list row; show name, coordinates, accuracy, method, last update", "Identify and judge the object"],
                ["Accuracy and method", "Optional accuracy circle and human-readable method label", "Honest uncertainty, no false precision"],
                ["Data health", "Live / stale / refresh error / fatal error / empty / partial-invalid states", "Trust and debuggability"],
                ["Validation and diagnostics", "Zod envelope + per-record validation; skipped records counted", "Bad data must not blank the map"],
                ["Sample data and docs", "Versioned example snapshot, schema, runbook, test checklist", "Handover and future integration"],
            ],
            [4.0, 8.0, 4.8],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("2.2 Out of scope")
        self.table(
            ["Deferred item", "Why it is not in MVP 0.1", "Where it lands"],
            [
                ["RSSI / RSRP / RSRQ processing", "Belongs to the positioning engine, not the UI", "Phase 2"],
                ["Multilateration and Kalman filtering", "Requires calibration data and a radio test bench", "Phase 2"],
                ["Magma, AGW, Orchestrator, SIM management", "Adds infrastructure and credentials; not needed to prove the screen", "Phase 2"],
                ["MQTT broker and on-board agents", "Hardware-dependent", "Phase 2"],
                ["Database, history, tracks, playback", "A full snapshot is enough for live dots", "Phase 3"],
                ["Authentication and roles", "MVP is deployed inside the perimeter", "Phase 3"],
                ["Station CRUD and calibration UI", "Stations are read-only in the snapshot", "Phase 3"],
                ["Geofences, alerts, notifications", "Requires rules and an event model", "Phase 3"],
                ["Mobile app, 3D, indoor map", "Not needed for the first dispatcher screen", "Post-MVP"],
                ["High availability and multi-site", "A demo and a pilot are single-site", "Production"],
            ],
            [4.6, 7.2, 5.0],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("2.3 User stories")
        self.table(
            ["ID", "Story", "Accepted when"],
            [
                ["US-01", "As a dispatcher, I open the page and see all trucks from the snapshot on the site map.", "Every valid truck has a dot; stations are visible; the map is centred on the site."],
                ["US-02", "As a dispatcher, I can tell whether the picture is current.", "The screen shows the last update time and a stale banner when the producer stops."],
                ["US-03", "As a dispatcher, I click a truck and identify it.", "A details card shows name, coordinates, accuracy, method, and timestamp."],
                ["US-04", "As a dispatcher, I can find a truck in a list without hunting on the map.", "A keyboard-accessible list selects the same object as the map."],
                ["US-05", "As an integrator, I replace the file with a new one and see the dots move.", "No page reload is required; the next poll picks up the new snapshot."],
                ["US-06", "As a developer, I can replace the file adapter with an API adapter without touching the screen.", "The map imports only the domain type and a repository port, not the file adapter."],
                ["US-07", "As a reviewer, I can see what went wrong with bad data.", "Invalid records are counted; a fatal envelope error has a readable message and a retry."],
            ],
            [1.5, 8.6, 6.7],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("2.4 Acceptance criteria")
        self.p(
            "These are the demo checks. They are written as Given/When/Then so that they can become automated tests "
            "without translation."
        )
        self.table(
            ["#", "Given / When / Then", "Verified by"],
            [
                ["AC-01", "Given a valid snapshot with 3 stations and 5 trucks, when the page loads, then 3 station markers and 5 truck dots appear within 2 s.", "Manual + E2E"],
                ["AC-02", "Given the file is replaced with new coordinates, when the next poll completes, then the dots move without a page reload.", "Manual + integration"],
                ["AC-03", "Given a dispatcher clicks a truck dot, then the details card shows its name, coordinates, accuracy, method, and last update.", "Component"],
                ["AC-04", "Given one truck record has an invalid latitude, when the snapshot is loaded, then the other trucks still render and the UI reports one skipped record.", "Unit + component"],
                ["AC-05", "Given the file is missing or returns HTTP 404 on first load, then a fatal error card explains the problem and offers Retry.", "Component"],
                ["AC-06", "Given a successful load followed by a failed refresh, then the last good dots remain and a non-blocking banner says the refresh failed.", "Integration"],
                ["AC-07", "Given the snapshot is older than the stale threshold, then a stale banner appears and the dots are visibly de-emphasised.", "Unit + component"],
                ["AC-08", "Given 100 trucks at 1 Hz, then pan and zoom remain responsive and the update does not freeze the main thread.", "Performance check"],
                ["AC-09", "Given map tiles are unavailable, then the dots, stations, legend, and details still render on a blank map background.", "Manual"],
                ["AC-10", "Given keyboard-only navigation, then the truck list can select a truck and the details card updates.", "Manual + a11y check"],
            ],
            [1.3, 12.0, 3.5],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("2.5 Non-functional requirements")
        self.table(
            ["Area", "MVP target", "How it is checked"],
            [
                ["Freshness", "Poll every 1 s; stale warning after 10 s without a new snapshot", "Fake timers in tests; manual file stop"],
                ["Capacity", "100 trucks and 20 stations on one screen", "Synthetic snapshot; performance profile"],
                ["Initial load", "Useful map within 2.5 s on a corporate LAN", "Production build + throttled network"],
                ["Update cost", "One poll cycle under 50 ms of main-thread work for 100 trucks", "Performance panel"],
                ["Bundle", "Initial JS under 300 KB gzip (Leaflet included)", "`vite build` report"],
                ["Browsers", "Latest Chrome, Edge, Firefox, Safari; no Internet Explorer", "Manual smoke test"],
                ["Accessibility", "Keyboard list, visible focus, contrast, status not by colour alone", "Manual + axe spot check"],
                ["Security", "No secrets in the bundle; no direct Magma access; app behind perimeter auth", "Code review + network check"],
                ["Observability", "On-screen data-health panel: source, last fetch, generatedAt, counts, skipped records", "Manual"],
            ],
            [3.0, 8.2, 5.6],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("2.6 Constraints and deliberate omissions")
        self.bullets([
            "**No backend in MVP 0.1.** The static server is the only server. This is a constraint, not an accident.",
            "**No database.** History and playback are later; live dots do not need persistence.",
            "**No auth in the application.** The whole app is placed behind the corporate perimeter or a reverse-proxy login.",
            "**No write operations.** Stations and trucks are read-only; the file is the only input.",
            "**No arbitrary local file access.** The snapshot is served from the same origin as the app.",
            "**No secrets in the frontend.** Vite environment variables are public; Magma credentials never go there.",
            "**No silent data loss.** Invalid records are surfaced as diagnostics, not swallowed.",
        ])

        self.h2("2.7 Scope change rule")
        self.callout(
            "If it cannot be demonstrated in the MVP demo, it is not in MVP 0.1",
            "New requests go to the post-MVP backlog with an estimate. The only exception is a correctness issue in the "
            "data contract or a safety/security problem. This rule protects the two-week delivery window and keeps the "
            "architecture honest.",
            "danger",
        )

    # ------------------------------------------------------------------
    # Chapter 3
    # ------------------------------------------------------------------
    def chapter_3(self) -> None:
        self.h1("3. Architecture principles")
        self.p(
            "The architecture is intentionally small. Flexibility here does not mean many layers, microservices, or "
            "generic abstractions. It means that the places most likely to change — the data source and the map library "
            "— are isolated behind narrow seams, while everything else stays simple and direct."
        )

        self.table(
            ["Principle", "How it appears in the code", "Review question"],
            [
                ["The contract is the product", "One versioned `FleetSnapshot` schema; no ad-hoc fetch shapes in components", "Can a new producer implement this without reading React code?"],
                ["Dependencies point inward", "Domain imports no React, Leaflet, fetch, or file APIs", "Does `src/domain` compile in a plain Node test?"],
                ["One port, one adapter now", "`FleetRepository` with `JsonFileFleetRepository`", "Can the file be replaced by a mock in a test in one line?"],
                ["Fail soft, never lie", "Last good snapshot is kept; stale/error banners; no fake zero positions", "What does the screen say when the producer stops?"],
                ["Map is a renderer", "`FleetMap` receives data and callbacks; Leaflet imports stay in one folder", "Can the map library change without touching the repository?"],
                ["Boring, observable code", "TanStack Query, Zod, standard fetch, one diagnostics panel", "Can a new developer explain the data flow in ten minutes?"],
                ["Build for the next step, not the next year", "No backend, DB, auth, or generic plugin system in MVP", "Is this abstraction already used twice, or is it speculative?"],
            ],
            [4.3, 7.4, 5.1],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("3.1 The flexibility test")
        self.p(
            "Architecture is judged by the changes it makes cheap. Before calling the MVP done, run these five tests. "
            "They are more useful than a diagram review because they exercise the seams."
        )
        self.numbered([
            "**Source swap.** Replace `JsonFileFleetRepository` with an in-memory mock. The page must render the same data with no component changes.",
            "**Transport swap.** Add an `HttpFleetRepository` that fetches `/api/v1/fleet/snapshot`. Only the composition root should change.",
            "**Renderer swap.** Replace Leaflet with a stub map component that renders a `<ul>` of truck names. The repository, schema, and page state must not change.",
            "**Contract extension.** Add an optional `zone` field to the file. Old files must still load; the new field appears in details when present.",
            "**Failure drill.** Rename the file, corrupt one record, and set `generatedAt` two minutes in the past. The map must keep working and explain each condition.",
        ])

        self.h2("3.2 What “flexible” does not mean")
        self.bullets([
            "It does not mean a generic `DataSource<T>` that can fetch anything. The domain has exactly one snapshot shape.",
            "It does not mean a plugin system for map providers. There is one map component and one Leaflet folder; a second provider is added when it is actually needed.",
            "It does not mean Redux, RxJS, or an event bus. TanStack Query owns server state; React owns local UI state.",
            "It does not mean a backend “just in case”. The file adapter is the backend for MVP 0.1.",
            "It does not mean abstracting every function. Pure helpers are tested directly; only volatile boundaries get ports.",
        ])

        self.h2("3.3 Decision log at a glance")
        self.table(
            ["ADR", "Decision", "Consequence"],
            [
                ["ADR-001", "File-backed static SPA for MVP 0.1", "No backend; fastest demo; file is a temporary transport"],
                ["ADR-002", "`FleetRepository` port with a file adapter", "Source can change without touching the UI"],
                ["ADR-003", "Leaflet + OpenStreetMap for the map", "No API key; open licence; easy markers and circles"],
                ["ADR-004", "WGS84 lat/lon is the canonical UI contract", "No geodesy in components; local metres converted upstream"],
                ["ADR-005", "JSON Schema v1 + Zod at the boundary", "Runtime safety; versioned evolution"],
                ["ADR-006", "1 Hz polling, not WebSocket, in MVP", "Simple, debuggable, proxy-friendly; upgrade later"],
                ["ADR-007", "No database or history in MVP", "Smaller scope; live dots only"],
                ["ADR-008", "Magma only server-side in Phase 2", "No credentials or core APIs in the browser"],
            ],
            [1.8, 7.4, 7.6],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "The full ADR entries, including context and alternatives, are in Appendix C. The table above is the "
            "one-screen version for architecture reviews."
        )

        self.p("Design review checklist", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.table(
            ["Question", "Pass condition"],
            [
                ["Can a different team implement the producer from chapter 6 alone?", "Yes, without reading React code"],
                ["Can the file source be replaced with a mock in a test?", "One constructor change; no UI edits"],
                ["Does the domain compile without a DOM or Leaflet?", "Yes; pure TypeScript tests pass"],
                ["Is every fetch/validation decision outside the map component?", "`FleetMap` receives data and callbacks only"],
                ["Does a broken file leave the last good picture on screen?", "Yes, with a visible banner and timestamp"],
            ],
            [9.0, 7.8],
            font_size=8.5,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Chapter 4
    # ------------------------------------------------------------------
    def chapter_4(self) -> None:
        self.h1("4. System context and data flow")
        self.p(
            "MVP 0.1 has four moving parts: a producer that writes the snapshot, a static server that serves the app and "
            "the snapshot, a browser that polls and validates, and a map that draws. There is no backend service and no "
            "database. The simplicity is the point: every remaining part can be tested in isolation."
        )

        self.h2("4.1 Current context")
        self.figure(
            "fig1-context.png",
            "Figure 1. MVP context: the browser reads one atomic JSON snapshot from the same static server that serves the app.",
            "Diagram: a coordinate producer writes fleet.snapshot.json; a static server serves the React app and the snapshot; the browser polls, validates with Zod, and renders with Leaflet; OpenStreetMap provides tiles.",
        )
        self.p(
            "The producer is drawn outside the MVP boundary because it already exists in a different form: a "
            "positioning script, a simulator, or a future backend. The MVP owns the file format, the polling loop, the "
            "validation, and the screen. It does not own the radio physics."
        )

        self.h2("4.2 One polling cycle")
        self.figure(
            "fig3-sequence.png",
            "Figure 3. One polling cycle: fetch, validate, render; on failure, keep the last good snapshot and explain.",
            "Sequence diagram: producer writes an atomic file; browser fetches it every second; Zod validates the envelope and records; Leaflet updates markers; on error the last good snapshot is kept and a banner is shown.",
        )
        self.p(
            "The loop is deliberately boring. A full snapshot arrives every second, is validated, and replaces the "
            "previous snapshot atomically in the query cache. There are no deltas to merge, no sequence numbers to track, "
            "and no reconnect protocol. If a poll fails, the previous snapshot stays on screen and the UI reports the "
            "failure."
        )

        self.h2("4.3 The data path step by step")
        self.step(1, "The producer writes a complete snapshot",
                  "A script or service writes `site + baseStations + trucks` to a temporary file and renames it over "
                  "`fleet.snapshot.json`. The rename is atomic on the same filesystem, so the browser never reads a "
                  "half-written file.")
        self.step(2, "The static server serves the file",
                  "Nginx (production) or Vite (development) serves the React build and `/data/fleet.snapshot.json` from "
                  "the same origin. `Cache-Control: no-store` prevents a proxy from returning yesterday's positions.")
        self.step(3, "The browser polls on a timer",
                  "TanStack Query calls the repository every second. The request carries a cache-busting query parameter "
                  "as a second line of defence against aggressive caches.")
        self.step(4, "The repository parses and validates",
                  "`JSON.parse` is wrapped in a typed error. Zod validates the envelope first; then each station and truck "
                  "record is validated individually. Invalid records are skipped and counted.")
        self.step(5, "The domain snapshot replaces the previous one",
                  "The query cache stores the last successful `FleetLoadResult`. The map receives a stable domain object, "
                  "not raw JSON.")
        self.step(6, "The map renders the new positions",
                  "Leaflet updates existing markers by stable truck ID. Stations are drawn once per snapshot; the accuracy "
                  "circle is drawn only for the selected truck.")
        self.step(7, "The UI reports data health",
                  "The header shows the last successful fetch and the snapshot's `generatedAt`. If the producer stops, the "
                  "snapshot becomes stale even though the HTTP request still succeeds.")
        self.step(8, "Failure keeps the last good picture",
                  "On a network or schema error with existing data, the map stays and a non-blocking banner appears. On a "
                  "first-load failure, a fatal error card explains what to check and offers Retry.")

        self.h2("4.4 Why the browser cannot read an arbitrary local file")
        self.p(
            "A common first instinct is to put the JSON file next to the project and call `fetch('C:\\\\positions.json')` "
            "or `fs.readFile`. Neither works in a normal browser. The browser is sandboxed: a web page cannot read an "
            "arbitrary path on the user's disk, and `fs` is a Node.js API that does not exist in the browser bundle."
        )
        self.p(
            "There are legitimate alternatives, but each has a cost. The MVP chooses the simplest one that supports "
            "automatic refresh: the file is placed in the web server's public directory and fetched over HTTP from the "
            "same origin."
        )
        self.table(
            ["Option", "How it works", "Verdict for MVP"],
            [
                ["Static file served by the web server", "`public/data/fleet.snapshot.json` → `GET /data/...`", "**Chosen.** Same origin, automatic refresh, no permissions, easy to deploy."],
                ["File input / drag-and-drop", "User selects a local file; `FileReader` reads it", "Good for manual inspection; bad for a live wall display because it needs a user action."],
                ["File System Access API", "Browser asks for a directory handle and watches a file", "Chrome-only, permission prompts, fragile for kiosks; not a cross-browser MVP."],
                ["Minimal backend API", "Server reads the file and exposes JSON", "Right long-term; unnecessary for MVP and adds deployment work."],
                ["Direct Magma / database call", "Browser authenticates to the core", "**Never.** Credentials, CORS, security, and coupling make this unacceptable."],
            ],
            [4.6, 6.3, 5.9],
            font_size=8.4,
            first_col_bold=True,
        )

        self.callout(
            "The file path is a URL, not a disk path",
            "In the app, the source is `${import.meta.env.BASE_URL}data/fleet.snapshot.json`. With a base path such as "
            "`/fleet/`, this resolves to `/fleet/data/fleet.snapshot.json`. Hard-coding `/data/...` is the most common "
            "cause of a 404 after deployment.",
            "warning",
        )

        self.h2("4.5 What the browser must never do")
        self.bullets([
            "Call Magma Orchestrator, AGW, MQTT, or a database directly.",
            "Hold API keys, SIM credentials, database passwords, or service tokens. Everything in a Vite bundle is public.",
            "Compute positions from raw RSSI. That logic belongs to the positioning engine and must be testable without a browser.",
            "Invent a position when data is missing. A grey last-known dot with a timestamp is better than a fake live dot.",
            "Trust a successful HTTP 200. A stale or malformed file can still arrive with status 200.",
        ])

        self.h2("4.6 The contract is the architecture")
        self.p(
            "The most important line in this document is not a React component; it is the shape of `FleetSnapshot`. If "
            "that shape is stable, the producer can be a script, an API, Magma, or a simulator, and the UI does not care. "
            "If that shape is unstable, no amount of component abstraction will save the project."
        )


    # ------------------------------------------------------------------
    # Chapter 5
    # ------------------------------------------------------------------
    def chapter_5(self) -> None:
        self.h1("5. Frontend architecture")
        self.p(
            "The frontend is a React + TypeScript single-page application. It has four kinds of code: the domain model, "
            "the data adapter, the application hooks, and the presentation. The dependency rule is simple: outer layers "
            "may import inner layers, never the other way around. The domain is the centre and has no framework imports."
        )
        self.figure(
            "fig2-layers.png",
            "Figure 2. Four layers and one port. The domain is independent; the file adapter and Leaflet are replaceable edges.",
            "Layered diagram: presentation FleetMapPage, application useFleetSnapshot, domain FleetSnapshot and Zod schemas, infrastructure JsonFileFleetRepository and Leaflet adapter; a FleetRepository port connects application and infrastructure.",
        )

        self.h2("5.1 Folder structure")
        self.code(
            """web/
  public/
    data/
      fleet.snapshot.json          # served, updated by the producer
      fleet.snapshot.example.json  # committed sample, used in tests
  src/
    app/
      App.tsx                      # composition root
      providers.tsx                # QueryClient, error boundary
      config.ts                    # base URL, stale thresholds
    domain/
      fleet.ts                     # FleetSnapshot, Truck, Station types
      fleet.schema.ts              # Zod envelope + record schemas
      geo.ts                       # coordinate helpers (pure)
      staleness.ts                 # age and status rules (pure)
    data/
      fleet-repository.ts          # the port + result types
      json-file-fleet-repository.ts# the only file adapter
      errors.ts                    # typed source errors
    features/
      fleet-map/
        FleetMapPage.tsx           # page composition, selection state
        components/
          FleetMap.tsx             # Leaflet canvas
          TruckMarker.tsx          # memoised dot
          StationMarker.tsx        # station marker
          TruckDetails.tsx         # selected truck card
          StatusBanner.tsx         # live / stale / error
          DataHealth.tsx           # diagnostics popover
          Legend.tsx
        hooks/
          useFleetSnapshot.ts      # polling + cache
        model/
          selectors.ts             # derived lists and counts
    shared/
      ui/                          # Button, Badge, Panel
      lib/                         # time, formatting, assertNever
    styles/
      app.css
      map.css
  package.json
  vite.config.ts
  tsconfig.json""",
            "Proposed folder structure. The exact names can change; the dependency direction must not.",
        )

        self.h2("5.2 Module responsibilities")
        self.table(
            ["Module", "Owns", "Must not do"],
            [
                ["`domain/`", "Types, Zod schemas, pure staleness and coordinate rules", "Import React, Leaflet, fetch, or browser APIs"],
                ["`data/`", "Implement the repository port; fetch, parse, validate, normalise errors", "Render UI or know about selected truck"],
                ["`features/fleet-map/hooks`", "Polling, caching, derived data, retry policy", "Parse raw JSON or draw markers"],
                ["`features/fleet-map/components`", "Map, markers, details, banners, legend", "Call `fetch` directly or know the file URL"],
                ["`app/`", "Wire concrete adapter, providers, global error boundary", "Contain business rules"],
                ["`shared/`", "Reusable presentational primitives and pure helpers", "Know about trucks, stations, or the map"],
            ],
            [4.0, 7.0, 5.8],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("5.3 The port: FleetRepository")
        self.p(
            "The port is the only contract between the application and the data source. It is deliberately smaller than a "
            "typical “API client”: one method, one result, one error type."
        )
        self.code(
            """// src/data/fleet-repository.ts
import type { FleetSnapshot } from '../domain/fleet';

export interface SourceDiagnostic {
  level: 'warning' | 'error';
  code: 'invalid-truck' | 'invalid-station' | 'duplicate-id' | 'clock-skew';
  message: string;
  recordIndex?: number;
}

export interface FleetLoadResult {
  snapshot: FleetSnapshot;
  diagnostics: SourceDiagnostic[];
}

export interface FleetRepository {
  loadSnapshot(options?: { signal?: AbortSignal }): Promise<FleetLoadResult>;
}""",
            "The port returns a validated snapshot plus non-fatal diagnostics. The UI never sees raw JSON.",
        )
        self.p(
            "`FleetLoadResult` is intentionally not just `FleetSnapshot`. A file can be 95% valid: four trucks are fine, "
            "one has a broken latitude. Throwing away the whole snapshot would be worse than rendering four trucks and "
            "showing “1 record skipped”. Diagnostics make that behaviour explicit."
        )

        self.h2("5.4 The file adapter")
        self.p(
            "The adapter is the only place that knows the file URL, the HTTP method, the cache headers, and the JSON "
            "parser. If the transport changes, this is the file that changes."
        )
        self.code(
            """// src/data/json-file-fleet-repository.ts
import { parseFleetSnapshot } from '../domain/fleet.schema';
import { FleetSourceError } from './errors';
import type { FleetLoadResult, FleetRepository } from './fleet-repository';

export class JsonFileFleetRepository implements FleetRepository {
  constructor(private readonly url: string) {}

  async loadSnapshot({ signal }: { signal?: AbortSignal } = {}): Promise<FleetLoadResult> {
    let response: Response;
    try {
      response = await fetch(`${this.url}?t=${Date.now()}`, {
        signal,
        cache: 'no-store',
        headers: { Accept: 'application/json' },
      });
    } catch (cause) {
      throw new FleetSourceError('network', 'Cannot reach the snapshot file', cause);
    }

    if (!response.ok) {
      throw new FleetSourceError('http', `Snapshot returned HTTP ${response.status}`);
    }

    let json: unknown;
    try {
      json = await response.json();
    } catch (cause) {
      throw new FleetSourceError('invalid-json', 'Snapshot is not valid JSON', cause);
    }

    return parseFleetSnapshot(json);
  }
}""",
            "The adapter maps transport failures to typed errors; it does not decide how the UI should display them.",
        )

        self.h2("5.5 Validation and partial failure")
        self.p(
            "TypeScript is erased at build time. A JSON file from another process can contain anything, so the boundary "
            "must validate at runtime. Zod is used in two stages: the envelope is fatal, individual records are not."
        )
        self.code(
            """// src/domain/fleet.schema.ts (shape, simplified)
const envelopeSchema = z.object({
  schemaVersion: z.string().regex(/^1\\.\\d+$/, 'Unsupported schema version'),
  generatedAt: isoDate,
  site: siteSchema,
  baseStations: z.array(z.unknown()),
  trucks: z.array(z.unknown()),
});

export function parseFleetSnapshot(raw: unknown): FleetLoadResult {
  const envelope = envelopeSchema.safeParse(raw);
  if (!envelope.success) {
    throw new FleetSourceError('schema', 'Snapshot envelope is invalid', envelope.error);
  }

  const diagnostics: SourceDiagnostic[] = [];
  const stations = parseRecords(envelope.data.baseStations, stationSchema, 'invalid-station', diagnostics);
  const trucks = parseRecords(envelope.data.trucks, truckSchema, 'invalid-truck', diagnostics);

  return {
    snapshot: { ...envelope.data, baseStations: stations, trucks: dedupeById(trucks, diagnostics) },
    diagnostics,
  };
}""",
            "Envelope errors fail the load; record errors are collected. This is what “fail soft” means in code.",
        )
        self.callout(
            "Validate the version before the records",
            "If a producer ships schema 2.0, the app should say “This file uses a newer contract” rather than a hundred "
            "confusing field errors. A major-version check is cheaper and kinder than deep validation.",
            "warning",
        )

        self.h2("5.6 Polling and server state")
        self.p(
            "TanStack Query owns the server state: fetching, retries, caching, and background refresh. The hook is small "
            "on purpose. Components do not use `setInterval`; they read the query result and render."
        )
        self.code(
            """// src/features/fleet-map/hooks/useFleetSnapshot.ts
import { keepPreviousData, useQuery } from '@tanstack/react-query';

export function useFleetSnapshot(repository: FleetRepository) {
  return useQuery({
    queryKey: ['fleet-snapshot'],
    queryFn: ({ signal }) => repository.loadSnapshot({ signal }),
    refetchInterval: 1000,
    refetchIntervalInBackground: false,
    staleTime: 0,
    retry: 1,
    placeholderData: keepPreviousData,
  });
}""",
            "One query, one polling interval. On error, the previous data stays available; the page decides how to present it.",
        )
        self.bullets([
            "`refetchIntervalInBackground: false` avoids polling a hidden tab forever; the map refreshes when the dispatcher returns.",
            "`retry: 1` avoids a retry storm on a missing file; the next scheduled poll is the real retry.",
            "`staleTime: 0` is correct because every snapshot is a new picture.",
            "`keepPreviousData` is what lets the map survive a failed refresh without a white flash.",
        ])

        self.h2("5.7 Selection and UI state")
        self.p(
            "Only one piece of state is truly local: which truck is selected. It belongs to `FleetMapPage` and is passed "
            "down to the map and the details panel. For MVP, `useState<string | null>` is enough. If shareable links are "
            "needed, move it to the URL (`?truck=t-01`) without changing the components."
        )
        self.callout(
            "Do not put server data in a global store",
            "Copying the snapshot into Redux or Zustand creates a second source of truth and a synchronization bug. The "
            "query cache is the server state; React state is the selection and panel visibility.",
            "warning",
        )

        self.h2("5.8 Dependency rules")
        self.bullets([
            "`domain` imports only TypeScript and Zod. It compiles in a plain Node test with no DOM.",
            "`data` imports `domain` and browser `fetch`; it never imports React or Leaflet.",
            "`features` imports `domain`, `data` types, and shared UI; it never imports a concrete adapter.",
            "`app` imports the concrete adapter and wires it into the provider. This is the only composition point.",
            "Components import the `FleetSnapshot` type, not `JsonFileFleetRepository`.",
        ])
        self.p(
            "These rules can be enforced with ESLint `import/no-restricted-paths` or `dependency-cruiser`. A simple code "
            "review checklist is enough for a two-week MVP, but an automated rule pays off as soon as a second developer "
            "joins."
        )

        self.h2("5.9 What we intentionally do not abstract")
        self.table(
            ["Not abstracted", "Why", "When to revisit"],
            [
                ["HTTP client", "One `fetch` call; a wrapper adds indirection without value", "When auth, retries, or multiple endpoints appear"],
                ["Map provider", "One Leaflet component; a provider interface would be speculative", "When a second renderer (MapLibre/Yandex) is actually required"],
                ["Form/state library", "One selection state; React is enough", "When URL state, filters, and panels multiply"],
                ["Generic data source", "There is one domain shape", "Never; add a second port if a second shape appears"],
            ],
            [4.4, 7.2, 5.2],
            font_size=8.4,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Chapter 6
    # ------------------------------------------------------------------
    def chapter_6(self) -> None:
        self.h1("6. The snapshot data contract")
        self.p(
            "The contract is a single JSON object called a **snapshot**. It contains the site, the base stations, and the "
            "trucks at one moment in time. It is complete, not incremental: a consumer can render the whole screen from "
            "one file without keeping previous state."
        )

        self.h2("6.1 Design goals")
        self.bullets([
            "**Human-readable.** An engineer can open the file and understand it without a schema browser.",
            "**Complete.** One file is enough to draw the screen; no join with another file is required.",
            "**Atomic.** The producer replaces the whole file; the consumer never merges partial updates.",
            "**Versioned.** A breaking change is visible in `schemaVersion`, not discovered in production.",
            "**Forgiving.** Unknown fields are ignored; invalid records are skipped, not fatal to the whole screen.",
            "**Producer-friendly.** A Python script, a Node service, or a future backend can write it with standard libraries.",
        ])

        self.h2("6.2 Top-level fields")
        self.table(
            ["Field", "Type", "Required", "Rules and meaning"],
            [
                ["`schemaVersion`", "string", "yes", "`1.x` for this contract. Major mismatch is a fatal, explicit error."],
                ["`generatedAt`", "ISO 8601 string", "yes", "When the producer created this snapshot, UTC with `Z` or an offset."],
                ["`site`", "object", "yes", "Site identity, map centre, default zoom, optional time zone."],
                ["`baseStations`", "array", "yes", "0 or more station objects. Unknown stations are still drawn if coordinates are valid."],
                ["`trucks`", "array", "yes", "0 or more truck objects. An empty array is a valid empty state."],
            ],
            [3.4, 3.1, 2.2, 8.1],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("6.3 Site object")
        self.table(
            ["Field", "Type", "Required", "Rules"],
            [
                ["`id`", "string", "yes", "Stable site identifier, e.g. `plant-1`."],
                ["`name`", "string", "yes", "Human-readable name shown in the header."],
                ["`center.lat`", "number", "yes", "WGS84 latitude, −90…90."],
                ["`center.lon`", "number", "yes", "WGS84 longitude, −180…180."],
                ["`defaultZoom`", "integer", "yes", "Leaflet zoom, 2…22; 16–18 is typical for a factory."],
                ["`timeZone`", "IANA string", "no", "e.g. `Europe/Moscow`; used for absolute time display. Default: browser time zone."],
                ["`map`", "object", "no", "Optional map mode: `osm`, `image`, or `blank`; image bounds for a site plan."],
            ],
            [3.1, 2.8, 2.2, 8.7],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("6.4 Base station object")
        self.table(
            ["Field", "Type", "Required", "Rules"],
            [
                ["`id`", "string", "yes", "Stable and unique within the snapshot, e.g. `bs-01`."],
                ["`name`", "string", "yes", "Label shown on the map, e.g. `BS-01 / North gate`."],
                ["`lat`, `lon`", "number", "yes", "WGS84, same CRS as trucks; 6 decimal places are enough."],
                ["`status`", "enum", "yes", "`online`, `offline`, or `maintenance`."],
                ["`heightM`", "number", "no", "Antenna height in metres; not used for 2D display, useful for future diagnostics."],
            ],
            [3.1, 2.8, 2.2, 8.7],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("6.5 Truck object")
        self.table(
            ["Field", "Type", "Required", "Rules"],
            [
                ["`id`", "string", "yes", "Stable asset ID, unique in the snapshot. Never use the array index."],
                ["`name`", "string", "no", "Display name; fall back to `id`."],
                ["`lat`, `lon`", "number", "yes", "WGS84 position; finite numbers within valid ranges."],
                ["`updatedAt`", "ISO 8601 string", "yes", "When this truck's position was measured, not when the file was written."],
                ["`status`", "enum", "yes", "`moving`, `idle`, `offline`, or `unknown`."],
                ["`accuracyM`", "number", "no", "Estimated 1-sigma radius in metres, ≥ 0. Absent means “unknown”, not zero."],
                ["`method`", "string", "no", "`rssi-multilateration`, `cell-id`, `timing-advance`, etc. Unknown values are displayed raw."],
                ["`speedMps`", "number", "no", "Metres per second, ≥ 0. Optional; useful in details."],
                ["`headingDeg`", "number", "no", "0 ≤ value < 360; 0 = north, clockwise."],
                ["`zone`", "string", "no", "Optional site zone label for future grouping."],
                ["`batteryPct`", "number", "no", "0…100; optional and not required for the map."],
            ],
            [3.0, 3.0, 2.2, 8.6],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("6.6 A complete example")
        self.p(
            "The snippet below is a valid snapshot with three stations and four trucks. The full starter file is "
            "`web/public/data/fleet.snapshot.example.json`; the committed live file is the same shape."
        )
        self.code(
            """{
  "schemaVersion": "1.0",
  "generatedAt": "2026-10-28T13:38:30.000Z",
  "site": {
    "id": "plant-1",
    "name": "Plant 1 — Assembly and logistics",
    "center": { "lat": 55.75580, "lon": 37.61730 },
    "defaultZoom": 17,
    "timeZone": "Europe/Moscow",
    "map": { "mode": "osm" }
  },
  "baseStations": [
    { "id": "bs-01", "name": "BS-01 / North gate", "lat": 55.75620, "lon": 37.61680, "status": "online" },
    { "id": "bs-02", "name": "BS-02 / Warehouse",  "lat": 55.75540, "lon": 37.61810, "status": "online" },
    { "id": "bs-03", "name": "BS-03 / Workshop",   "lat": 55.75600, "lon": 37.61790, "status": "maintenance" }
  ],
  "trucks": [
    {
      "id": "truck-01", "name": "Truck 01",
      "lat": 55.75590, "lon": 37.61710,
      "updatedAt": "2026-10-28T13:38:28.000Z",
      "status": "moving", "accuracyM": 18.5,
      "method": "rssi-multilateration",
      "speedMps": 0.8, "headingDeg": 92
    },
    {
      "id": "truck-02", "name": "Truck 02",
      "lat": 55.75560, "lon": 37.61760,
      "updatedAt": "2026-10-28T13:38:29.000Z",
      "status": "idle", "accuracyM": 12.0,
      "method": "rssi-multilateration"
    },
    {
      "id": "truck-03", "name": "Truck 03",
      "lat": 55.75610, "lon": 37.61800,
      "updatedAt": "2026-10-28T13:38:27.000Z",
      "status": "offline", "accuracyM": 45.0,
      "method": "cell-id"
    },
    {
      "id": "truck-04", "name": "Truck 04",
      "lat": 55.75575, "lon": 37.61695,
      "updatedAt": "2026-10-28T13:38:30.000Z",
      "status": "moving", "accuracyM": 22.0,
      "method": "rssi-multilateration"
    }
  ]
}""",
            "A complete snapshot. Note that `generatedAt` and each `updatedAt` are separate: the file can be fresh while one truck is stale.",
        )

        self.h2("6.7 Validation rules")
        self.table(
            ["Rule", "Envelope failure", "Record failure"],
            [
                ["`schemaVersion` matches `1.x`", "Fatal: unsupported contract", "n/a"],
                ["`generatedAt` parses as ISO 8601", "Fatal: cannot judge freshness", "n/a"],
                ["`site` has id, name, valid centre, zoom 2…22", "Fatal: cannot place the map", "n/a"],
                ["`baseStations` is an array", "Fatal: contract violation", "Invalid station skipped and counted"],
                ["`trucks` is an array", "Fatal: contract violation", "Invalid truck skipped and counted"],
                ["`id` is non-empty and unique", "n/a", "Duplicate or empty record skipped and counted"],
                ["`lat`/`lon` are finite and in range", "n/a", "Record skipped and counted"],
                ["`updatedAt` parses; not more than 5 min in the future", "n/a", "Record kept with a clock-skew warning"],
                ["`accuracyM` is finite and ≥ 0", "n/a", "Record kept, accuracy treated as unknown"],
                ["`status` is one of four values", "n/a", "Record kept, status set to `unknown`"],
            ],
            [6.0, 5.2, 5.6],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("6.8 Error policy")
        self.table(
            ["Condition", "Behaviour", "What the user sees"],
            [
                ["File missing / HTTP 404", "Fatal on first load; keep previous data on later polls", "Error card with URL and Retry, or a non-blocking banner"],
                ["Invalid JSON", "Fatal for this poll; keep previous data", "“Snapshot is not valid JSON” + last good time"],
                ["Envelope schema invalid", "Fatal for this poll; keep previous data", "“Contract mismatch” + first Zod issue"],
                ["One invalid truck", "Skip only that record", "“1 record skipped” in data health"],
                ["Duplicate truck ID", "Keep the first, skip the duplicate", "“1 duplicate ID” in data health"],
                ["`generatedAt` old", "Keep data, mark snapshot stale", "Amber stale banner with age"],
                ["Clock skew > 5 min", "Keep data, mark warning", "Small warning in data health"],
                ["Empty `trucks`", "Valid empty snapshot", "Empty state: “No trucks in the snapshot”"],
            ],
            [5.0, 5.8, 6.0],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("6.9 Coordinates and units")
        self.p(
            "The canonical UI contract is **WGS84 latitude and longitude in decimal degrees**. This is what Leaflet "
            "expects and what a future API will return. Local site coordinates in metres are excellent for the "
            "positioning math, but they must not leak into the UI contract: a component cannot know the site origin, the "
            "projection, or the rotation of the site plan."
        )
        self.table(
            ["Quantity", "Unit", "Convention"],
            [
                ["Latitude, longitude", "decimal degrees", "WGS84; 6 decimal places ≈ 0.11 m; 7 is plenty"],
                ["Accuracy", "metres", "Radius, not diameter; absent means unknown"],
                ["Speed", "metres per second", "Display may convert to km/h"],
                ["Heading", "degrees", "0 = north, clockwise, [0, 360)"],
                ["Timestamps", "ISO 8601", "UTC with `Z` or an explicit offset; never local time without offset"],
                ["Distances on the map", "metres", "Leaflet `Circle` radius is metres"],
            ],
            [4.2, 4.2, 8.4],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "If the producer only has local metres, convert **before** writing the file. For a site smaller than a few "
            "kilometres, an equirectangular approximation around the site origin is sufficient:"
        )
        self.code(
            """// Local ENU metres -> WGS84, for a site origin (lat0, lon0)
const R = 6_378_137; // metres
const lat = lat0 + (y / R) * (180 / Math.PI);
const lon = lon0 + (x / (R * Math.cos(lat0 * Math.PI / 180))) * (180 / Math.PI);""",
            "Use this once, in the producer. Document the origin and the axis convention (x = east, y = north).",
        )

        self.h2("6.10 Versioning")
        self.bullets([
            "**Minor change** (`1.0` → `1.1`): add an optional field, add an enum value the UI can display raw, or relax a constraint. Old consumers keep working.",
            "**Major change** (`1.x` → `2.0`): rename or remove a required field, change a unit, or change the meaning of a field. The app refuses the file with a clear message.",
            "**Additive by default.** The UI must ignore unknown fields and display unknown `method` values as raw text.",
            "**Never reuse a field name with a new meaning.** Add `zoneName` rather than changing `zone` from a string to an object.",
            "**Record the contract in the repo.** The schema file and the example file are the source of truth; a PDF is not.",
        ])

        self.h2("6.11 Atomic writes")
        self.p(
            "A browser polling every second will eventually read the file while the producer is writing it. The result is "
            "a truncated JSON document and a fatal parse error. The producer must write to a temporary file in the same "
            "directory and rename it over the target. On POSIX filesystems, `rename` is atomic: a reader sees either the "
            "old file or the new file, never a half-written one."
        )
        self.code(
            """// Node.js producer: atomic replace
import { writeFile, rename } from 'node:fs/promises';

const target = '/srv/fleet/data/fleet.snapshot.json';
const temp = `${target}.tmp`;

await writeFile(temp, JSON.stringify(snapshot, null, 2), 'utf8');
await rename(temp, target); // atomic on the same filesystem""",
            "The same pattern works in Python with `os.replace(temp, target)`.",
        )
        self.callout(
            "Atomic rename is not a backup",
            "Keep the previous good snapshot as `fleet.snapshot.previous.json` if the producer crashes mid-write. The app "
            "does not need it, but the operator does when diagnosing a bad deploy.",
            "info",
        )

        self.h2("6.12 Why JSON, not CSV or JSON Lines")
        self.table(
            ["Format", "Strength", "Problem for this MVP"],
            [
                ["JSON object", "Nested site/stations/trucks; one atomic document; native to JS", "None for this size"],
                ["CSV", "Easy to edit in Excel; familiar to operators", "No nesting, no types, encoding issues, one table per file"],
                ["JSON Lines", "Good for append-only streams and large volumes", "A growing file is awkward to poll; the browser needs the latest complete state"],
                ["Protobuf", "Compact and schema-driven", "Extra tooling and a build step; overkill for 25 KB"],
            ],
            [3.4, 6.2, 7.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "If an operator insists on Excel, keep CSV as an import format in the producer and convert it to the JSON "
            "contract. Do not add a second contract to the browser."
        )

        self.h2("6.13 Size, frequency, and a warning about disk writes")
        self.p(
            "A snapshot with 100 trucks is roughly 20–30 KB of JSON. At one rewrite per second, that is about 2 GB of "
            "disk writes per day, even though the file is small at any instant. For a demo or a short pilot this is fine. "
            "For a 24/7 production system it is not: use a backend API with an in-memory/Redis snapshot, or place the file "
            "on a tmpfs/ramdisk. The file is a bridge, not the final telemetry store."
        )
        self.table(
            ["Fleet size", "Approx. snapshot", "Writes/day at 1 Hz", "Verdict"],
            [
                ["5 trucks", "3–5 KB", "0.3–0.4 GB", "Demo: fine"],
                ["100 trucks", "20–30 KB", "1.7–2.6 GB", "Pilot: acceptable for weeks, not ideal for years"],
                ["1,000 trucks", "200–300 KB", "17–26 GB", "Move to API/WebSocket before this"],
            ],
            [3.0, 3.8, 4.6, 5.4],
            font_size=8.4,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Chapter 7
    # ------------------------------------------------------------------
    def chapter_7(self) -> None:
        self.h1("7. Map and screen")
        self.p(
            "The screen is deliberately close to the familiar “buses on a map” pattern: a large map, coloured dots, a "
            "selected object, and a small legend. The difference is that the dots come from a private positioning system, "
            "so the screen must also communicate uncertainty and freshness."
        )

        self.h2("7.1 Why Leaflet")
        self.bullets([
            "**Small and mature.** Leaflet is a stable, BSD-licensed library with a large plugin ecosystem and a low learning curve.",
            "**No API key.** OpenStreetMap tiles work without a commercial key, which keeps the demo and the closed-contour discussion simple.",
            "**The needed primitives are built in.** Markers, circles (metres), polylines, popups, tooltips, image overlays, and fit-bounds.",
            "**React integration is straightforward.** `react-leaflet` maps declaratively to components; the map can be isolated in one folder.",
            "**Offline fallback is easy.** A site-plan image can be added as an `ImageOverlay` without changing the data layer.",
        ])
        self.p(
            "MapLibre GL JS is the natural upgrade if the project later needs vector tiles, smooth zoom, 3D, or a heavily "
            "styled site map. The architecture keeps that option open by isolating Leaflet in `FleetMap.tsx` and marker "
            "components; no repository or domain code imports Leaflet."
        )

        self.h2("7.2 Map configuration and tiles")
        self.table(
            ["Mode", "When to use", "Implementation"],
            [
                ["`osm`", "Development, demo with internet access", "`TileLayer` with the OSM URL and attribution"],
                ["`image`", "Closed network or a site with poor OSM detail", "`ImageOverlay` with `bounds` from `site.map.imageBounds`"],
                ["`blank`", "Tiles blocked, but dots still matter", "No tile layer; a neutral background and a grid"],
            ],
            [2.8, 6.2, 7.8],
            font_size=8.4,
            first_col_bold=True,
        )
        self.code(
            """<!-- OpenStreetMap tile layer (development / demo only) -->
<TileLayer
  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  maxZoom={19}
/>""",
            "Public OSM tiles are subject to the OSM tile usage policy. For a production or offline site, self-host tiles or use a site plan.",
        )
        self.p(
            "To use a site plan, georeference it by supplying two WGS84 corners (`imageBounds`); a plan that is rotated "
            "or not north-up will misplace every dot, so fix the source image first."
        )

        self.h2("7.3 Marker design")
        self.table(
            ["Object", "Visual", "Behaviour"],
            [
                ["Truck, moving", "Green dot, 14 px, white 2 px border", "Hover tooltip; click selects; optional heading triangle"],
                ["Truck, idle", "Amber dot", "Same as moving"],
                ["Truck, offline", "Grey dot, 60% opacity", "Still shown at the last known position; details show the age"],
                ["Truck, unknown", "Blue dot", "Used when status is missing or unrecognised"],
                ["Selected truck", "20 px dot + 3 px ring + accuracy circle", "Details panel opens; map does not auto-pan on every update"],
                ["Base station", "Blue diamond/square, 12 px, label", "Always visible; tooltip shows status and coordinates"],
                ["Accuracy circle", "Dashed circle, radius `accuracyM`", "Only for the selected truck, to avoid visual noise"],
            ],
            [3.4, 6.4, 7.0],
            font_size=8.4,
            first_col_bold=True,
        )
        self.callout(
            "Do not encode status by colour alone",
            "About 8% of men have some form of colour-vision deficiency. Add a shape, an icon, or a short label in the "
            "tooltip and details. The legend should use words and shapes, not only green/amber/grey dots.",
            "warning",
        )

        self.h2("7.4 Accuracy and method")
        self.p(
            "A dot without an accuracy indicator looks more precise than it is. The contract therefore carries "
            "`accuracyM` and `method`, and the details panel always shows both. If `accuracyM` is absent, show “accuracy "
            "unknown”; do not render a zero-radius circle."
        )
        self.table(
            ["Method value", "Label in UI", "What it means"],
            [
                ["`rssi-multilateration`", "RSSI multilateration", "Three or more stations; the main method"],
                ["`timing-advance`", "Timing advance", "Two-station fallback; coarse distance from timing"],
                ["`cell-id`", "Cell ID", "Serving-cell only; large uncertainty"],
                ["anything else", "Raw value", "Forward compatibility; do not crash on a new method"],
            ],
            [4.4, 5.0, 7.4],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("7.5 Screen layout")
        self.code(
            """┌──────────────────────────────────────────────────────────┬─────────────────────┐
│ Header: site name · data status · last update · refresh   │                     │
├──────────────────────────────────────────────────────────┤  Truck list         │
│                                                          │  (search / filter)  │
│                                                          │                     │
│                         MAP                              │  ─────────────────  │
│              stations + truck dots + accuracy            │  Selected truck     │
│                                                          │  details            │
│                                                          │  (name, coords,     │
│                                                          │   accuracy, method, │
│                                                          │   last update)      │
├──────────────────────────────────────────────────────────┴─────────────────────┤
│ Legend: ● moving  ● idle  ● offline  ◆ station  ○ accuracy radius             │
└────────────────────────────────────────────────────────────────────────────────┘""",
            "Desktop-first layout. On narrow screens the right panel becomes a bottom sheet; the map remains the primary surface.",
        )
        self.p(
            "The header is the trust surface: site name on the left, data status and last update on the right. The "
            "details panel is the identification surface. The legend is small and always visible; it should not require a "
            "click to understand the dots."
        )

        self.h2("7.6 Screen states")
        self.table(
            ["State", "Trigger", "What the user sees"],
            [
                ["Initial loading", "No data yet, first request in flight", "Map skeleton + “Loading positions…”; no fake dots"],
                ["Live", "Fresh snapshot, fresh trucks", "Full map; green “Live” pill; last update time"],
                ["Stale snapshot", "`generatedAt` older than 10 s", "Amber banner: “Data is N s old”; dots dimmed but visible"],
                ["Refresh error", "A later poll fails; previous data exists", "Red/amber banner: “Cannot refresh; showing last known positions”; Retry"],
                ["Fatal first load", "No data and the first request fails", "Error card with URL, reason, and Retry; map may show stations if available"],
                ["Empty", "Valid file with zero trucks", "Map + “No trucks in the snapshot” + file path hint"],
                ["Partial invalid", "Some records skipped", "Map + small “N records skipped” link to data health"],
                ["Tile failure", "Tiles blocked or offline", "Blank/grid background; dots and stations still visible"],
                ["Clock skew", "Timestamp in the future", "Warning in data health; no crash"],
            ],
            [3.4, 6.2, 7.2],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("7.7 Interaction details")
        self.bullets([
            "**Hover** a truck: tooltip with name and status. Keep it small; do not open a full popup on hover.",
            "**Click** a truck: select it, open the details panel, draw the accuracy circle. Clicking the map background clears the selection.",
            "**Truck list**: a searchable/filterable list is the keyboard-accessible alternative to the map. Selecting a row selects the map object.",
            "**Fit all**: a button that fits stations and trucks into the viewport. Useful after panning away.",
            "**Locate selected**: pan/zoom to the selected truck once, not on every poll. A “follow” mode is post-MVP.",
            "**No auto-pan on updates**: the map must not jump while the dispatcher is inspecting another area.",
            "**Close details**: an explicit close button; Escape also clears the selection.",
        ])

        self.h2("7.8 Performance")
        self.bullets([
            "Use `preferCanvas` for circle markers when the fleet grows; SVG is fine for a few dozen dots.",
            "Memoise `TruckMarker` by `id`, `lat`, `lon`, `status`, and `selected`; do not recreate icon objects on every render.",
            "Use stable `key={truck.id}`. Never use the array index as a key.",
            "Draw the accuracy circle only for the selected truck; 100 circles at once are visual noise and extra work.",
            "Keep the `MapContainer` mounted. Recreating the map on each poll destroys tiles and causes flicker.",
            "Batch updates if the polling rate increases; at 1 Hz, React and Leaflet handle 100 dots comfortably.",
            "Avoid popups for every marker; one details panel is cheaper and more usable on a wall display.",
        ])

        self.h2("7.9 Accessibility")
        self.bullets([
            "The truck list is a real `<ul>`/`<button>` interface, not a div with onClick. It is the accessible path to every object.",
            "Use `aria-live=\"polite\"` for the data-status banner and the selected truck summary; do not announce every position update.",
            "Maintain visible focus styles; Leaflet’s default focus outline is not enough on a dark map.",
            "Do not rely on colour alone: pair status colours with labels or shapes.",
            "Respect `prefers-reduced-motion`; disable smooth marker animation when it is set.",
            "Provide a text alternative for the map: the list plus details covers the same information.",
        ])

        self.h2("7.10 Yandex Maps: UX reference, not a dependency")
        self.p(
            "“Like buses on Yandex Maps” describes the **experience**, not necessarily the map provider. Yandex Maps JS "
            "API requires an API key, external servers, and a commercial licence; it may not be acceptable in a closed "
            "enterprise network. Leaflet + OSM delivers the same core pattern — dots, selection, details — without a key."
        )
        self.p(
            "If the customer mandates Yandex Maps, add a `YandexMapCanvas` behind the same props as `FleetMap`. The data "
            "layer, schema, and page state do not change. Do not make that decision implicitly by putting Yandex "
            "coordinates or SDK objects into the domain model."
        )
        self.callout(
            "Clarify the map provider before day 1",
            "A late “we need Yandex Maps” request is cheap if the map is isolated and expensive if Leaflet types have leaked "
            "into pages and hooks. The isolation is part of the MVP, even if the provider does not change.",
            "warning",
        )

    # ------------------------------------------------------------------
    # Chapter 8
    # ------------------------------------------------------------------
    def chapter_8(self) -> None:
        self.h1("8. Reliability, security, and operations")
        self.p(
            "MVP 0.1 has no backend to monitor, but it still has failure modes: the producer stops, the file is "
            "truncated, the network is down, the map tiles are blocked, or the timestamps are wrong. The design goal is "
            "not “no failures”; it is “the screen never lies about what it knows”."
        )

        self.h2("8.1 Failure modes")
        self.table(
            ["Failure", "Detection", "User-visible behaviour", "Operator action"],
            [
                ["Producer stops writing", "`generatedAt` age > threshold", "Stale banner; dots dimmed", "Check producer logs and disk"],
                ["File is truncated", "JSON parse error", "Keep last good data; error banner", "Check atomic write; restore previous file"],
                ["Schema changed", "Envelope Zod error", "Contract error with first issue", "Deploy compatible app or fix producer"],
                ["One bad record", "Record Zod error", "Skip record; count in data health", "Fix the producer record"],
                ["Network down", "Fetch rejection", "Keep last good data; banner", "Check network / reverse proxy"],
                ["Tiles blocked", "Tile layer errors", "Blank map; dots still visible", "Use site plan or local tiles"],
                ["Clock skew", "Timestamp > 5 min future", "Warning; data kept", "Enable NTP on the producer host"],
                ["Huge file", "Size > 5 MB", "Slow parse; warning", "Reduce frequency or move to API"],
            ],
            [3.4, 4.2, 5.0, 4.2],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("8.2 Staleness rules")
        self.p(
            "There are two different ages, and confusing them is a common bug. `generatedAt` says when the **producer** "
            "made the snapshot. `updatedAt` says when the **truck** was measured. A file can be freshly generated and "
            "still contain a truck that has not been seen for five minutes."
        )
        self.table(
            ["Rule", "Default", "Meaning"],
            [
                ["Snapshot stale", "`now - generatedAt > 10 s`", "The producer is not refreshing; the whole picture may be old"],
                ["Truck stale", "`now - updatedAt > 30 s`", "This object has not reported recently; show an offline/stale badge"],
                ["Clock skew warning", "`updatedAt > now + 5 min`", "A clock is wrong; do not trust relative times"],
                ["Poll interval", "1 s", "Display latency is roughly one cycle plus network"],
            ],
            [4.4, 5.2, 7.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.callout(
            "A successful fetch is not freshness",
            "If the producer crashes, Nginx will happily serve the last file with HTTP 200 forever. The stale check must "
            "look at `generatedAt`, not at the fetch status. This is the single most important reliability rule in the MVP.",
            "danger",
        )

        self.h2("8.3 Security and privacy")
        self.bullets([
            "**The snapshot is public to anyone who can reach the app.** If truck positions are sensitive, protect the whole app with VPN, SSO, or reverse-proxy auth.",
            "**No secrets in the bundle.** `VITE_*` variables are compiled into JavaScript and are not secret. Magma tokens, DB passwords, and API keys belong on the server.",
            "**No personal data.** Use asset IDs, not driver names or phone numbers. Do not put IMSIs in the UI contract unless there is a clear need.",
            "**No direct Magma access.** The browser must not hold Orchestrator credentials or call AGW APIs; CORS is not a security boundary.",
            "**Use HTTPS** in any environment beyond localhost. A static app can still leak positions over plain HTTP.",
            "**Tile privacy.** Public OSM tiles reveal the approximate map area to a third party. A closed site should use self-hosted tiles or a site plan.",
            "**Content Security Policy** is a later hardening step; start with `default-src 'self'` and add the tile host explicitly when the map provider is fixed.",
        ])

        self.h2("8.4 Deployment")
        self.p(
            "The build is a static `dist/` directory. The snapshot is a separate file mounted or copied into `/data/`. "
            "The app and the data must be served from the same origin so that no CORS configuration is needed."
        )
        self.code(
            """# Build and publish (example)
pnpm install --frozen-lockfile
pnpm build
rsync -a --delete dist/ /srv/fleet/www/
install -m 0644 data/fleet.snapshot.json /srv/fleet/www/data/fleet.snapshot.json""",
            "The exact commands depend on the host; the important part is that `/data/` is writable by the producer and readable by Nginx.",
        )
        self.p(
            "A minimal Nginx configuration is in Appendix B. The key details are: an SPA fallback to `index.html`, "
            "`Cache-Control: no-store` for `/data/`, long caching for hashed assets, and gzip for JSON and JavaScript."
        )

        self.h2("8.5 File update mechanics")
        self.bullets([
            "Write the snapshot to a temporary file in the same directory, then `rename` over the target.",
            "Never write directly to the served file; a 1 Hz reader will catch a partial write sooner or later.",
            "Keep the file permissions readable by the web server and writable only by the producer.",
            "Use UTC timestamps and keep the producer host on NTP. A one-minute clock drift makes “stale” meaningless.",
            "Do not run a `git pull` or an editor save directly on the served file; both can truncate it.",
            "If the producer writes from another host, use an atomic upload to a temp name and a server-side rename, not a direct overwrite over SMB.",
        ])

        self.h2("8.6 Monitoring and diagnostics")
        self.p(
            "Without a backend, the browser is the main observability surface. Add a small “Data health” popover that "
            "shows the source URL, last successful fetch, `generatedAt`, schema version, station/truck counts, and skipped "
            "records. It is invaluable for a first-time implementer and for the integrator."
        )
        self.table(
            ["Signal", "Where to see it", "What it tells you"],
            [
                ["Last successful fetch", "Header / data health", "Whether the network and server are working"],
                ["`generatedAt` age", "Header / stale banner", "Whether the producer is alive"],
                ["Skipped records", "Data health badge", "Whether the producer's data quality is degrading"],
                ["Schema version", "Data health", "Whether the app and producer are compatible"],
                ["Tile errors", "Browser console / blank map", "Whether the map provider is reachable"],
                ["Bundle version", "Footer / build info", "Which release is deployed"],
            ],
            [4.4, 6.0, 6.4],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "For an external check, a small cron job can fetch the snapshot and alert when `generatedAt` is older than "
            "60 seconds. This is a five-line script and catches the most common failure: a producer that stopped silently."
        )

        self.h2("8.7 Backup and rollback")
        self.bullets([
            "Keep the last known good snapshot and the last two static builds. Rollback is a symlink or directory swap.",
            "Version the app with a build stamp in the footer; “which version is on the wall display?” should be answerable without SSH.",
            "If a deploy breaks the map, the file is unaffected; if a producer change breaks the contract, the app's error state protects the last good picture.",
            "Document the restore procedure in the runbook; do not rely on memory during an incident.",
        ])

        self.h2("8.8 Browser support")
        self.p(
            "Target the latest two versions of Chrome, Edge, Firefox, and Safari. The app uses standard `fetch`, "
            "`AbortController`, CSS grid/flex, and Leaflet; no polyfills are required for these browsers. Internet "
            "Explorer is out of scope. For a wall display, pin the browser version and disable auto-update surprises "
            "during a demo."
        )

    # ------------------------------------------------------------------
    # Chapter 9
    # ------------------------------------------------------------------
    def chapter_9(self) -> None:
        self.h1("9. Testing and quality")
        self.p(
            "The MVP is small enough to test well. The goal is not 100% coverage; it is confidence in the boundary "
            "(schema), the failure behaviour (stale/error), and the one interaction that matters (select a truck)."
        )

        self.h2("9.1 Test strategy")
        self.table(
            ["Layer", "What to test", "Tools", "Share"],
            [
                ["Unit", "Zod envelope/records, duplicate IDs, staleness, coordinate helpers, selectors", "Vitest", "~55%"],
                ["Component", "Truck markers, details card, banners, empty/error states", "Vitest + Testing Library", "~30%"],
                ["Integration", "Repository + hook + page with a mocked fetch/file", "Vitest + MSW or a mock repository", "~10%"],
                ["End-to-end", "Load, see dots, select, stale banner, broken file", "Playwright (optional for MVP)", "~5%"],
                ["Manual", "Real file, real tiles, offline tiles, 100 trucks, wall display", "Checklist", "Every release"],
            ],
            [3.0, 7.2, 4.4, 2.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "`react-leaflet` is awkward in jsdom because Leaflet needs real layout and `ResizeObserver`. Do not fight it: "
            "unit-test the data and the page states, and mock the map component in component tests. Keep one real-browser "
            "E2E test for the map itself."
        )

        self.h2("9.2 Test cases")
        self.table(
            ["ID", "Case", "Expected"],
            [
                ["T-01", "Valid snapshot with 3 stations and 4 trucks", "Parsed; no diagnostics; counts correct"],
                ["T-02", "Missing `site`", "Fatal `schema` error with a readable message"],
                ["T-03", "`schemaVersion: 2.0`", "Fatal unsupported-version error"],
                ["T-04", "One truck with latitude 123", "Other trucks parsed; one `invalid-truck` diagnostic"],
                ["T-05", "Two trucks with the same ID", "First kept; one `duplicate-id` diagnostic"],
                ["T-06", "`generatedAt` 30 s old", "Snapshot status `stale`; banner visible"],
                ["T-07", "`updatedAt` 2 min old", "Truck badge `stale`/`offline`; snapshot still live"],
                ["T-08", "Fetch rejects", "Fatal on first load; non-blocking banner with previous data"],
                ["T-09", "Invalid JSON", "Typed `invalid-json` error; no unhandled rejection"],
                ["T-10", "Click truck dot", "Details card shows name, coords, accuracy, method, time"],
                ["T-11", "Keyboard select in list", "Same selection as map; details update"],
                ["T-12", "Empty trucks array", "Empty state, not an error"],
                ["T-13", "Unknown `method` value", "Displayed raw; no crash"],
                ["T-14", "100 trucks at 1 Hz", "No long task over 200 ms; no memory growth after 10 min"],
            ],
            [1.4, 9.2, 6.2],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("9.3 Definition of Done")
        self.bullets([
            "All acceptance criteria in section 2.4 pass on the demo build.",
            "`pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm build` are green.",
            "The example snapshot and the live snapshot both load; a corrupted file produces a useful error.",
            "The stale and refresh-error states are demonstrated, not just coded.",
            "The app works at a non-root base path and with `Cache-Control: no-store`.",
            "The README explains how to run, build, deploy, and replace the data file.",
            "The data contract is documented and linked from the code.",
            "No secrets, no `any` in domain code, no console errors on the happy path.",
            "The demo script has been rehearsed once end-to-end.",
            "The release is tagged `v0.1.0` and the build stamp is visible.",
        ])

        self.h2("9.4 Code quality")
        self.bullets([
            "TypeScript `strict: true`; no `any` at the data boundary; `unknown` plus Zod instead.",
            "ESLint + Prettier; a pre-commit hook is optional, CI is mandatory.",
            "One error boundary at the app root; it shows a readable fallback, not a white screen.",
            "No `console.log` in production; use a small debug flag for development.",
            "Pure functions in `domain` and `shared/lib`; side effects at the edges.",
            "Comments explain *why*, not *what*. The code should make the what obvious.",
        ])

        self.h2("9.5 Performance budget")
        self.table(
            ["Metric", "Budget", "How to check"],
            [
                ["Initial JS", "≤ 300 KB gzip", "`vite build` + `rollup-plugin-visualizer`"],
                ["First useful map", "≤ 2.5 s on LAN", "Performance panel, 4× CPU throttle"],
                ["Poll cycle, 100 trucks", "≤ 50 ms main-thread work", "Performance panel"],
                ["Marker update", "No full map remount", "React Profiler / visual stability"],
                ["Memory", "Stable after 10 min at 1 Hz", "Performance monitor"],
            ],
            [4.6, 5.0, 7.2],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("9.6 Manual QA checklist")
        self.table(
            ["Check", "Pass condition"],
            [
                ["Open the page on a clean profile", "Map, stations, and trucks appear; no console errors"],
                ["Replace the file with new coordinates", "Dots move within ~2 s; no reload"],
                ["Rename the file", "Banner appears; last dots stay; Retry recovers after restore"],
                ["Corrupt one record", "Other dots remain; data health shows one skipped"],
                ["Set `generatedAt` two minutes back", "Stale banner appears even though HTTP is 200"],
                ["Disable network / block tiles", "Dots and details still work on a blank map"],
                ["Resize to 1024 px and to mobile width", "Details panel remains usable; no horizontal scroll"],
                ["Keyboard only", "Tab to list, select a truck, read details, close with Escape"],
                ["100-truck snapshot", "Pan/zoom remains smooth; no visible freeze"],
                ["Base path deployment", "Assets and snapshot load under `/fleet/`"],
            ],
            [6.4, 10.4],
            font_size=8.4,
        )
        self.callout(
            "Test the failure that will actually happen",
            "The most likely production failure is not a broken React component. It is a producer that stopped, a file "
            "that was overwritten non-atomically, or a stale snapshot served with HTTP 200. Test those three first.",
            "info",
        )

    # ------------------------------------------------------------------
    # Chapter 10
    # ------------------------------------------------------------------
    def chapter_10(self) -> None:
        self.h1("10. Delivery plan")
        self.p(
            "The plan is built around one principle: every day ends with something that can be shown. The first demo is "
            "not “the architecture is ready”; it is “five dots move on a map”. The plan below assumes one frontend "
            "developer and a part-time domain expert, with a two-week calendar and a 15% buffer."
        )

        self.h2("10.1 Team and assumptions")
        self.table(
            ["Role", "Commitment", "Responsibility"],
            [
                ["Frontend developer", "Full-time, 8–10 days", "React, map, data layer, tests, deployment"],
                ["Positioning / integration expert", "2–3 hours per week", "Contract review, coordinate system, sample data"],
                ["Designer / product owner", "2–3 hours per week", "Screen layout, status language, demo acceptance"],
                ["Reviewer / QA", "0.5 day at gates", "Acceptance criteria, failure drills, release sign-off"],
                ["First-time implementer", "+20–30% time", "Pairing and code review; the architecture is deliberately learnable"],
            ],
            [4.3, 4.0, 8.5],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "The estimate is **55–65 ideal hours** of implementation, which fits 8–10 working days at 6–7 productive "
            "hours per day. The calendar below uses 10 days and keeps the buffer for integration surprises, not for new "
            "scope."
        )

        self.h2("10.2 Two-week calendar")
        self.table(
            ["Day", "Focus", "Output", "Gate"],
            [
                ["1", "Contract review; scaffold; map shell", "Schema v1 agreed; Vite app; Leaflet map with site centre", "G0: contract frozen"],
                ["2", "Domain types, Zod, sample file, repository", "Validated snapshot in tests; raw debug view", "—"],
                ["3", "Polling, station markers, truck dots", "Moving dots from the file; last update time", "G1: first dots"],
                ["4", "Selection, details, status colours", "Click a dot or list row; card and accuracy circle", "—"],
                ["5", "Error, empty, stale states; review", "Demo 1; issue list; scope check", "G2: usable screen"],
                ["6", "Responsive layout, accessibility, diagnostics", "Mobile/desktop; keyboard list; data health", "—"],
                ["7", "Unit, component, integration tests", "Test suite green; failure cases covered", "—"],
                ["8", "Build, Nginx, README, runbook", "Release candidate deployed at a real URL", "G3: RC"],
                ["9", "Bugfix, performance, demo data, rehearsal", "Polished demo; 100-truck check", "—"],
                ["10", "Customer demo, handover, tag", "Accepted MVP; `v0.1.0`; backlog for Phase 1", "G4: done"],
            ],
            [1.3, 5.2, 7.3, 3.0],
            font_size=8.3,
            first_col_bold=True,
            align_center_cols=[0],
        )

        self.h2("10.3 Backlog and estimates")
        self.table(
            ["ID", "Task", "h", "Depends on", "Done when"],
            [
                ["M0-1", "Contract review with producer and customer", "4", "—", "Schema v1 and sample signed off"],
                ["M0-2", "Coordinate and map-provider decisions", "3", "—", "WGS84 confirmed; tiles/site plan chosen"],
                ["M1-1", "Scaffold Vite + React + TS + lint/test", "3", "—", "`pnpm dev`, lint, test, build work"],
                ["M1-2", "App shell, providers, error boundary", "3", "M1-1", "Blank page with header/footer and no errors"],
                ["M2-1", "Domain types + Zod schemas + tests", "4", "M0-1", "Valid/invalid fixtures behave as specified"],
                ["M2-2", "JsonFileFleetRepository + typed errors", "4", "M2-1", "Fetch, parse, partial failure, 404 covered"],
                ["M2-3", "useFleetSnapshot + QueryClient", "2", "M2-2", "Debug view updates every second"],
                ["M3-1", "Map shell + station markers", "5", "M1-2", "Map centred; stations and labels visible"],
                ["M3-2", "Truck markers + status + accuracy", "5", "M3-1", "Dots move; selected dot has a ring"],
                ["M3-3", "Truck list + details panel + selection", "4", "M3-2", "Map and list select the same object"],
                ["M4-1", "Loading / empty / stale / error / partial states", "4", "M3-3", "Every state can be triggered manually"],
                ["M4-2", "Responsive layout + accessibility pass", "3", "M4-1", "1024 px and mobile; keyboard path works"],
                ["M4-3", "Data health panel + diagnostics", "3", "M4-1", "Source, age, counts, skipped records visible"],
                ["M5-1", "Unit/component/integration tests", "5", "M2-2, M3-3", "Test plan from 9.2 is covered"],
                ["M5-2", "Production build, Nginx, README, runbook", "4", "M4-2", "Deployed URL; docs reviewed"],
                ["M5-3", "Demo data, rehearsal, handover", "2", "M5-2", "Demo runs twice without intervention"],
            ],
            [1.4, 6.2, 1.2, 3.0, 5.0],
            font_size=8.2,
            first_col_bold=True,
            align_center_cols=[2],
        )
        self.p(
            "The sum is about 58 ideal hours. The buffer is for the unknowns that always appear: a coordinate convention, "
            "a tile policy, a deployment path, or a browser quirk. It is not for extra features."
        )

        self.h2("10.4 Milestones")
        self.table(
            ["Milestone", "Evidence", "Decision"],
            [
                ["M0 — Contract frozen", "Schema and example file reviewed by producer and UI", "Proceed to build; changes after this are versioned"],
                ["M1 — First dots", "Five trucks from the file move on the map", "Proceed to interaction and failure states"],
                ["M2 — Usable screen", "Selection, details, accuracy, legend, status", "Show to the dispatcher; collect feedback"],
                ["M3 — Release candidate", "Deployed build, tests green, README", "Freeze scope; only bug fixes"],
                ["M4 — MVP accepted", "Acceptance checklist signed; demo recorded", "Start Phase 1 backlog"],
            ],
            [4.4, 7.6, 4.8],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("10.5 Demo script (five minutes)")
        self.numbered([
            "**Open the page.** Name the site, point to the three stations, and note the live status and last update time.",
            "**Show the dots.** Explain the colours (moving, idle, offline) and the accuracy circle on the selected truck.",
            "**Select a truck.** Use the map and then the keyboard-accessible list; show the details card.",
            "**Move the fleet.** Run the demo generator or replace the file; the dots update without a reload.",
            "**Break it deliberately.** Rename the file and show the banner and last known positions; restore it and show recovery.",
            "**Show the seam.** Open the data-health panel, then show the `FleetRepository` interface and the one-line composition root. Close with the Phase 1/2 roadmap.",
        ])
        self.callout(
            "Rehearse the failure, not only the happy path",
            "A demo that only shows moving dots looks like a toy. A demo that survives a deleted file and explains stale data "
            "looks like an engineering product. Rehearse the failure drill at least twice.",
            "info",
        )

        self.h2("10.6 What could change the estimate")
        self.table(
            ["Change", "Extra effort", "Reason"],
            [
                ["Coordinates are not WGS84", "+2–3 days", "Conversion, validation, and site-origin documentation"],
                ["Yandex Maps is mandatory", "+2–3 days", "API key, licensing, a second map adapter, and testing"],
                ["Fully offline site", "+1–2 days", "Site-plan georeferencing or local tile server"],
                ["Authentication is required", "+2 days", "Reverse proxy or SSO integration, session handling"],
                ["Custom visual design", "+2 days", "Design system, responsive polish, review cycles"],
                ["First-time implementer without mentoring", "+20–30%", "Learning React, Leaflet, and the data boundary"],
            ],
            [5.0, 3.2, 8.6],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("10.7 Post-MVP backlog")
        self.table(
            ["Priority", "Item", "Why next"],
            [
                ["P0", "HTTP snapshot API adapter", "Moves the file behind a server and enables auth/CORS"],
                ["P0", "Production tile strategy (self-host or site plan)", "Removes the external OSM dependency"],
                ["P1", "WebSocket stream", "Lower latency and less polling at scale"],
                ["P1", "History and track playback", "Needs PostGIS/Timescale and a retention policy"],
                ["P1", "Authentication and roles", "Dispatcher vs admin; perimeter auth is not enough for production"],
                ["P2", "Station CRUD and calibration UI", "Operations become self-service"],
                ["P2", "Geofences and alerts", "Turns monitoring into action"],
                ["P2", "Clustering / canvas layer", "Supports 500–1,000+ trucks"],
                ["P3", "Smooth marker interpolation and trails", "Polish, not correctness"],
                ["P3", "Localisation (RU/EN) and dark theme", "Customer-facing polish"],
            ],
            [1.8, 7.2, 7.8],
            font_size=8.4,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Chapter 11
    # ------------------------------------------------------------------
    def chapter_11(self) -> None:
        self.h1("11. Risks and mitigations")
        self.p(
            "The risk register is short because the scope is small. The highest risks are not React bugs; they are "
            "coordinate mismatches, stale data presented as live, and scope creep into the positioning project."
        )
        self.table(
            ["Risk", "P", "I", "Score", "Mitigation", "Trigger"],
            [
                ["Coordinate system mismatch (local metres vs WGS84)", "H", "H", "9", "Freeze CRS in the contract; convert in the producer; validate ranges; one visual check against a known point", "Dots offset by a constant distance"],
                ["Stale file served as live", "H", "H", "9", "Check `generatedAt`, not HTTP status; stale banner; external age check", "HTTP 200 but positions frozen"],
                ["Scope creep into RSSI/Magma/DB", "H", "H", "9", "Out-of-scope list; change rule; Phase 1/2 backlog", "New “must-have” in standup"],
                ["Map tiles blocked in a closed network", "H", "M", "6", "Site-plan overlay or local tiles; blank map still works", "Grey tiles in the demo"],
                ["Yandex Maps required late", "M", "H", "6", "Isolate Leaflet behind `FleetMap`; clarify provider on day 1", "Customer mentions API key after build"],
                ["Non-atomic file write", "M", "H", "6", "Temp file + rename; previous snapshot; parse error banner", "Intermittent JSON parse errors"],
                ["Schema drift between producer and UI", "M", "M", "4", "Version field; Zod; contract review; example file in repo", "Unknown fields or missing required fields"],
                ["Performance at 1,000+ trucks", "M", "M", "4", "Canvas markers, API/WS, clustering; budget at 100 trucks", "Frame drops or long tasks"],
                ["Positions exposed on an open URL", "M", "H", "6", "Perimeter auth; no secrets; HTTPS; privacy review", "App reachable from a guest network"],
                ["Magma integration surprises", "H", "M", "6", "Server-side adapter; Open5GS fallback; spike in Phase 2", "Events missing or API unstable"],
                ["Clock skew / timezone errors", "M", "M", "4", "UTC ISO strings; NTP; future-timestamp warning", "“-3 s ago” or “in 2 hours”"],
                ["First-timer overengineering", "M", "M", "4", "One port, no Redux, no generic data source; code review checklist", "More abstraction than features"],
            ],
            [5.0, 1.0, 1.0, 1.2, 6.2, 2.4],
            font_size=7.8,
            first_col_bold=True,
            align_center_cols=[1, 2, 3],
        )
        self.p("P = probability, I = impact, Score = simple 1–9 product. The table is reviewed at every gate.", size=8.4, color=SUBTLE, italic=True)

        self.h2("11.1 The three risks that deserve a paragraph")
        self.p(
            "**Coordinate mismatch.** A constant offset is the most common silent failure. The map looks plausible, the "
            "dots move, and nobody notices that the whole fleet is 200 metres north of reality until a dispatcher walks "
            "to the wrong bay. Mitigation is procedural as much as technical: put one surveyed reference point in the "
            "file, compare the dot to the site plan, and sign off the CRS before the first demo."
        )
        self.p(
            "**Stale data presented as live.** A static server returns HTTP 200 for a file that has not changed in three "
            "hours. If the UI equates “fetch succeeded” with “data is live”, it will confidently show a frozen fleet. The "
            "fix is a single rule: freshness comes from `generatedAt`, not from the HTTP status. Test it by stopping the "
            "producer, not by unplugging the network."
        )
        self.p(
            "**Scope creep.** The project is surrounded by interesting problems: RSSI calibration, Magma events, MQTT "
            "QoS, Kalman tuning, history, geofences. Every one of them can consume the two-week window. The out-of-scope "
            "table and the “cannot be demonstrated in the demo” rule are the defence. The architecture is flexible "
            "precisely so those features can wait."
        )

        self.h2("11.2 Risk review cadence")
        self.bullets([
            "**Daily, 10 minutes:** what changed, what is blocked, which risk trigger fired.",
            "**At each gate:** re-score the top five risks; update the mitigation owner.",
            "**Before the demo:** run the failure drill (missing file, stale file, bad record, offline tiles).",
            "**After the demo:** convert the top unresolved risk into the first Phase 1 backlog item.",
        ])

    # ------------------------------------------------------------------
    # Chapter 12
    # ------------------------------------------------------------------
    def chapter_12(self) -> None:
        self.h1("12. Growing into Magma without a rewrite")
        self.p(
            "The MVP is file-backed, but it is not a dead end. The same contract and the same screen can be fed by an HTTP "
            "API and then by a Magma-backed positioning pipeline. This chapter explains what changes, what stays, and "
            "which decisions today keep the door open."
        )
        self.figure(
            "fig4-roadmap.png",
            "Figure 4. Four phases: file MVP, snapshot API, Magma + MQTT, production. Only the source adapter and the server side grow.",
            "Roadmap diagram with four phases: file MVP now, snapshot API next, Magma and MQTT later, production; the UI and contract stay stable while the source adapter and backend change.",
        )

        self.h2("12.1 What Magma is — and what it is not")
        self.p(
            "Magma is an open-source mobile core: an Access Gateway (AGW) that serves subscribers on site and an "
            "Orchestrator with APIs and an NMS for managing subscribers, networks, and policies. For this project it is "
            "valuable because it manages SIMs and sessions, knows which cell a truck is attached to, and emits events for "
            "attach, detach, and handover."
        )
        self.p(
            "Magma is **not** a positioning engine. It does not compute multilateration, and it does not provide "
            "neighbour-cell RSRP/RSRQ measurements by itself. Those measurements come from the truck's modem, collected "
            "by an on-board agent. Magma supplies the network context and the authoritative “this truck is online and "
            "attached to this cell” signal."
        )

        self.h2("12.2 Target architecture")
        self.figure(
            "fig5-magma-target.png",
            "Figure 5. Target architecture: trucks and Magma feed a private backend, which publishes the same FleetSnapshot to the browser.",
            "Target architecture diagram: truck agent publishes MQTT measurements; Magma emits session events; a backend ingest service, positioning engine, snapshot publisher, database, and REST/WebSocket API feed the React SPA; Open5GS is a drop-in alternative behind the adapters.",
        )
        self.p(
            "The important boundary is the vertical line between the backend and the browser. The browser receives a "
            "`FleetSnapshot` over HTTPS/WSS. It never receives Magma credentials, MQTT credentials, or raw radio "
            "measurements. This is both a security boundary and a testability boundary."
        )

        self.h2("12.3 Phase 1: the snapshot API")
        self.p(
            "Phase 1 removes the static file from the browser's path without changing the contract. A small backend "
            "reads the file (or a database) and exposes `GET /api/v1/fleet/snapshot`. The response body is the same JSON "
            "object. The frontend adds one adapter and changes one line in the composition root."
        )
        self.code(
            """// src/data/http-fleet-repository.ts
export class HttpFleetRepository implements FleetRepository {
  constructor(private readonly baseUrl: string) {}

  async loadSnapshot({ signal }: { signal?: AbortSignal } = {}): Promise<FleetLoadResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/fleet/snapshot`, {
      signal,
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new FleetSourceError('http', `HTTP ${response.status}`);
    const json: unknown = await response.json();
    return parseFleetSnapshot(json); // same parser, same contract
  }
}

// src/app/App.tsx — the only line that changes
const repository = new HttpFleetRepository('/api');""",
            "The UI does not know whether the snapshot came from a file or an API. That is the entire point of the port.",
        )
        self.p(
            "Phase 1 also introduces the things a server makes possible: authentication, CORS, rate limits, and a "
            "single place to add caching. None of them require a change to the map."
        )

        self.h2("12.4 Phase 2: Magma, MQTT, and the positioning engine")
        self.p(
            "Phase 2 is the real system. It has four server-side responsibilities: ingest, position, publish, and "
            "retain. The frontend remains a consumer of snapshots."
        )
        self.numbered([
            "**Ingest.** The on-board agent reads the modem (RSRP/RSRQ, serving cell, neighbours, timing advance) and publishes it to MQTT. Magma events (attach, detach, handover) arrive through the AGW event stream or Orchestrator API. The ingest service normalizes both into a measurement/event model.",
            "**Position.** The positioning engine applies calibration, filtering, weighted least squares, and a Kalman filter. It outputs a coordinate, accuracy, method, and timestamp per truck.",
            "**Publish.** The snapshot publisher assembles a complete `FleetSnapshot` and exposes it over REST and WebSocket. It writes history to PostGIS/TimescaleDB and keeps the current state in Redis for fast reads.",
            "**Consume.** The React app uses a `WebSocketFleetRepository` (or the HTTP adapter as a fallback) and renders the same screen.",
        ])

        self.h2("12.5 What changes and what stays")
        self.table(
            ["Area", "MVP 0.1", "Phase 1", "Phase 2"],
            [
                ["Data source", "Static JSON file", "HTTP API", "API + WebSocket"],
                ["Backend", "None", "Small snapshot service", "Ingest + engine + publisher"],
                ["Database", "None", "Optional", "PostGIS + Timescale + Redis"],
                ["Radio / Magma", "None", "None", "MQTT agents + Magma events"],
                ["Frontend repository", "`JsonFileFleetRepository`", "`HttpFleetRepository`", "`WebSocketFleetRepository`"],
                ["Domain contract", "`FleetSnapshot` v1", "Same, additive fields", "Same, additive fields"],
                ["Map / screen", "Leaflet + page", "No change", "No change"],
                ["Auth", "Perimeter", "API auth", "SSO / roles"],
            ],
            [3.2, 4.4, 4.2, 5.0],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h2("12.6 Magma-readiness checklist for the MVP")
        self.bullets([
            "**Stable truck IDs.** Use the asset ID in the UI; when Magma arrives, add an optional `networkId`/IMSI mapping rather than replacing the asset ID.",
            "**Method is a string, not an enum.** New positioning methods can appear without a frontend release; known values get labels, unknown values display raw.",
            "**Accuracy is optional, not zero.** A missing accuracy means “unknown”; the UI must not pretend the dot is exact.",
            "**Timestamps are UTC ISO strings.** Magma, MQTT, and the browser all need one time base.",
            "**The contract is versioned.** A major change is negotiated; additive fields are safe.",
            "**The source is behind a port.** The browser never imports Magma SDKs or credentials.",
            "**No 1 Hz assumption in the UI.** The polling interval is configuration; a WebSocket can push faster or slower.",
            "**Snapshot atomicity is preserved.** The WebSocket message is a complete snapshot or a documented patch; MVP consumers only understand snapshots.",
            "**Diagnostics are first-class.** When the radio pipeline degrades, the UI can explain it instead of freezing.",
        ])

        self.h2("12.7 Open5GS fallback")
        self.p(
            "Magma's activity and maintainer support are a project risk. The architecture does not depend on it. If Magma "
            "does not fit the lab, Open5GS can replace it behind the same `NetworkEventSource` and `MeasurementSource` "
            "interfaces. The positioning engine and the UI do not change. The decision should be made after a short lab "
            "spike in Phase 2, not on paper."
        )
        self.callout(
            "Do not couple the domain to a core",
            "The UI must not know whether the core is Magma, Open5GS, or a simulator. The only thing it knows is the "
            "snapshot. This is what makes the “very flexible” requirement real rather than aspirational.",
            "success",
        )

        self.h2("12.8 Storage evolution")
        self.p(
            "Live dots need no database. History, playback, and audits do. When Phase 3 arrives, store positions in "
            "PostGIS/TimescaleDB with a retention policy, keep the current snapshot in Redis, and serve the UI from the "
            "same API. The `FleetSnapshot` contract is unchanged; the API simply reads from a different place."
        )

        self.h2("12.9 What could go wrong in Phase 2")
        self.table(
            ["Risk", "Mitigation"],
            [
                ["Magma event stream is incomplete or unstable", "Spike early; keep Open5GS fallback; treat Magma as one adapter"],
                ["MQTT message loss or duplication", "QoS 1, idempotent ingest, timestamp-based dedupe, sequence IDs"],
                ["Radio accuracy is insufficient", "Calibrate per zone; add stations; show accuracy honestly; consider UWB later"],
                ["Clock skew between agent and server", "NTP; server-side timestamp validation; reject future measurements"],
                ["Snapshot volume grows", "Publish at a fixed cadence, not per measurement; batch; use WebSocket"],
                ["Browser credentials leak", "Never send core/MQTT credentials to the browser; use short-lived API tokens"],
            ],
            [6.6, 10.2],
            font_size=8.4,
        )

    # ------------------------------------------------------------------
    # Chapter 13
    # ------------------------------------------------------------------
    def chapter_13(self) -> None:
        self.h1("13. Step-by-step implementation guide")
        self.p(
            "This chapter is for a developer building the MVP for the first time. It is not a full tutorial, but it gives "
            "the order of work, the commands, and the mistakes that cost the most time. The key is to get a vertical "
            "slice working early: one file, one dot, one click."
        )

        self.h2("13.1 Prerequisites")
        self.bullets([
            "**Node.js 20 or 22 LTS** and **pnpm** (or npm; the commands below use pnpm).",
            "**Git** and a code editor with TypeScript and ESLint support.",
            "A modern browser with developer tools.",
            "A sample snapshot file and a known point on the site to verify coordinates.",
        ])

        self.h2("13.2 Scaffold the app")
        self.code(
            """mkdir web && cd web
pnpm create vite . --template react-ts
pnpm install
pnpm add leaflet react-leaflet @tanstack/react-query zod
pnpm add -D @types/leaflet vitest @testing-library/react @testing-library/jest-dom jsdom
pnpm dev""",
            "Keep the app in `web/` so the architecture documents, sample data, and future backend can live beside it.",
        )
        self.p(
            "Add scripts for `lint`, `typecheck`, `test`, and `build` to `package.json`. A CI pipeline should run all four. "
            "Do this on day 1; adding them later is always more expensive."
        )

        self.h2("13.3 The build order")
        self.step(1, "Freeze the contract",
                  "Copy the example snapshot into `public/data/fleet.snapshot.json`. Walk through every field with the "
                  "producer. Confirm WGS84, UTC, units, and the update cadence. This is a 30-minute conversation that "
                  "saves days.")
        self.step(2, "Add the domain types and Zod schema",
                  "Write `FleetSnapshot`, `Truck`, `BaseStation`, and `Site`. Write the envelope schema and the record "
                  "schemas. Add unit tests with one valid and three invalid fixtures before writing any UI.")
        self.step(3, "Implement the repository",
                  "Write `JsonFileFleetRepository` with fetch, `cache: 'no-store'`, HTTP checks, JSON parse errors, and "
                  "partial-record validation. Test it with a mocked `fetch`; do not test it through the map.")
        self.step(4, "Add the query hook and a debug view",
                  "Render the truck count and the first truck's name in a `<pre>` or a simple list. This proves the data "
                  "path before Leaflet adds layout complexity.")
        self.step(5, "Build the map shell",
                  "Render `MapContainer` with the site centre and zoom. Add the tile layer and a hard-coded marker. Fix "
                  "the container height and import `leaflet/dist/leaflet.css` before debugging anything else.")
        self.step(6, "Draw stations, then trucks",
                  "Stations first: they are static and easy to verify. Then trucks with `key={truck.id}` and "
                  "`center={[truck.lat, truck.lon]}`. Remember Leaflet's order is latitude, longitude.")
        self.step(7, "Add selection and details",
                  "Lift `selectedTruckId` to `FleetMapPage`. Pass it to the map and the details panel. Clicking the map "
                  "background clears it. Add the accuracy circle only for the selected truck.")
        self.step(8, "Add the states",
                  "Implement loading, empty, stale, refresh error, fatal error, and partial-invalid. Trigger each one "
                  "manually: rename the file, corrupt a record, set `generatedAt` back, delete the file. If you cannot "
                  "trigger it, you cannot test it.")
        self.step(9, "Add the tests",
                  "Cover the schema, the repository errors, staleness, the details card, and the banner. Mock Leaflet in "
                  "component tests; keep one real-browser check for the map.")
        self.step(10, "Build and deploy",
                  "Run `pnpm build`. Serve `dist/` with the Nginx config in Appendix A. Verify the base path, "
                  "`Cache-Control: no-store` for `/data/`, and the SPA fallback.")
        self.step(11, "Rehearse the demo",
                  "Run the five-minute script twice, including the failure drill. Record it. A recorded demo is the best "
                  "insurance against a live network surprise.")

        self.h2("13.4 Common mistakes and fixes")
        self.table(
            ["Symptom", "Likely cause", "Fix"],
            [
                ["404 for the snapshot", "Hard-coded `/data/...` under a base path", "Use `${import.meta.env.BASE_URL}data/...`"],
                ["Map tiles are stacked or invisible", "Leaflet CSS missing", "Import `leaflet/dist/leaflet.css` in the app entry"],
                ["Map is blank / zero height", "Parent has no height", "Give the map container an explicit height (e.g. `calc(100vh - 64px)`)"],
                ["Dots are in the ocean", "Latitude/longitude swapped or local metres", "Leaflet expects `[lat, lon]`; check the CRS"],
                ["Map flickers on every poll", "`MapContainer` remounted", "Keep it mounted; update marker props only"],
                ["Requests pile up", "`setInterval` in a component", "Use TanStack Query's `refetchInterval`"],
                ["Stale dots look live", "Freshness based on HTTP status", "Check `generatedAt`; show a stale banner"],
                ["Bad record blanks the map", "Whole-snapshot parse throws", "Validate records individually; collect diagnostics"],
                ["Markers jump/duplicate", "Array index used as `key`", "Use `key={truck.id}`"],
                ["Secret exposed", "Secret in `VITE_*`", "Remove it; Vite variables are public"],
                ["Works locally, fails on deploy", "SPA route/base path not configured", "Nginx `try_files` + correct `base`"],
            ],
            [5.0, 5.8, 6.0],
            font_size=8.2,
        )

        self.h2("13.5 Learning path")
        self.table(
            ["Topic", "What to learn", "Artifact"],
            [
                ["React + TypeScript", "Components, props, state, effects, strict typing", "A list + details panel with local state"],
                ["TanStack Query", "Queries, caching, polling, retries, `keepPreviousData`", "A 1 Hz query with an error state"],
                ["Zod", "Object/array schemas, `safeParse`, custom refinements", "Envelope + record validation with fixtures"],
                ["Leaflet / react-leaflet", "MapContainer, TileLayer, CircleMarker, Circle, Tooltip, ImageOverlay", "A map with stations and one moving dot"],
                ["Data modelling", "Snapshots vs deltas, units, timestamps, versioning", "The v1 contract and example file"],
                ["Testing", "Vitest, Testing Library, mocking fetch/Leaflet", "Unit + component tests for failure states"],
                ["Deployment", "Vite build, Nginx, cache headers, base path", "A deployed URL with no-store data"],
            ],
            [3.6, 7.6, 5.6],
            font_size=8.4,
            first_col_bold=True,
        )

        self.h2("13.6 First-day checklist")
        self.bullets([
            "Repository created; `web/` app runs locally.",
            "Contract v1 and example snapshot reviewed with the producer.",
            "A known reference point on the site is chosen for a visual coordinate check.",
            "Map provider decision recorded: OSM, site plan, or both.",
            "Base path and deployment target known (root or `/fleet/`).",
            "The team agrees on the stale threshold and the status vocabulary.",
            "The demo script is written, even though the app does not exist yet.",
        ])

    # ------------------------------------------------------------------
    # Chapter 14
    # ------------------------------------------------------------------
    def chapter_14(self) -> None:
        self.h1("14. Glossary")
        self.table(
            ["Term", "Meaning in this document"],
            [
                ["MVP", "Minimum viable product: the smallest increment that proves the user value and the architecture."],
                ["Snapshot", "A complete JSON picture of the site, stations, and trucks at one moment."],
                ["Producer", "The script or service that writes the snapshot file. Outside the MVP boundary."],
                ["FleetRepository", "The port through which the UI loads a snapshot. The only data-source seam."],
                ["Adapter", "A concrete implementation of a port, e.g. `JsonFileFleetRepository`."],
                ["Port", "An interface owned by the application, implemented by infrastructure."],
                ["Domain", "Types and pure rules that do not depend on React, Leaflet, or the network."],
                ["WGS84", "The latitude/longitude coordinate system used by GPS and Leaflet."],
                ["ENU", "East–North–Up local metric coordinates, convenient for positioning math."],
                ["Multilateration", "Computing a position from distances to several known stations."],
                ["RSSI / RSRP / RSRQ", "Radio signal strength/quality measurements used to estimate distance or cell quality."],
                ["Timing advance", "A network timing measurement that gives a coarse distance to the serving cell."],
                ["Cell ID", "Positioning by serving cell only; very coarse."],
                ["Accuracy radius", "An estimate of position uncertainty in metres; not a guarantee."],
                ["Stale snapshot", "A snapshot whose `generatedAt` is older than the threshold; the producer may have stopped."],
                ["Polling", "Repeatedly fetching the full snapshot at a fixed interval."],
                ["WebSocket", "A persistent browser–server connection for pushed updates; a Phase 2 option."],
                ["MQTT", "A lightweight publish/subscribe protocol for telemetry; a Phase 2 transport."],
                ["Magma", "An open-source mobile core (AGW + Orchestrator) for private LTE; a Phase 2 data source."],
                ["AGW", "Access Gateway in Magma; serves subscribers and emits session events."],
                ["Orchestrator", "Magma's management API/NMS for subscribers, networks, and policies."],
                ["Open5GS", "An open-source 4G/5G core; a fallback behind the same adapters."],
                ["Leaflet", "The open-source map library used for the MVP."],
                ["OSM", "OpenStreetMap; the map data and tile source used in development."],
                ["Tile", "A small map image at a zoom level; the map is a grid of tiles."],
                ["Zod", "A runtime schema validation library used at the JSON boundary."],
                ["TanStack Query", "The server-state library that handles polling, caching, and retries."],
                ["Stale-while-revalidate", "Showing cached data while a new request is in flight; the UX behind `keepPreviousData`."],
            ],
            [4.0, 12.8],
            font_size=8.2,
            first_col_bold=True,
        )

    # ------------------------------------------------------------------
    # Appendices
    # ------------------------------------------------------------------
    def appendices(self) -> None:
        self.h1("Appendix A. Nginx configuration")
        self.p(
            "This configuration serves the SPA, disables caching for the snapshot, and keeps long-lived caching for "
            "hashed assets. It assumes the app is at the root; for a subpath, set Vite's `base` and adjust `location`."
        )
        self.code(
            """server {
    listen 80;
    server_name fleet.example.internal;

    root /usr/share/nginx/html;
    index index.html;

    # The live snapshot must never be cached.
    location ^~ /data/ {
        add_header Cache-Control "no-store, max-age=0" always;
        try_files $uri =404;
    }

    # Hashed build assets can be cached aggressively.
    location ^~ /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # SPA fallback: any unknown path serves index.html.
    location / {
        try_files $uri $uri/ /index.html;
    }

    gzip on;
    gzip_types application/json application/javascript text/css image/svg+xml;
    gzip_min_length 1024;

    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "same-origin" always;
}""",
            "The `^~` prefix prevents a later regex location from overriding the no-store rule for `/data/`.",
        )
        self.callout(
            "Check the headers, not just the page",
            "Open DevTools → Network → the snapshot request. It must show `Cache-Control: no-store` and a 200. If it is "
            "served from disk cache, the map can freeze while the producer is healthy.",
            "warning",
        )

        self.h1("Appendix B. Demo data generator")
        self.p(
            "The demo needs movement. A small Node script can update the snapshot every second and write it atomically. "
            "It is a development tool, not a production producer; keep it in `tools/` and do not deploy it with the app."
        )
        self.code(
            """// tools/generate-demo-snapshot.mjs
import { writeFile, rename } from 'node:fs/promises';

const target = 'web/public/data/fleet.snapshot.json';
const temp = `${target}.tmp`;
const station = { lat: 55.7558, lon: 37.6173 };
const trucks = [
  { id: 'truck-01', name: 'Truck 01', phase: 0 },
  { id: 'truck-02', name: 'Truck 02', phase: Math.PI / 2 },
  { id: 'truck-03', name: 'Truck 03', phase: Math.PI },
  { id: 'truck-04', name: 'Truck 04', phase: (3 * Math.PI) / 2 },
];

let tick = 0;
setInterval(async () => {
  tick += 1;
  const now = new Date().toISOString();
  const snapshot = {
    schemaVersion: '1.0',
    generatedAt: now,
    site: { id: 'plant-1', name: 'Plant 1 — Demo', center: station, defaultZoom: 17 },
    baseStations: [
      { id: 'bs-01', name: 'BS-01', lat: 55.7562, lon: 37.6168, status: 'online' },
      { id: 'bs-02', name: 'BS-02', lat: 55.7554, lon: 37.6181, status: 'online' },
      { id: 'bs-03', name: 'BS-03', lat: 55.7560, lon: 37.6179, status: 'online' },
    ],
    trucks: trucks.map((t) => ({
      id: t.id, name: t.name,
      lat: station.lat + 0.00035 * Math.sin(tick / 18 + t.phase),
      lon: station.lon + 0.00055 * Math.cos(tick / 18 + t.phase),
      updatedAt: now, status: 'moving', accuracyM: 18,
      method: 'rssi-multilateration',
    })),
  };
  await writeFile(temp, JSON.stringify(snapshot, null, 2));
  await rename(temp, target);
}, 1000);""",
            "A demo-only generator. It writes the committed live file, so run it only in the development workspace.",
        )

        self.h1("Appendix C. Architecture decision records")
        self.p(
            "Each ADR is deliberately short: context, decision, consequence. The log is the memory of the project; it "
            "prevents the same debate from happening twice."
        )
        self.table(
            ["ADR", "Decision and context", "Consequences"],
            [
                ["ADR-001\nFile-backed MVP", "**Context:** the radio stack and Magma are not ready. **Decision:** serve a static JSON snapshot and build the UI first. **Alternatives:** wait for the backend, use a mock API, use a spreadsheet import.", "Fast demo; no backend; file is a temporary transport; risk of disk writes at 1 Hz; replace in Phase 1."],
                ["ADR-002\nFleetRepository port", "**Context:** the data source will change at least twice (file → API → WS). **Decision:** one small interface with `loadSnapshot`. **Alternatives:** direct fetch in components, a generic data-source framework.", "Source swap is one class + one wiring line; no over-abstraction; the port is easy to mock."],
                ["ADR-003\nLeaflet + OSM", "**Context:** need a free, keyless map with markers and circles in a closed network. **Decision:** Leaflet + `react-leaflet`, OSM in dev, site plan/self-hosted tiles in production. **Alternatives:** Yandex Maps, MapLibre, Google Maps.", "No API key; open licence; simple markers; OSM public tiles are not a production SLA; map adapter seam kept."],
                ["ADR-004\nWGS84 contract", "**Context:** positioning math uses local metres; the map uses lat/lon. **Decision:** canonical UI contract is WGS84; conversion happens upstream. **Alternatives:** send local x/y and convert in the browser.", "No geodesy in components; producer must document the origin; one CRS to validate."],
                ["ADR-005\nJSON v1 + Zod", "**Context:** the producer is a separate process; TypeScript cannot validate runtime data. **Decision:** versioned JSON envelope + per-record Zod validation. **Alternatives:** CSV, Protobuf, no validation.", "Runtime safety, partial failure, clear errors; a little schema maintenance."],
                ["ADR-006\n1 Hz polling", "**Context:** the file is a snapshot; WebSocket adds server work. **Decision:** poll every second with TanStack Query. **Alternatives:** WebSocket, SSE, long polling.", "Simple, debuggable, proxy-friendly; ~1 s latency; upgrade to WS in Phase 2."],
                ["ADR-007\nNo DB/history", "**Context:** live dots do not need persistence. **Decision:** no database in MVP. **Alternatives:** SQLite/Postgres from day 1.", "Smaller scope; no history/playback yet; Phase 3 adds PostGIS/Timescale."],
                ["ADR-008\nMagma server-side only", "**Context:** Magma credentials and APIs are sensitive; CORS is not security. **Decision:** future Magma access is behind a backend adapter. **Alternatives:** browser calls Orchestrator directly.", "Secure boundary; testable; the browser only sees snapshots; a backend is required in Phase 2."],
            ],
            [3.2, 7.8, 5.8],
            font_size=8.0,
            first_col_bold=True,
        )

        self.h1("Appendix D. Acceptance checklist")
        self.p(
            "Print this page or copy it into the release ticket. A checked box means “demonstrated”, not “implemented”."
        )
        checks = [
            "Valid snapshot with 3 stations and 5 trucks renders within 2 s",
            "Dots move after the file is replaced, without a page reload",
            "Clicking a dot opens the correct details card",
            "Keyboard-only selection works through the truck list",
            "Accuracy circle and method label are correct for the selected truck",
            "One invalid record is skipped; the rest render; the count is visible",
            "Missing file shows a fatal error with Retry on first load",
            "Failed refresh keeps the last good dots and shows a banner",
            "Old `generatedAt` shows a stale banner even with HTTP 200",
            "Empty trucks array shows an empty state, not an error",
            "Unknown method value displays raw without crashing",
            "Map tiles blocked: dots, stations, legend, and details still work",
            "100-truck snapshot remains responsive",
            "Base-path deployment loads assets and data",
            "`Cache-Control: no-store` is present on the snapshot response",
            "Lint, typecheck, test, and production build are green",
            "README covers run, build, deploy, and data replacement",
            "No secrets in the bundle; app is behind the agreed perimeter",
            "Demo script rehearsed twice, including the failure drill",
            "Release tagged `v0.1.0` with a visible build stamp",
        ]
        rows = [[f"☐", check] for check in checks]
        self.table(["Done", "Check"], rows, [1.6, 15.2], font_size=8.5, align_center_cols=[0])

        self.h1("Appendix E. References and further reading")
        refs = [
            ("React documentation", "https://react.dev/", "Components, state, effects, and the mental model."),
            ("TanStack Query", "https://tanstack.com/query/latest", "Polling, caching, retries, and keepPreviousData."),
            ("Zod", "https://zod.dev/", "Runtime schemas and `safeParse`."),
            ("Leaflet", "https://leafletjs.com/", "Map, markers, circles, image overlays."),
            ("react-leaflet", "https://react-leaflet.js.org/", "React bindings for Leaflet."),
            ("OpenStreetMap tile policy", "https://operations.osmfoundation.org/policies/tiles/", "Why public tiles are for development, not a production SLA."),
            ("Magma", "https://magmacore.org/", "Open-source mobile core: AGW, Orchestrator, NMS."),
            ("Magma on GitHub", "https://github.com/magma/magma", "Source, issues, and current activity."),
            ("Open5GS", "https://open5gs.org/", "Alternative open-source 4G/5G core."),
            ("RFC 3339", "https://www.rfc-editor.org/rfc/rfc3339", "The timestamp format used by generatedAt and updatedAt."),
            ("MDN fetch", "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API", "AbortController, cache, and response handling."),
            ("Vite", "https://vite.dev/", "Build, base path, and environment variables."),
        ]
        for title, url, note in refs:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(f"{title} — ")
            r.bold = True
            r.font.size = Pt(9.2)
            add_hyperlink(p, url, url)
            r = p.add_run(f". {note}")
            r.font.size = Pt(9.2)
            r.font.color.rgb = rgb("334155")

        self.p("", size=8, space_after=2)
        self.callout(
            "Document status",
            "This is MVP 0.1, a draft for review. The architecture is intentionally small; the seams are intentionally "
            "explicit. Update the ADR log when a decision changes, and keep the example snapshot in sync with the schema.",
            "info",
        )


def build() -> Path:
    b = Builder()
    b.cover()
    b.contents()
    b.executive_summary()
    b.chapter_1()
    b.chapter_2()
    b.chapter_3()
    b.chapter_4()
    b.chapter_5()
    b.chapter_6()
    b.chapter_7()
    b.chapter_8()
    b.chapter_9()
    b.chapter_10()
    b.chapter_11()
    b.chapter_12()
    b.chapter_13()
    b.chapter_14()
    b.appendices()
    out = ROOT / "MVP_Plan_and_Architecture.docx"
    b.doc.save(out)
    print(f"Saved {out} ({out.stat().st_size / 1024:.1f} KB)")
    return out


if __name__ == "__main__":
    build()
