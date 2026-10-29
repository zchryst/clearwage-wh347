"""Pixel-accurate PyMuPDF overlay compiler onto the official DOL Rev. Jan-2025 Form WH-347."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import re
import pymupdf

from clearwage_wh347.calculator import ComputedPayrollResult, ComputedWorkerLine, Page2WorkerFringeRow, compute_payroll
from clearwage_wh347.models import PayrollSubmission

ASSET_PDF = Path(__file__).parent / "assets" / "wh347_official.pdf"

# Exact Page 1 row top/mid/bottom Y coordinates from vector inspection of wh347_official.pdf:
P1_ROW_BANDS: list[tuple[float, float, float]] = [
    (282.3, 295.4, 310.0),
    (310.7, 324.0, 337.9),
    (338.7, 351.5, 365.9),
    (366.7, 380.4, 394.8),
    (395.6, 409.3, 423.7),
    (424.5, 438.2, 452.2),
    (452.2, 466.1, 480.0),
    (480.0, 494.0, 508.4),
]

P1_DAY_X: list[tuple[float, float]] = [
    (341.4, 355.6),
    (355.6, 367.8),
    (367.8, 380.2),
    (380.2, 392.5),
    (392.5, 404.9),
    (404.9, 417.2),
    (417.2, 430.4),
]

P2_PLAN_X: list[tuple[float, float]] = [
    (144.0, 238.6),
    (238.6, 333.0),
    (333.0, 427.6),
    (427.6, 522.0),
    (522.0, 616.6),
    (616.6, 711.0),
]

P2_WORKER_Y: list[tuple[float, float]] = [
    (371.9, 383.6),
    (383.6, 395.2),
    (395.2, 406.6),
    (406.6, 418.1),
    (418.1, 429.6),
    (429.6, 441.0),
    (441.0, 452.5),
    (452.5, 464.0),
]

INK = (0.06, 0.14, 0.28)  # Crisp dark navy ink so filled values stand out cleanly


def _fmt_hrs(val: Decimal) -> str:
    if val == 0:
        return ""
    if val == val.to_integral_value():
        return str(int(val))
    return f"{val.normalize():f}"


def _fmt_money(val: Decimal | None, blank_zero: bool = False) -> str:
    if val is None:
        return ""
    if blank_zero and val == 0:
        return "0.00"
    return f"{val:,.2f}"


def _draw_box_text(
    page: pymupdf.Page,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    text: str,
    fontsize: float = 7.2,
    align: int = pymupdf.TEXT_ALIGN_LEFT,
    bold: bool = False,
    multiline: bool = False,
) -> None:
    if not text:
        return
    fontname = "hebo" if bold else "helv"
    pad_x = 1.4
    avail_w = max(4.0, (x1 - x0) - 2.0 * pad_x)

    if multiline:
        rect = pymupdf.Rect(x0 + pad_x, y0 + 0.8, x1 - pad_x, y1 - 0.5)
        fs = fontsize
        while fs >= 4.6:
            rc = page.insert_textbox(
                rect,
                text,
                fontsize=fs,
                fontname=fontname,
                color=INK,
                align=align,
            )
            if rc >= 0:
                return
            fs -= 0.4

    # Single-line exact positioning (guarantees numbers like 1,794.00 never wrap mid-digit!)
    fs = fontsize
    tw = pymupdf.get_text_length(text, fontname=fontname, fontsize=fs)
    while fs > 3.5 and tw > avail_w:
        fs = round(fs - 0.25, 2)
        tw = pymupdf.get_text_length(text, fontname=fontname, fontsize=fs)

    if align == pymupdf.TEXT_ALIGN_RIGHT:
        tx = max(x0 + 0.8, x1 - pad_x - tw)
    elif align == pymupdf.TEXT_ALIGN_CENTER:
        tx = max(x0 + 0.6, x0 + ((x1 - x0) - tw) / 2.0)
    else:
        tx = x0 + pad_x

    baseline_y = (y0 + y1) / 2.0 + fs * 0.34
    page.insert_text(
        pymupdf.Point(tx, baseline_y),
        text,
        fontsize=fs,
        fontname=fontname,
        color=INK,
    )


def _draw_check(page: pymupdf.Page, cx0: float, cy0: float, cx1: float, cy1: float) -> None:
    """Draws a crisp vector checkmark inside an official WH-347 checkbox rectangle."""
    w = cx1 - cx0
    h = cy1 - cy0
    p1 = pymupdf.Point(cx0 + 0.18 * w, cy0 + 0.55 * h)
    p2 = pymupdf.Point(cx0 + 0.42 * w, cy0 + 0.80 * h)
    p3 = pymupdf.Point(cx0 + 0.85 * w, cy0 + 0.20 * h)
    shape = page.new_shape()
    shape.draw_line(p1, p2)
    shape.draw_line(p2, p3)
    shape.finish(color=INK, width=1.35)
    shape.commit()


def _stamp_watermark(page: pymupdf.Page, text: str) -> None:
    page.insert_text(
        pymupdf.Point(155, 360),
        text,
        fontsize=36,
        fontname="hebo",
        color=(0.82, 0.22, 0.22),
        rotate=0,
        fill_opacity=0.18,
    )


def _fill_page1_chunk(
    page: pymupdf.Page,
    calc: ComputedPayrollResult,
    chunk: list[ComputedWorkerLine],
    sheet_idx: int,
    total_p1_sheets: int,
) -> None:
    sub = calc.submission
    # Top checkboxes
    if sub.is_final_payroll:
        _draw_check(page, 40.4, 101.4, 49.4, 110.4)
    if sub.contractor_role.strip().lower() == "prime":
        _draw_check(page, 432.0, 101.4, 441.0, 110.4)
    elif sub.contractor_role.strip().lower() == "subcontractor":
        _draw_check(page, 576.0, 101.4, 585.0, 110.4)

    pno_str = str(sub.certified_payroll_no)
    if total_p1_sheets > 1:
        pno_str = f"{sub.certified_payroll_no} (Sh. {sheet_idx + 1}/{total_p1_sheets})"

    # Header Row 1 (y = 132.6 .. 152.0)
    _draw_box_text(page, 42.0, 133.0, 195.0, 151.6, sub.project_name, fontsize=7.6, bold=True)
    _draw_box_text(page, 196.5, 133.0, 340.5, 151.6, sub.project_no, fontsize=7.6)
    _draw_box_text(page, 342.0, 133.0, 439.0, 151.6, pno_str, fontsize=7.6, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
    _draw_box_text(page, 440.5, 133.0, 751.0, 151.6, sub.business_name, fontsize=7.6, bold=True)

    # Header Row 2 (y = 164.0 .. 184.3)
    _draw_box_text(page, 42.0, 164.4, 195.0, 183.8, sub.project_location, fontsize=6.8)
    _draw_box_text(page, 196.5, 164.4, 340.5, 183.8, sub.wage_determination_no, fontsize=7.2)
    _draw_box_text(page, 342.0, 164.4, 439.0, 183.8, sub.week_ending_date, fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER)
    _draw_box_text(page, 440.5, 164.4, 751.0, 183.8, sub.business_address, fontsize=6.8)

    # Column 4 Day Letters (y = 223.3..236.0) & Dates (y = 236.0..250.1)
    # Note: Day 0 has a small artifact box on left edge of template around 345.6..351.2, still centers cleanly
    for d_idx in range(7):
        dx0, dx1 = P1_DAY_X[d_idx]
        _draw_box_text(page, dx0, 223.5, dx1, 235.8, calc.day_letters[d_idx], fontsize=6.8, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
        _draw_box_text(page, dx0, 236.2, dx1, 249.8, calc.day_dates_md[d_idx], fontsize=5.6, align=pymupdf.TEXT_ALIGN_CENTER)

    # Worker Rows (up to 8 per sheet)
    for r_idx, cl in enumerate(chunk):
        src = cl.source
        y_top, y_mid, y_bot = P1_ROW_BANDS[r_idx]
        _draw_box_text(page, 41.2, y_top, 65.7, y_bot, str(src.worker_entry_no), fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
        _draw_box_text(page, 66.2, y_top, 115.6, y_bot, src.last_name, fontsize=6.8)
        _draw_box_text(page, 116.2, y_top, 165.3, y_bot, src.first_name, fontsize=6.8)
        _draw_box_text(page, 165.8, y_top, 191.0, y_bot, src.middle_initial, fontsize=6.8, align=pymupdf.TEXT_ALIGN_CENTER)
        _draw_box_text(page, 191.6, y_top, 221.0, y_bot, src.worker_id, fontsize=6.6, align=pymupdf.TEXT_ALIGN_CENTER)

        col2_txt = src.status if src.status == "J" else f"RA {src.apprentice_progression}".strip()
        _draw_box_text(page, 221.6, y_top, 255.6, y_bot, col2_txt, fontsize=6.0, align=pymupdf.TEXT_ALIGN_CENTER, multiline=True)
        _draw_box_text(page, 256.4, y_top, 300.8, y_bot, src.labor_classification, fontsize=5.8, multiline=True)

        for d_idx in range(7):
            dx0, dx1 = P1_DAY_X[d_idx]
            _draw_box_text(page, dx0, y_top, dx1, y_mid, _fmt_hrs(src.st_hours[d_idx]), fontsize=6.3, align=pymupdf.TEXT_ALIGN_CENTER)
            _draw_box_text(page, dx0, y_mid, dx1, y_bot, _fmt_hrs(src.ot_hours[d_idx]), fontsize=6.3, align=pymupdf.TEXT_ALIGN_CENTER)

        # Col 5 Total Hours (ST top, OT bottom)
        _draw_box_text(page, 430.6, y_top, 469.4, y_mid, _fmt_hrs(cl.st_total_hours), fontsize=6.8, align=pymupdf.TEXT_ALIGN_RIGHT, bold=True)
        _draw_box_text(page, 430.6, y_mid, 469.4, y_bot, _fmt_hrs(cl.ot_total_hours), fontsize=6.8, align=pymupdf.TEXT_ALIGN_RIGHT)

        # Col 6A Wage Rates Paid (ST top, OT bottom)
        _draw_box_text(page, 469.8, y_top, 497.9, y_mid, _fmt_money(src.st_rate_paid), fontsize=6.4, align=pymupdf.TEXT_ALIGN_RIGHT)
        if cl.ot_total_hours > 0 or src.ot_rate_paid > 0:
            _draw_box_text(page, 469.8, y_mid, 497.9, y_bot, _fmt_money(src.ot_rate_paid), fontsize=6.4, align=pymupdf.TEXT_ALIGN_RIGHT)

        # Col 6B, 6C, 7A
        _draw_box_text(page, 498.3, y_top, 524.2, y_bot, _fmt_money(cl.col_6b_total_fringe_credit, blank_zero=True), fontsize=6.2, align=pymupdf.TEXT_ALIGN_RIGHT)
        _draw_box_text(page, 524.6, y_top, 550.6, y_bot, _fmt_money(cl.col_6c_cash_in_lieu, blank_zero=True), fontsize=6.2, align=pymupdf.TEXT_ALIGN_RIGHT)
        _draw_box_text(page, 551.0, y_top, 577.0, y_bot, _fmt_money(cl.col_7a_gross_project), fontsize=6.2, align=pymupdf.TEXT_ALIGN_RIGHT, bold=True)

        # Col 7B, 8 (Tax, FICA, Other, Total), 9 Net Pay — printed on primary row per worker
        if cl.is_primary_row_for_worker:
            _draw_box_text(page, 577.4, y_top, 604.5, y_bot, _fmt_money(cl.col_7b_gross_all_work), fontsize=6.2, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 604.9, y_top, 631.4, y_bot, _fmt_money(cl.col_8_tax, blank_zero=True), fontsize=6.0, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 631.8, y_top, 658.2, y_bot, _fmt_money(cl.col_8_fica, blank_zero=True), fontsize=6.0, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 658.6, y_top, 689.2, y_bot, _fmt_money(cl.col_8_other, blank_zero=True), fontsize=6.0, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 689.6, y_top, 712.6, y_bot, _fmt_money(cl.col_8_total_deductions, blank_zero=True), fontsize=6.0, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 713.0, y_top, 751.8, y_bot, _fmt_money(cl.col_9_net_pay), fontsize=6.4, align=pymupdf.TEXT_ALIGN_RIGHT, bold=True)
        else:
            _draw_box_text(page, 577.4, y_top, 751.8, y_bot, f"See Entry #{src.worker_entry_no} primary row", fontsize=5.6, align=pymupdf.TEXT_ALIGN_CENTER)


def _fill_page2_chunk(
    page: pymupdf.Page,
    calc: ComputedPayrollResult,
    fringe_chunk: list[Page2WorkerFringeRow],
    sheet_idx: int,
    total_p2_sheets: int,
) -> None:
    sub = calc.submission
    pno_str = str(sub.certified_payroll_no)
    if total_p2_sheets > 1:
        pno_str = f"{sub.certified_payroll_no} ({sheet_idx + 1}/{total_p2_sheets})"

    # Header Row 1 (y = 44.3 .. 63.6)
    _draw_box_text(page, 33.0, 44.8, 237.5, 63.0, sub.project_name, fontsize=7.6, bold=True)
    _draw_box_text(page, 240.0, 44.8, 377.0, 63.0, sub.project_no, fontsize=7.6)
    _draw_box_text(page, 379.5, 44.8, 471.5, 63.0, pno_str, fontsize=7.6, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
    _draw_box_text(page, 474.0, 44.8, 759.5, 63.0, sub.business_name, fontsize=7.6, bold=True)

    # Header Row 2 (y = 75.6 .. 95.9)
    _draw_box_text(page, 33.0, 76.0, 377.0, 95.4, sub.project_location, fontsize=7.0)
    _draw_box_text(page, 379.5, 76.0, 471.5, 95.4, sub.week_ending_date, fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER)
    official_line = f"{sub.certifying_official_name}, {sub.certifying_official_title}".strip(", ")
    _draw_box_text(page, 474.0, 76.0, 759.5, 95.4, official_line, fontsize=7.4, bold=True)

    # 6 Statement of Compliance Checkboxes
    if calc.box1_checked:
        _draw_check(page, 38.2, 125.2, 47.2, 134.2)
    if calc.box2_checked:
        _draw_check(page, 38.2, 156.0, 47.2, 165.0)
    if calc.box3_checked:
        _draw_check(page, 38.2, 176.2, 47.2, 185.2)
    if calc.box4_apprentices_checked:
        _draw_check(page, 38.2, 199.8, 47.2, 208.8)
    if calc.box5_fringes_checked:
        _draw_check(page, 38.2, 284.6, 47.2, 293.6)
    if calc.box6_checked:
        _draw_check(page, 38.2, 472.3, 47.2, 481.3)

    # Apprenticeship Table (3 rows: y=237.8..250.4, 250.4..262.0, 262.0..273.5)
    ap_ys = [(237.8, 250.4), (250.4, 262.0), (262.0, 273.5)]
    ap_chk_ys = [(240.4, 248.4), (252.4, 260.4), (263.9, 272.0)]
    if calc.apprentice_table_na:
        # Mandatory DOL instruction when Box 4 is unchecked: enter "N/A" under Program Name!
        _draw_box_text(page, 56.0, ap_ys[0][0], 376.0, ap_ys[0][1], "N/A", fontsize=7.2, bold=True)
    else:
        for idx, prog in enumerate(sub.apprentice_programs[:3]):
            ay0, ay1 = ap_ys[idx]
            cy0, cy1 = ap_chk_ys[idx]
            _draw_box_text(page, 56.0, ay0, 376.0, ay1, prog.program_name, fontsize=6.8)
            if prog.registration_agency == "OA":
                _draw_check(page, 383.4, cy0, 391.4, cy1)
            elif prog.registration_agency == "SAA":
                _draw_check(page, 432.8, cy0, 440.9, cy1)
            _draw_box_text(page, 474.0, ay0, 759.0, ay1, prog.labor_classification, fontsize=6.8)

    # Hourly Credit for Fringe Benefits Subsection (only populated when Col 6B > 0)
    if calc.populate_page2_fringe_grid:
        plans_6 = sub.fringe_plans[:6]
        funded_x = [
            (149.4, 194.4),
            (243.8, 288.8),
            (338.4, 383.4),
            (432.8, 477.8),
            (527.4, 572.4),
            (621.8, 666.8),
        ]
        for p_idx, plan in enumerate(plans_6):
            px0, px1 = P2_PLAN_X[p_idx]
            _draw_box_text(page, px0 + 42.0, 326.8, px1 - 2.0, 338.0, plan.fb_name, fontsize=5.6, bold=True)
            _draw_box_text(page, px0 + 38.5, 338.8, px1 - 2.0, 350.2, plan.fb_type, fontsize=5.6)
            _draw_box_text(page, px0 + 40.5, 350.6, px1 - 2.0, 362.0, plan.plan_no, fontsize=5.6)
            fx, ufx = funded_x[p_idx]
            if plan.is_funded:
                _draw_check(page, fx, 363.9, fx + 7.0, 370.9)
            else:
                _draw_check(page, ufx, 363.9, ufx + 7.0, 370.9)

        for w_idx, wrow in enumerate(fringe_chunk):
            wy0, wy1 = P2_WORKER_Y[w_idx]
            _draw_box_text(page, 55.0, wy0, 143.5, wy1, wrow.worker_display_name, fontsize=6.0)
            for p_idx, plan in enumerate(plans_6):
                px0, px1 = P2_PLAN_X[p_idx]
                amt = wrow.plan_credits.get(plan.plan_id, Decimal("0.00"))
                if amt > 0:
                    _draw_box_text(page, px0 + 57.0, wy0, px1 - 2.0, wy1, f"{amt:.2f}", fontsize=6.2, align=pymupdf.TEXT_ALIGN_RIGHT)
            _draw_box_text(page, 720.0, wy0, 759.0, wy1, f"{wrow.total_hourly_credit:.2f}", fontsize=6.4, align=pymupdf.TEXT_ALIGN_RIGHT, bold=True)

    # Additional Remarks (y = 503.5 .. 527.0)
    _draw_box_text(page, 33.0, 504.0, 759.0, 526.6, calc.auto_remarks, fontsize=6.4, multiline=True)

    # Signature Block (y = 540.2 .. 556.6)
    sig_str = sub.signature_text or (f"/s/ {sub.certifying_official_name}" if sub.certifying_official_name else "")
    sig_dt = sub.signature_date or sub.week_ending_date
    _draw_box_text(page, 33.0, 540.8, 376.0, 556.2, sig_str, fontsize=7.6, bold=True)
    _draw_box_text(page, 380.0, 540.8, 471.0, 556.2, sig_dt, fontsize=7.2, align=pymupdf.TEXT_ALIGN_CENTER)
    # Place 10-digit US telephone numbers directly into the pre-printed ( ___ ) ___ - ____ slots!
    digits = re.sub(r"\D", "", sub.telephone or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        _draw_box_text(page, 482.0, 540.0, 509.8, 551.8, digits[:3], fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
        _draw_box_text(page, 521.0, 540.0, 548.8, 551.8, digits[3:6], fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
        _draw_box_text(page, 558.0, 540.0, 595.5, 551.8, digits[6:], fontsize=7.4, align=pymupdf.TEXT_ALIGN_CENTER, bold=True)
    else:
        _draw_box_text(page, 475.0, 540.0, 615.0, 552.0, sub.telephone, fontsize=7.0, align=pymupdf.TEXT_ALIGN_CENTER)
    _draw_box_text(page, 619.0, 540.8, 759.0, 556.2, sub.email, fontsize=6.8)


def _append_addendum_page(out_doc: pymupdf.Document, calc: ComputedPayrollResult) -> None:
    """Appends a clean Landscape US-Letter Addendum page if needed (>3 RA programs, >6 plans, or >=2 Other deductions)."""
    sub = calc.submission
    page = out_doc.new_page(width=792, height=612)
    shape = page.new_shape()
    shape.draw_rect(pymupdf.Rect(30, 28, 762, 584))
    shape.finish(color=(0.55, 0.35, 0.18), width=1.1)
    shape.draw_rect(pymupdf.Rect(30, 28, 762, 68))
    shape.finish(color=(0.55, 0.35, 0.18), fill=(0.95, 0.88, 0.81), width=1.0)
    shape.commit()

    page.insert_text(
        pymupdf.Point(42, 46),
        "U.S. DOL FORM WH-347 (REV. JAN 2025) — OFFICIAL CONTINUATION ADDENDUM",
        fontsize=11,
        fontname="hebo",
        color=INK,
    )
    page.insert_text(
        pymupdf.Point(42, 60),
        f"Project: {sub.project_name} ({sub.project_no})   |   Payroll No: {sub.certified_payroll_no}   |   Week Ending: {sub.week_ending_date}   |   Contractor: {sub.business_name}",
        fontsize=7.8,
        fontname="helv",
        color=INK,
    )
    y = 88.0

    if calc.deduction_addendum_rows:
        page.insert_text(
            pymupdf.Point(42, y),
            "SECTION A — COPELAND ACT (29 CFR § 3.5) ITEMIZED 'OTHER' DEDUCTIONS SCHEDULE",
            fontsize=9.2,
            fontname="hebo",
            color=INK,
        )
        y += 15
        for row in calc.deduction_addendum_rows:
            items_str = ";  ".join(
                f"{it.description}: ${it.amount:.2f}" + (f" [DOL Approval: {it.dol_approval_ref}]" if it.dol_approval_ref else "")
                for it in row["items"]
            )
            page.insert_text(
                pymupdf.Point(50, y),
                f"Entry #{row['worker_entry_no']} — {row['worker_name']}   |   Col 8 Other Total: ${row['total_other']:.2f}   |   Breakdown: {items_str}",
                fontsize=8.0,
                fontname="helv",
                color=INK,
            )
            y += 14
        y += 12

    if calc.apprentice_addendum_rows:
        page.insert_text(
            pymupdf.Point(42, y),
            "SECTION B — ADDITIONAL REGISTERED APPRENTICESHIP PROGRAMS (PAGE 2 BOX 4 CONTINUATION)",
            fontsize=9.2,
            fontname="hebo",
            color=INK,
        )
        y += 15
        for prog in calc.apprentice_addendum_rows:
            page.insert_text(
                pymupdf.Point(50, y),
                f"Program: {prog.program_name}   |   Registered Agency: {prog.registration_agency}   |   Classification: {prog.labor_classification} ({prog.progression_pct}%)",
                fontsize=8.0,
                fontname="helv",
                color=INK,
            )
            y += 14
        y += 12

    if calc.fringe_plan_addendum_plans:
        page.insert_text(
            pymupdf.Point(42, y),
            "SECTION C — ADDITIONAL BONA FIDE FRINGE BENEFIT PLANS (PAGE 2 BOX 5 CONTINUATION)",
            fontsize=9.2,
            fontname="hebo",
            color=INK,
        )
        y += 15
        for plan in calc.fringe_plan_addendum_plans:
            status_lbl = "Funded" if plan.is_funded else f"Unfunded (29 CFR 5.28 Approval: {plan.dol_unfunded_approval_ref})"
            page.insert_text(
                pymupdf.Point(50, y),
                f"{plan.fb_name} ({plan.fb_type})   |   Plan No: {plan.plan_no}   |   Status: {status_lbl}",
                fontsize=8.0,
                fontname="helv",
                color=INK,
            )
            y += 14

    sig_str = sub.signature_text or (f"/s/ {sub.certifying_official_name}" if sub.certifying_official_name else "")
    page.insert_text(
        pymupdf.Point(42, 568),
        f"Certified true and complete as an integral attachment to Form WH-347 Payroll #{sub.certified_payroll_no}:   {sig_str}   ({sub.signature_date or sub.week_ending_date})",
        fontsize=7.6,
        fontname="helv",
        color=INK,
    )


def render_wh347_pdf(
    submission: PayrollSubmission,
    output_path: str | Path,
    watermark_text: str | None = None,
) -> Path:
    """Compiles a complete, pixel-aligned Revised Jan-2025 DOL Form WH-347 PDF."""
    calc = compute_payroll(submission)
    tpl = pymupdf.open(str(ASSET_PDF))
    out = pymupdf.open()

    # Chunk Page 1 into groups of 8 classification lines
    lines = calc.lines
    p1_chunks = [lines[i : i + 8] for i in range(0, max(1, len(lines)), 8)]
    for idx, ch in enumerate(p1_chunks):
        out.insert_pdf(tpl, from_page=0, to_page=0)
        p = out[-1]
        _fill_page1_chunk(p, calc, ch, idx, len(p1_chunks))
        if watermark_text:
            _stamp_watermark(p, watermark_text)

    # Chunk Page 2 into groups of 8 workers if populate_page2_fringe_grid has >8 unique workers
    f_rows = calc.page2_fringe_rows
    p2_chunks = [f_rows[i : i + 8] for i in range(0, max(1, len(f_rows)), 8)]
    for idx, ch in enumerate(p2_chunks):
        out.insert_pdf(tpl, from_page=1, to_page=1)
        p = out[-1]
        _fill_page2_chunk(p, calc, ch, idx, len(p2_chunks))
        if watermark_text:
            _stamp_watermark(p, watermark_text)

    if calc.deduction_addendum_rows or calc.apprentice_addendum_rows or calc.fringe_plan_addendum_plans:
        _append_addendum_page(out, calc)
        if watermark_text:
            _stamp_watermark(out[-1], watermark_text)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(str(out_path), deflate=True)
    out.close()
    tpl.close()
    return out_path
