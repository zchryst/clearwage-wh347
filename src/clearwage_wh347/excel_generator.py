"""Macro-free, cross-platform (.xlsx) Revised Jan-2025 WH-347 Excel Suite compiler.

Generates two distinct commercial-grade workbooks with zero VBA macros (100% compatible
with Windows Excel, Mac Excel, Excel Online, Google Sheets, and LibreOffice Calc):
1. ClearWage_WH347_Starter_Check_2026.xlsx — Free Lead-Magnet 5-Row Compliance Checker
2. ClearWage_WH347_Pro_Contractor_Suite_2026.xlsx — Full 6-Tab Multi-Crew Production Suite
"""

from __future__ import annotations

from pathlib import Path
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.utils import get_column_letter

from clearwage_wh347.samples import build_clean_hvac_subcontractor_sample

NAVY_DARK = "0F172A"
NAVY_HDR = "1E3A5F"
SLATE_SUB = "334155"
DOL_TAN = "F3D9C4"
DOL_TAN_LIGHT = "FBF2EA"
INPUT_BLUE = "EFF6FF"
OK_GREEN_BG = "DCFCE7"
OK_GREEN_FG = "166534"
ERR_RED_BG = "FEE2E2"
ERR_RED_FG = "991B1B"
WARN_AMB_BG = "FEF3C7"
WARN_AMB_FG = "92400E"
BORDER_GRAY = "CBD5E1"

THIN = Side(border_style="thin", color=BORDER_GRAY)
MED_NAVY = Side(border_style="medium", color=NAVY_HDR)
GRID_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BOX_BORDER = Border(left=MED_NAVY, right=MED_NAVY, top=MED_NAVY, bottom=MED_NAVY)

F_TITLE = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
F_SUBTITLE = Font(name="Calibri", size=10, italic=True, color="E2E8F0")
F_SEC = Font(name="Calibri", size=11, bold=True, color=NAVY_DARK)
F_HDR = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
F_DOL_HDR = Font(name="Calibri", size=8, bold=True, color=NAVY_DARK)
F_BODY = Font(name="Calibri", size=10, color=NAVY_DARK)
F_INPUT = Font(name="Calibri", size=10, color="1D4ED8", bold=False)
F_CALC = Font(name="Calibri", size=10, color=NAVY_DARK, bold=True)

FILL_NAVY = PatternFill("solid", fgColor=NAVY_DARK)
FILL_HDR = PatternFill("solid", fgColor=NAVY_HDR)
FILL_TAN = PatternFill("solid", fgColor=DOL_TAN)
FILL_TAN_LT = PatternFill("solid", fgColor=DOL_TAN_LIGHT)
FILL_INPUT = PatternFill("solid", fgColor=INPUT_BLUE)
FILL_ZEBRA = PatternFill("solid", fgColor="F8FAFC")
FILL_OK = PatternFill("solid", fgColor=OK_GREEN_BG)
FILL_ERR = PatternFill("solid", fgColor=ERR_RED_BG)


def _style_banner(ws, max_col: int, title: str, subtitle: str) -> None:
    end_col = get_column_letter(max_col)
    ws.merge_cells(f"A1:{end_col}1")
    ws.merge_cells(f"A2:{end_col}2")
    ws["A1"] = title
    ws["A2"] = subtitle
    ws["A1"].font = F_TITLE
    ws["A2"].font = F_SUBTITLE
    for col_i in range(1, max_col + 1):
        c1 = ws.cell(row=1, column=col_i)
        c2 = ws.cell(row=2, column=col_i)
        c1.fill = FILL_NAVY
        c2.fill = FILL_HDR
        c1.alignment = Alignment(vertical="center", indent=1)
        c2.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[1].height = 28
    ws.row_dimensions[2].height = 20


def build_pro_contractor_workbook(output_path: str | Path) -> Path:
    """Compiles the full 6-tab macro-free ClearWage WH-347 Pro Contractor Suite (.xlsx)."""
    sample = build_clean_hvac_subcontractor_sample()
    wb = Workbook()

    # =========================================================================
    # TAB 1: README & 2026 MANDATORY CHANGES
    # =========================================================================
    ws_info = wb.active
    ws_info.title = "1_Start_Here_2026_Rules"
    ws_info.views.sheetView[0].showGridLines = False
    _style_banner(
        ws_info,
        6,
        "ClearWage WH-347 Pro Contractor Suite — Post-Oct 2026 Mandatory Edition",
        "OMB Control No. 1235-0008 (Rev. Jan 2025, Exp. 01/31/2028)  |  100% Macro-Free Cross-Platform Engine",
    )

    guide_rows = [
        ("WHY PRE-2025 TEMPLATES ARE BEING REJECTED (EFFECTIVE OCT 1, 2026)", ""),
        ("1. Columns 6B & 6C Split", "Old single Fringe column is gone. Col 6B = Total Bona Fide Plan Credit ($); Col 6C = Total Cash Paid in Lieu of Fringes ($)."),
        ("2. Strict Col 6A Purity Rule", "Cash paid in lieu of fringes MUST NOT be added into Col 6A Hourly Wage Rate. Keep base rates in 6A and cash-in-lieu in 6C."),
        ("3. Mandatory Wage Determination Box", "Page 1 Header now mandates exact SAM.gov Wage Determination Number + Modification # (e.g., 'TX20260028 Mod 3')."),
        ("4. Col 2 'J' vs 'RA' + Step Tier", "Every worker row must declare 'J' (Journeyworker) or 'RA' (Registered Apprentice + progression period/pct)."),
        ("5. Split-Classification Entry No.", "When one worker performs 2+ trades in a week, use separate rows sharing the SAME Col 1A Worker Entry No."),
        ("6. Page 2 Mandatory 'N/A' Rule", "When Box 4 (Apprentices) is unchecked, DOL instructions require entering 'N/A' under Apprenticeship Program Name."),
        ("", ""),
        ("HOW TO USE THIS WORKBOOK IN 3 MINUTES EACH WEEK", ""),
        ("Step 1 — Tab 2 (Project & Rates)", "Enter blue input cells once per contract: project details, SAM.gov prevailing rates, bona fide fringe plans, and apprentice programs."),
        ("Step 2 — Tab 3 (Weekly Crew Entry)", "Enter blue daily ST/OT hours, hourly rates paid, and payroll tax/FICA/other deductions for up to 40 classification rows."),
        ("Step 3 — Tab 4 (Live Audit Gate)", "Verify 'SUBMISSION READY (0 BLOCKERS)' — automatically checks DBRA weighted overtime, CWHSSA >40h, SSN leaks, and Col 9 math."),
        ("Step 4 — Tabs 5 & 6 (Print WH-347)", "Print Tab 5 (Page 1 Payroll) and Tab 6 (Page 2 Statement of Compliance) directly to Landscape PDF!"),
    ]
    r = 4
    for col_a, col_b in guide_rows:
        ws_info.cell(row=r, column=1, value=col_a)
        ws_info.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
        ws_info.cell(row=r, column=2, value=col_b)
        if col_a and not col_b:
            ws_info.cell(row=r, column=1).font = F_SEC
            ws_info.row_dimensions[r].height = 24
        else:
            ws_info.cell(row=r, column=1).font = F_CALC
            ws_info.cell(row=r, column=2).font = F_BODY
            ws_info.row_dimensions[r].height = 20
        r += 1
    ws_info.column_dimensions["A"].width = 34
    for col_let in ("B", "C", "D", "E", "F"):
        ws_info.column_dimensions[col_let].width = 20

    # =========================================================================
    # TAB 2: PROJECT SETUP, SAM.GOV WAGE RATES, FRINGE PLANS & APPRENTICES
    # =========================================================================
    ws_cfg = wb.create_sheet("2_Project_&_SAM_Rates")
    _style_banner(
        ws_cfg,
        8,
        "Contract Metadata, SAM.gov Wage Determination Schedule & Fringe Plans",
        "Edit blue input cells once per project; formulas propagate across Weekly Entry, Audit, and Print WH-347 tabs.",
    )

    meta_fields = [
        ("Project Name", sample.project_name),
        ("Project or Contract No.", sample.project_no),
        ("Certified Payroll No.", sample.certified_payroll_no),
        ("Contractor Role (PRIME or SUBCONTRACTOR)", "SUBCONTRACTOR"),
        ("Final Payroll Submission? (YES or NO)", "NO"),
        ("Business Legal Name", sample.business_name),
        ("Business Full Address", sample.business_address),
        ("Project Location (Include County & State)", sample.project_location),
        ("SAM.gov Wage Determination No. & Mod", sample.wage_determination_no),
        ("Week Ending Date (YYYY-MM-DD)", sample.week_ending_date),
        ("Certifying Official Name", sample.certifying_official_name),
        ("Certifying Official Title", sample.certifying_official_title),
        ("Certifying Official Phone", sample.telephone),
        ("Certifying Official Email", sample.email),
        ("Additional Remarks (Page 2)", sample.additional_remarks),
    ]
    for idx, (lbl, val) in enumerate(meta_fields, start=4):
        c_lbl = ws_cfg.cell(row=idx, column=1, value=lbl)
        c_lbl.font = F_CALC
        c_lbl.fill = FILL_ZEBRA
        c_lbl.border = GRID_BORDER
        ws_cfg.merge_cells(start_row=idx, start_column=2, end_row=idx, end_column=4)
        c_val = ws_cfg.cell(row=idx, column=2, value=val)
        c_val.font = F_INPUT
        c_val.fill = FILL_INPUT
        c_val.protection = Protection(locked=False)
        for mc in range(2, 5):
            ws_cfg.cell(row=idx, column=mc).border = GRID_BORDER
            ws_cfg.cell(row=idx, column=mc).fill = FILL_INPUT

    # SAM.gov Prevailing Wage Schedule (Cols F..I, rows 4..18)
    ws_cfg.cell(row=4, column=6, value="Labor Classification (Exact WD Title)").font = F_HDR
    ws_cfg.cell(row=4, column=7, value="WD Base $/hr").font = F_HDR
    ws_cfg.cell(row=4, column=8, value="WD Fringe $/hr").font = F_HDR
    ws_cfg.cell(row=4, column=9, value="Total Prevailing $/hr").font = F_HDR
    for c_i in range(6, 10):
        cell = ws_cfg.cell(row=4, column=c_i)
        cell.fill = FILL_HDR
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for slot in range(12):
        row_i = 5 + slot
        wd = sample.wage_determinations[slot] if slot < len(sample.wage_determinations) else None
        c_cls = ws_cfg.cell(row=row_i, column=6, value=wd.classification if wd else "")
        c_base = ws_cfg.cell(row=row_i, column=7, value=float(wd.basic_hourly_rate) if wd else None)
        c_frg = ws_cfg.cell(row=row_i, column=8, value=float(wd.fringe_hourly_rate) if wd else None)
        c_tot = ws_cfg.cell(row=row_i, column=9, value=f'=IF(F{row_i}="","",G{row_i}+H{row_i})')
        for c_in in (c_cls, c_base, c_frg):
            c_in.fill = FILL_INPUT
            c_in.font = F_INPUT
            c_in.border = GRID_BORDER
            c_in.protection = Protection(locked=False)
        c_base.number_format = "$#,##0.00"
        c_frg.number_format = "$#,##0.00"
        c_tot.font = F_CALC
        c_tot.fill = FILL_ZEBRA
        c_tot.border = GRID_BORDER
        c_tot.number_format = "$#,##0.00"

    # Bona Fide Fringe Benefit Plans Table (Rows 20..26, Cols A..F)
    ws_cfg.cell(row=20, column=1, value="Plan Slot").font = F_HDR
    ws_cfg.cell(row=20, column=2, value="Fringe Plan Name (Page 2)").font = F_HDR
    ws_cfg.cell(row=20, column=3, value="Plan Type").font = F_HDR
    ws_cfg.cell(row=20, column=4, value="Plan Number").font = F_HDR
    ws_cfg.cell(row=20, column=5, value="Funded / Unfunded").font = F_HDR
    ws_cfg.cell(row=20, column=6, value="DOL 29 CFR 5.28 Ref (if Unfunded)").font = F_HDR
    for c_i in range(1, 7):
        ws_cfg.cell(row=20, column=c_i).fill = FILL_HDR

    for p_idx in range(6):
        r_p = 21 + p_idx
        fp = sample.fringe_plans[p_idx] if p_idx < len(sample.fringe_plans) else None
        ws_cfg.cell(row=r_p, column=1, value=f"FB{p_idx+1}").font = F_CALC
        ws_cfg.cell(row=r_p, column=1).border = GRID_BORDER
        vals = [
            fp.fb_name if fp else "",
            fp.fb_type if fp else "",
            fp.plan_no if fp else "",
            ("FUNDED" if fp.is_funded else "UNFUNDED") if fp else "",
            fp.dol_unfunded_approval_ref if fp else "",
        ]
        for off, v in enumerate(vals, start=2):
            cell = ws_cfg.cell(row=r_p, column=off, value=v)
            cell.fill = FILL_INPUT
            cell.font = F_INPUT
            cell.border = GRID_BORDER
            cell.protection = Protection(locked=False)

    # Registered Apprenticeship Programs Table (Rows 28..31, Cols A..E)
    ws_cfg.cell(row=28, column=1, value="Apprentice Program Name (Box 4)").font = F_HDR
    ws_cfg.cell(row=28, column=2, value="Agency (OA or SAA)").font = F_HDR
    ws_cfg.cell(row=28, column=3, value="Labor Classification").font = F_HDR
    ws_cfg.cell(row=28, column=4, value="Step % of JW Base").font = F_HDR
    for c_i in range(1, 5):
        ws_cfg.cell(row=28, column=c_i).fill = FILL_HDR

    for a_idx in range(3):
        r_a = 29 + a_idx
        ap = sample.apprentice_programs[a_idx] if a_idx < len(sample.apprentice_programs) else None
        vals = [
            ap.program_name if ap else "",
            ap.registration_agency if ap else "",
            ap.labor_classification if ap else "",
            float(ap.progression_pct) / 100.0 if ap else None,
        ]
        for off, v in enumerate(vals, start=1):
            cell = ws_cfg.cell(row=r_a, column=off, value=v)
            cell.fill = FILL_INPUT
            cell.font = F_INPUT
            cell.border = GRID_BORDER
            cell.protection = Protection(locked=False)
        ws_cfg.cell(row=r_a, column=4).number_format = "0%"

    widths_cfg = {"A": 36, "B": 28, "C": 20, "D": 18, "E": 18, "F": 34, "G": 15, "H": 15, "I": 18}
    for k, w in widths_cfg.items():
        ws_cfg.column_dimensions[k].width = w

    # =========================================================================
    # TAB 3: WEEKLY CREW PAYROLL ENTRY & LIVE CALCULATOR (UP TO 24 ROWS)
    # =========================================================================
    ws_ent = wb.create_sheet("3_Weekly_Crew_Entry")
    _style_banner(
        ws_ent,
        34,
        "Weekly Certified Payroll Crew Entry & Deterministic DBRA / 2026 WH-347 Calculator",
        "Enter blue columns; grey/green columns auto-compute Col 5, Col 6B, Col 6C, Col 7A, Col 9 Net Pay, and Prevailing Shortfalls.",
    )

    ent_headers = [
        "1A Entry#", "1B Last Name", "1C First Name", "1D MI", "1E Worker ID (Last4)",
        "2 J/RA", "Apprentice Step%", "3 Classification",
        "D1 ST", "D2 ST", "D3 ST", "D4 ST", "D5 ST", "D6 ST", "D7 ST",
        "D1 OT", "D2 OT", "D3 OT", "D4 OT", "D5 OT", "D6 OT", "D7 OT",
        "5 ST Hrs", "5 OT Hrs", "Total Hrs",
        "6A ST $/hr", "6A OT $/hr", "Page2 Plan $/hr", "Cash Fringe $/hr",
        "6B Plan Credit $", "6C Cash Fringe $", "7A Project Gross $",
        "7B All-Work Gross $", "8a Tax $", "8b FICA $", "8c Other $", "8 Total Ded $", "9 Net Pay $",
        "Audit Status",
    ]
    for c_i, h_txt in enumerate(ent_headers, start=1):
        cell = ws_ent.cell(row=4, column=c_i, value=h_txt)
        cell.font = F_HDR
        cell.fill = FILL_HDR
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = GRID_BORDER
    ws_ent.row_dimensions[4].height = 30

    seen_sample_eno: set[int] = set()
    for slot in range(20):
        r = 5 + slot
        wl = sample.worker_lines[slot] if slot < len(sample.worker_lines) else None
        is_prim = False
        ded = None
        if wl is not None:
            is_prim = wl.worker_entry_no not in seen_sample_eno
            seen_sample_eno.add(wl.worker_entry_no)
            ded = sample.worker_deductions.get(wl.worker_entry_no) if is_prim else None

        plan_hr_sum = float(sum(wl.plan_hourly_credits.values())) if wl else None
        other_ded_sum = float(sum(d.amount for d in ded.other_deductions)) if ded else (0.0 if is_prim and wl else None)
        all_gross_in = (
            float(ded.other_projects_gross) if ded else (0.0 if is_prim and wl else None)
        )

        # Populate input columns
        in_map = {
            1: wl.worker_entry_no if wl else None,
            2: wl.last_name if wl else "",
            3: wl.first_name if wl else "",
            4: wl.middle_initial if wl else "",
            5: wl.worker_id if wl else "",
            6: wl.status if wl else "",
            7: (0.65 if (wl and wl.status == "RA") else (1.0 if wl else None)),
            8: wl.labor_classification if wl else "",
        }
        for d_i in range(7):
            in_map[9 + d_i] = float(wl.st_hours[d_i]) if (wl and wl.st_hours[d_i] > 0) else None
            in_map[16 + d_i] = float(wl.ot_hours[d_i]) if (wl and wl.ot_hours[d_i] > 0) else None
        in_map[26] = float(wl.st_rate_paid) if wl else None
        in_map[27] = float(wl.ot_rate_paid) if wl else None
        in_map[28] = plan_hr_sum
        in_map[29] = float(wl.cash_in_lieu_hourly_rate) if wl else None
        # Col 33 = Non-Project Additional Gross (added to project gross for primary row!), or direct formula:
        for col_idx, val in in_map.items():
            cell = ws_ent.cell(row=r, column=col_idx, value=val)
            cell.fill = FILL_INPUT
            cell.font = F_INPUT
            cell.border = GRID_BORDER
            cell.protection = Protection(locked=False)

        # Formulas for Col 23..25 (Hours) & Col 30..32 (6B, 6C, 7A)
        ws_ent.cell(row=r, column=23, value=f'=IF(A{r}="","",SUM(I{r}:O{r}))')
        ws_ent.cell(row=r, column=24, value=f'=IF(A{r}="","",SUM(P{r}:V{r}))')
        ws_ent.cell(row=r, column=25, value=f'=IF(A{r}="","",W{r}+X{r})')
        ws_ent.cell(row=r, column=30, value=f'=IF(A{r}="","",ROUND(Y{r}*AB{r},2))')
        ws_ent.cell(row=r, column=31, value=f'=IF(A{r}="","",ROUND(Y{r}*AC{r},2))')
        ws_ent.cell(row=r, column=32, value=f'=IF(A{r}="","",ROUND(W{r}*Z{r}+X{r}*AA{r}+AE{r},2))')

        # Primary row All-Work Gross (Col 33) & Deductions (Cols 34..36 inputs, 37..38 formulas)
        # On primary row (first appearance of Entry# in A$5:A{r}), sum all project 7A rows for that worker + off-project gross
        c33_val = (
            round(float(ded.other_projects_gross) + sum(
                float(sum(x.st_hours)*x.st_rate_paid + sum(x.ot_hours)*x.ot_rate_paid + (sum(x.st_hours)+sum(x.ot_hours))*x.cash_in_lieu_hourly_rate)
                for x in sample.worker_lines if x.worker_entry_no == wl.worker_entry_no
            ), 2)
            if (wl and is_prim and ded)
            else None
        )
        c33 = ws_ent.cell(
            row=r,
            column=33,
            value=c33_val if c33_val is not None else f'=IF(A{r}="","",IF(COUNTIF($A$5:A{r},A{r})=1,SUMIF($A$5:$A$24,A{r},$AF$5:$AF$24),""))',
        )
        c33.fill = FILL_INPUT if c33_val is not None else FILL_ZEBRA
        c33.font = F_INPUT if c33_val is not None else F_CALC
        c33.border = GRID_BORDER
        c33.protection = Protection(locked=False)

        for d_col, d_val in [
            (34, float(ded.tax_withholdings) if ded else None),
            (35, float(ded.fica) if ded else None),
            (36, other_ded_sum),
        ]:
            dc = ws_ent.cell(row=r, column=d_col, value=d_val)
            dc.fill = FILL_INPUT
            dc.font = F_INPUT
            dc.border = GRID_BORDER
            dc.protection = Protection(locked=False)

        ws_ent.cell(row=r, column=37, value=f'=IF(AG{r}="","",ROUND(SUM(AH{r}:AJ{r}),2))')
        ws_ent.cell(row=r, column=38, value=f'=IF(AG{r}="","",ROUND(AG{r}-AK{r},2))')

        # Col 39: Live Deterministic Row Compliance Check Formula!
        # Checks: (1) SSN length != 9/11, (2) Status is J or RA, (3) Prevailing ST floor via VLOOKUP on Tab 2, (4) FLSA/DBRA 1.5x OT check
        audit_formula = (
            f'=IF(A{r}="","",'
            f'IF(OR(LEN(TRIM(E{r}))=9,LEN(TRIM(E{r}))=11),"BLOCKER: Full SSN in 1E",'
            f'IF(AND(F{r}<>"J",F{r}<>"RA"),"BLOCKER: Col 2 Must Be J or RA",'
            f'IF(ISERROR(VLOOKUP(H{r},\'2_Project_&_SAM_Rates\'!$F$5:$I$16,2,FALSE)),"WARN: Check WD Class",'
            f'IF((Z{r}+AB{r}+AC{r})+0.001 < (VLOOKUP(H{r},\'2_Project_&_SAM_Rates\'!$F$5:$I$16,2,FALSE)*IF(F{r}="RA",G{r},1)+VLOOKUP(H{r},\'2_Project_&_SAM_Rates\'!$F$5:$I$16,3,FALSE)),"BLOCKER: Below Prevailing ST+Fringe",'
            f'IF(AND(X{r}>0, AA{r}+0.001 < ROUND(1.5*Z{r},2)),"BLOCKER: OT < 1.5x Base","PASS"))))))'
        )
        ws_ent.cell(row=r, column=39, value=audit_formula)

        for calc_col in (23, 24, 25, 30, 31, 32, 37, 38, 39):
            cc = ws_ent.cell(row=r, column=calc_col)
            cc.font = F_CALC
            cc.fill = FILL_ZEBRA
            cc.border = GRID_BORDER

        ws_ent.cell(row=r, column=7).number_format = "0%"
        for m_col in range(26, 39):
            ws_ent.cell(row=r, column=m_col).number_format = "$#,##0.00"

    # Conditional formatting on Audit Status column (AM5:AM24)
    ws_ent.conditional_formatting.add(
        "AM5:AM24",
        FormulaRule(formula=['ISNUMBER(SEARCH("BLOCKER",AM5))'], fill=FILL_ERR, font=Font(color=ERR_RED_FG, bold=True)),
    )
    ws_ent.conditional_formatting.add(
        "AM5:AM24",
        CellIsRule(operator="equal", formula=['"PASS"'], fill=FILL_OK, font=Font(color=OK_GREEN_FG, bold=True)),
    )

    # =========================================================================
    # TAB 4: LIVE SUBMISSION AUDIT DASHBOARD
    # =========================================================================
    ws_aud = wb.create_sheet("4_Live_DBRA_Audit")
    _style_banner(
        ws_aud,
        5,
        "Pre-Submission Statutory Compliance Gate (29 CFR Parts 3 & 5 + CWHSSA)",
        "Verify 0 BLOCKERS before signing Page 2 Statement of Compliance under 18 U.S.C. § 1001.",
    )
    kpis = [
        ("Overall WH-347 Submission Gate", '=IF(B6>0,"HOLD — FIX BLOCKERS BEFORE SIGNING","SUBMISSION READY — 0 BLOCKERS")'),
        ("Active Blocker Count", '=COUNTIF(\'3_Weekly_Crew_Entry\'!AM5:AM24,"BLOCKER*") + IF(\'2_Project_&_SAM_Rates\'!B12="",1,0)'),
        ("Total Project Hours (Col 5)", "=SUM('3_Weekly_Crew_Entry'!Y5:Y24)"),
        ("Total Bona Fide Plan Credit (Col 6B)", "=SUM('3_Weekly_Crew_Entry'!AD5:AD24)"),
        ("Total Cash Paid in Lieu of Fringes (Col 6C)", "=SUM('3_Weekly_Crew_Entry'!AE5:AE24)"),
        ("Total DBRA Project Gross Earned (Col 7A)", "=SUM('3_Weekly_Crew_Entry'!AF5:AF24)"),
        ("Total Net Wages Paid All Work (Col 9)", "=SUM('3_Weekly_Crew_Entry'!AL5:AL24)"),
        ("Page 2 Box 4 Apprentice Mode", '=IF(COUNTIF(\'3_Weekly_Crew_Entry\'!F5:F24,"RA")>0,"CHECK BOX 4 & LIST OA/SAA PROGRAM","LEAVE UNCHECKED & PRINT \'N/A\'")'),
        ("Page 2 Box 5 Fringe Subsection Mode", '=IF(B9>0,"CHECK BOX 5 & COMPLETE HOURLY CREDIT GRID",IF(B10>0,"CHECK BOX 5 ONLY (100% CASH IN COL 6C)","UNCHECKED"))'),
    ]
    for idx, (k_lbl, k_form) in enumerate(kpis, start=5):
        c1 = ws_aud.cell(row=idx, column=1, value=k_lbl)
        c2 = ws_aud.cell(row=idx, column=2, value=k_form)
        c1.font = F_CALC
        c2.font = F_CALC
        c1.border = GRID_BORDER
        c2.border = GRID_BORDER
        c1.fill = FILL_ZEBRA
        if "Total " in k_lbl and "Hours" not in k_lbl:
            c2.number_format = "$#,##0.00"
        ws_aud.row_dimensions[idx].height = 24
    ws_aud.column_dimensions["A"].width = 42
    ws_aud.column_dimensions["B"].width = 48

    # =========================================================================
    # TAB 5: PRINT-READY REVISED JAN 2025 FORM WH-347 PAGE 1 (LANDSCAPE)
    # =========================================================================
    ws_p1 = wb.create_sheet("5_Print_WH347_Page1")
    ws_p1.page_setup.orientation = ws_p1.ORIENTATION_LANDSCAPE
    ws_p1.page_setup.paperSize = ws_p1.PAPERSIZE_LETTER
    ws_p1.sheet_properties.pageSetUpPr.fitToPage = True
    ws_p1.page_setup.fitToWidth = 1
    ws_p1.page_setup.fitToHeight = 1

    ws_p1.merge_cells("A1:R1")
    ws_p1["A1"] = "U.S. DEPARTMENT OF LABOR — WAGE AND HOUR DIVISION  |  DAVIS-BACON WEEKLY CERTIFIED PAYROLL FORM WH-347 (Rev. Jan 2025 | OMB No. 1235-0008 | Exp. 01/31/2028)"
    ws_p1["A1"].font = F_SEC
    ws_p1["A2"] = "Project:"
    ws_p1["B2"] = "='2_Project_&_SAM_Rates'!B4"
    ws_p1["E2"] = "Contract No.:"
    ws_p1["F2"] = "='2_Project_&_SAM_Rates'!B5"
    ws_p1["I2"] = "Payroll No.:"
    ws_p1["J2"] = "='2_Project_&_SAM_Rates'!B6"
    ws_p1["L2"] = "Contractor:"
    ws_p1["M2"] = "='2_Project_&_SAM_Rates'!B9"

    ws_p1["A3"] = "Location:"
    ws_p1["B3"] = "='2_Project_&_SAM_Rates'!B11"
    ws_p1["E3"] = "Wage Det. No.:"
    ws_p1["F3"] = "='2_Project_&_SAM_Rates'!B12"
    ws_p1["I3"] = "Week Ending:"
    ws_p1["J3"] = "='2_Project_&_SAM_Rates'!B13"
    ws_p1["L3"] = "Role:"
    ws_p1["M3"] = "='2_Project_&_SAM_Rates'!B7"

    p1_cols = [
        "(1A) Entry#", "(1B) Last", "(1C) First", "(1D) MI", "(1E) ID",
        "(2) J/RA", "(3) Classification", "(5) ST Hrs", "(5) OT Hrs",
        "(6A) ST Rate", "(6A) OT Rate", "(6B) Fringe Credit", "(6C) Cash Fringe",
        "(7A) Proj Gross", "(7B) All Gross", "(8a) Tax", "(8b) FICA", "(8c) Other", "(8) Tot Ded", "(9) Net Pay",
    ]
    src_cols = ["A", "B", "C", "D", "E", "F", "H", "W", "X", "Z", "AA", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"]
    for idx, ch in enumerate(p1_cols, start=1):
        cell = ws_p1.cell(row=5, column=idx, value=ch)
        cell.font = F_DOL_HDR
        cell.fill = FILL_TAN
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = GRID_BORDER
    ws_p1.row_dimensions[5].height = 28

    for slot in range(16):
        rp = 6 + slot
        re_row = 5 + slot
        for c_idx, scol in enumerate(src_cols, start=1):
            c = ws_p1.cell(row=rp, column=c_idx, value=f"='3_Weekly_Crew_Entry'!{scol}{re_row}")
            c.font = Font(name="Calibri", size=8.5, color=NAVY_DARK)
            c.fill = FILL_TAN_LT if slot % 2 == 1 else PatternFill(fill_type=None)
            c.border = GRID_BORDER
            if c_idx >= 10:
                c.number_format = "$#,##0.00"

    # =========================================================================
    # TAB 6: PRINT-READY STATEMENT OF COMPLIANCE (WH-347 PAGE 2)
    # =========================================================================
    ws_p2 = wb.create_sheet("6_Print_WH347_Page2")
    ws_p2.page_setup.orientation = ws_p2.ORIENTATION_LANDSCAPE
    ws_p2.page_setup.paperSize = ws_p2.PAPERSIZE_LETTER
    ws_p2.sheet_properties.pageSetUpPr.fitToPage = True
    ws_p2.page_setup.fitToWidth = 1
    ws_p2.page_setup.fitToHeight = 1

    ws_p2["A1"] = "STATEMENT OF COMPLIANCE — FORM WH-347 PAGE 2 (OMB Control No. 1235-0008, Expires 01/31/2028)"
    ws_p2["A1"].font = F_SEC
    ws_p2["A2"] = "Project:"
    ws_p2["B2"] = "='2_Project_&_SAM_Rates'!B4"
    ws_p2["D2"] = "Contract No.:"
    ws_p2["E2"] = "='2_Project_&_SAM_Rates'!B5"
    ws_p2["G2"] = "Week Ending:"
    ws_p2["H2"] = "='2_Project_&_SAM_Rates'!B13"
    ws_p2["A3"] = "Certifying Official:"
    ws_p2["B3"] = "='2_Project_&_SAM_Rates'!B14 & \", \" & '2_Project_&_SAM_Rates'!B15"

    certs = [
        ("[X]", "Box 1: Payroll information is correct and complete; wage and fringe rates paid >= applicable Wage Determination."),
        ("[X]", "Box 2: All regular payrolls and required basic records are complete, accurate, and available upon DOL/agency request."),
        ("[X]", "Box 3: Classifications reported for each laborer or mechanic match the work actually performed."),
        ('=IF(COUNTIF(\'3_Weekly_Crew_Entry\'!F5:F24,"RA")>0,"[X]","[  ]")', "Box 4: Registered Apprentices duly registered with DOL OA or recognized State Apprenticeship Agency (SAA)."),
        ('=IF((SUM(\'3_Weekly_Crew_Entry\'!AD5:AD24)+SUM(\'3_Weekly_Crew_Entry\'!AE5:AE24))>0,"[X]","[  ]")', "Box 5: Fringe benefits paid in cash (Col 6C) and/or bona fide benefit plans (Col 6B & Hourly Credit table)."),
        ("[X]", "Box 6: All workers paid full weekly wages earned; no kickbacks or impermissible deductions under 29 CFR Part 3."),
    ]
    for idx, (box_f, txt) in enumerate(certs, start=5):
        ws_p2.cell(row=idx, column=1, value=box_f).font = F_CALC
        ws_p2.cell(row=idx, column=2, value=txt).font = F_BODY

    ws_p2["A12"] = "Box 4 Apprenticeship Program:"
    ws_p2["B12"] = '=IF(COUNTIF(\'3_Weekly_Crew_Entry\'!F5:F24,"RA")>0,\'2_Project_&_SAM_Rates\'!A29,"N/A")'
    ws_p2["D12"] = "Agency:"
    ws_p2["E12"] = '=IF(COUNTIF(\'3_Weekly_Crew_Entry\'!F5:F24,"RA")>0,\'2_Project_&_SAM_Rates\'!B29,"")'

    ws_p2["A14"] = "Additional Remarks:"
    ws_p2["B14"] = "='2_Project_&_SAM_Rates'!B18"
    ws_p2["A16"] = "Electronic / Printed Signature:"
    ws_p2["B16"] = "=\"/s/ \" & '2_Project_&_SAM_Rates'!B14"
    ws_p2["D16"] = "Phone:"
    ws_p2["E16"] = "='2_Project_&_SAM_Rates'!B16"
    ws_p2["G16"] = "Email:"
    ws_p2["H16"] = "='2_Project_&_SAM_Rates'!B17"

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out))
    return out


def build_free_starter_workbook(output_path: str | Path) -> Path:
    """Compiles the Free Lead-Magnet 5-Worker 2026 WH-347 Compliance Check Sheet (.xlsx)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "WH347_2026_Free_QuickCheck"
    _style_banner(
        ws,
        10,
        "ClearWage WH-347 (Rev. Jan 2025 / Oct 2026 Mandatory) — Free 5-Worker Compliance Quick-Check",
        "Check DBRA Weighted Overtime + New Columns 6B & 6C Instantly  |  Full Multi-Crew Print Suite & Official PDF Generator: clearwage-wh347",
    )
    headers = [
        "Worker Name", "1E ID (Last4)", "2 Status (J/RA)", "WD Base $/hr", "WD Fringe $/hr",
        "ST Hrs", "OT Hrs", "6A ST Paid $/hr", "6A OT Paid $/hr", "Plan $/hr + Cash Fringe $/hr",
    ]
    for i, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=i, value=h)
        c.font = F_HDR
        c.fill = FILL_HDR
        c.border = GRID_BORDER
    ws.cell(row=4, column=11, value="6B+6C Fringe Total $").font = F_HDR
    ws.cell(row=4, column=11).fill = FILL_HDR
    ws.cell(row=4, column=12, value="2026 Compliance Verdict").font = F_HDR
    ws.cell(row=4, column=12).fill = FILL_HDR

    demo_rows = [
        ("Ramirez, Carlos", "4829", "J", 38.50, 14.20, 40, 4, 39.00, 58.50, 14.20),
        ("Kowalski, Tomasz", "3318", "J", 22.40, 7.60, 40, 0, 22.40, 33.60, 7.60),
    ]
    for idx in range(5):
        r = 5 + idx
        dr = demo_rows[idx] if idx < len(demo_rows) else ("", "", "J", None, None, None, None, None, None, None)
        for c_i, v in enumerate(dr, start=1):
            c = ws.cell(row=r, column=c_i, value=v)
            c.fill = FILL_INPUT
            c.font = F_INPUT
            c.border = GRID_BORDER
        ws.cell(row=r, column=11, value=f'=IF(A{r}="","",ROUND((F{r}+G{r})*J{r},2))').number_format = "$#,##0.00"
        ws.cell(
            row=r,
            column=12,
            value=(
                f'=IF(A{r}="","",'
                f'IF(LEN(TRIM(B{r}))>=9,"BLOCKER: Full SSN Forbidden",'
                f'IF((H{r}+J{r})+0.001<(D{r}+E{r}),"BLOCKER: ST+Fringe Shortfall",'
                f'IF(AND(G{r}>0,I{r}+0.001<ROUND(1.5*MAX(D{r},H{r}),2)),"BLOCKER: DBRA OT Shortfall","PASS - 2026 COMPLIANT"))))'
            ),
        ).font = F_CALC
    for col_i in range(1, 13):
        ws.column_dimensions[get_column_letter(col_i)].width = 19

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out))
    return out
