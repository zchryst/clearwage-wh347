"""Deterministic cent-exact DBRA & Revised Jan-2025 WH-347 calculation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from clearwage_wh347.models import (
    ApprenticeProgram,
    PayrollSubmission,
    WageDeterminationRate,
    WorkerLineInput,
    q_cent,
)

# Official DOL WH-347 single-letter day codes (Monday=0 .. Sunday=6):
# Per official instructions: M, T, W, T, F, S, S (e.g., T W T F S S M)
DOL_DAY_LETTERS = ["M", "T", "W", "T", "F", "S", "S"]


@dataclass
class ComputedWorkerLine:
    """Computed values for a single Page 1 classification row."""

    row_index: int
    source: WorkerLineInput
    is_primary_row_for_worker: bool
    st_total_hours: Decimal
    ot_total_hours: Decimal
    total_hours: Decimal  # Col 5 combined
    hourly_fringe_credit: Decimal  # Sum of Page 2 plan credits/hr for this row
    col_6b_total_fringe_credit: Decimal  # Total Hours * hourly_fringe_credit
    col_6c_cash_in_lieu: Decimal  # Total Hours * cash_in_lieu_hourly_rate
    col_7a_gross_project: Decimal  # ST*st_rate + OT*ot_rate + Col 6C
    # Populated on primary row for each unique worker_entry_no:
    col_7b_gross_all_work: Decimal | None = None
    col_8_tax: Decimal | None = None
    col_8_fica: Decimal | None = None
    col_8_other: Decimal | None = None
    col_8_total_deductions: Decimal | None = None
    col_9_net_pay: Decimal | None = None
    # Prevailing floor diagnostics:
    required_basic_rate: Decimal | None = None
    required_fringe_rate: Decimal | None = None
    required_st_total_rate: Decimal | None = None
    required_ot_cash_plus_fringe_rate: Decimal | None = None
    effective_st_total_paid: Decimal = Decimal("0.00")
    effective_ot_total_paid: Decimal = Decimal("0.00")
    st_shortfall_per_hour: Decimal = Decimal("0.00")
    ot_shortfall_per_hour: Decimal = Decimal("0.00")
    total_back_wage_shortfall: Decimal = Decimal("0.00")


@dataclass
class Page2WorkerFringeRow:
    """Aggregated Page 2 'Hourly Credit for Fringe Benefits' row per unique worker."""

    worker_entry_no: int
    worker_display_name: str
    plan_credits: dict[str, Decimal]  # plan_id -> $/hr
    total_hourly_credit: Decimal


@dataclass
class ComputedPayrollResult:
    """Full deterministic calculation output across Pages 1, 2, and Addenda."""

    submission: PayrollSubmission
    day_letters: list[str]
    day_dates_md: list[str]
    lines: list[ComputedWorkerLine]
    page2_fringe_rows: list[Page2WorkerFringeRow]
    # Checkboxes on Page 2:
    box1_checked: bool = True
    box2_checked: bool = True
    box3_checked: bool = True
    box4_apprentices_checked: bool = False
    box5_fringes_checked: bool = False
    box6_checked: bool = True
    apprentice_table_na: bool = True
    populate_page2_fringe_grid: bool = False
    auto_remarks: str = ""
    deduction_addendum_rows: list[dict[str, Any]] = field(default_factory=list)
    apprentice_addendum_rows: list[ApprenticeProgram] = field(default_factory=list)
    fringe_plan_addendum_plans: list[Any] = field(default_factory=list)
    # Totals:
    total_project_hours: Decimal = Decimal("0.00")
    total_col_6b: Decimal = Decimal("0.00")
    total_col_6c: Decimal = Decimal("0.00")
    total_col_7a: Decimal = Decimal("0.00")
    total_col_7b: Decimal = Decimal("0.00")
    total_col_9_net: Decimal = Decimal("0.00")
    total_back_wages_due: Decimal = Decimal("0.00")


def compute_workweek_headers(week_ending_iso: str) -> tuple[list[str], list[str]]:
    """Computes the 7 single-letter day codes and M/D dates ending on week_ending_iso."""
    end_dt = date.fromisoformat(week_ending_iso)
    start_dt = end_dt - timedelta(days=6)
    letters: list[str] = []
    dates_md: list[str] = []
    for offset in range(7):
        d = start_dt + timedelta(days=offset)
        letters.append(DOL_DAY_LETTERS[d.weekday()])
        dates_md.append(f"{d.month}/{d.day}")
    return letters, dates_md


def resolve_prevailing_floor(
    line: WorkerLineInput,
    wd_map: dict[str, WageDeterminationRate],
    ap_map: dict[str, ApprenticeProgram],
) -> tuple[Decimal | None, Decimal | None]:
    """Resolves required (basic_hourly_rate, fringe_hourly_rate) for J or RA worker."""
    cls_key = line.labor_classification.strip().lower()
    if line.status == "RA":
        prog = ap_map.get(line.apprentice_program_name.strip().lower())
        if prog is None:
            for p in ap_map.values():
                if p.labor_classification.strip().lower() == cls_key:
                    prog = p
                    break
        if prog is not None:
            jw_key = (prog.journeyworker_classification or prog.labor_classification).strip().lower()
            jw_wd = wd_map.get(jw_key) or wd_map.get(cls_key)
            if jw_wd is not None:
                req_base = q_cent(jw_wd.basic_hourly_rate * (prog.progression_pct / Decimal("100")))
                if prog.apprentice_fringe_hourly_rate is not None:
                    req_fringe = prog.apprentice_fringe_hourly_rate
                elif prog.fringes_full_rate:
                    req_fringe = jw_wd.fringe_hourly_rate
                else:
                    req_fringe = q_cent(
                        jw_wd.fringe_hourly_rate * (prog.progression_pct / Decimal("100"))
                    )
                return req_base, req_fringe
    wd = wd_map.get(cls_key)
    if wd is not None:
        return wd.basic_hourly_rate, wd.fringe_hourly_rate
    return None, None


def compute_dbra_overtime_floor(
    req_base: Decimal,
    req_fringe: Decimal,
    actual_st_base_paid: Decimal,
    hourly_fringe_and_cash_lieu: Decimal,
) -> tuple[Decimal, Decimal]:
    """Computes minimum legal OT total hourly package and minimum OT cash rate in Col 6A.

    Under 29 CFR 5.32 & CWHSSA / FLSA:
    1. Total ST package required = req_base + req_fringe.
    2. Under DBRA/CWHSSA, overtime requires:
       - At least (req_base + req_fringe) straight-time equivalent, PLUS
       - Half-time (0.5x) cash premium on AT LEAST the WD basic hourly rate `req_base`
         (and under FLSA, if actual regular cash rate > req_base, 1.5x actual_st_base_paid!).
       Specifically:
       - DBRA total OT package floor = req_base + req_fringe + q_cent(Decimal("0.5") * req_base)
       - FLSA cash OT rate floor (Col 6A OT) = q_cent(Decimal("1.5") * max(actual_st_base_paid, req_base))
         when cash wages >= req_base; or if employer offsets base with excess fringe (rare),
         cash + fringe + 0.5*req_base.
    Returns (min_total_ot_package_per_hr, min_col_6a_ot_cash_rate).
    """
    half_wd_base = q_cent(Decimal("0.5") * req_base)
    dbra_total_ot_floor = req_base + req_fringe + half_wd_base
    flsa_cash_ot_floor = q_cent(Decimal("1.5") * actual_st_base_paid)
    flsa_total_ot_floor = flsa_cash_ot_floor + hourly_fringe_and_cash_lieu
    return max(dbra_total_ot_floor, flsa_total_ot_floor), flsa_cash_ot_floor


def compute_payroll(submission: PayrollSubmission) -> ComputedPayrollResult:
    """Runs deterministic payroll & prevailing-wage math for an entire WH-347 submission."""
    day_letters, day_dates = compute_workweek_headers(submission.week_ending_date)
    wd_map = {w.classification.strip().lower(): w for w in submission.wage_determinations}
    ap_map = {a.program_name.strip().lower(): a for a in submission.apprentice_programs}
    valid_plan_ids = {p.plan_id for p in submission.fringe_plans}

    # First pass: compute row-level Col 5, 6B, 6C, 7A and group by worker_entry_no
    seen_workers: set[int] = set()
    worker_project_gross_sum: dict[int, Decimal] = {}
    computed_lines: list[ComputedWorkerLine] = []

    for idx, line in enumerate(submission.worker_lines):
        is_primary = line.worker_entry_no not in seen_workers
        seen_workers.add(line.worker_entry_no)

        st_tot = sum(line.st_hours, Decimal("0"))
        ot_tot = sum(line.ot_hours, Decimal("0"))
        tot_hrs = st_tot + ot_tot

        hr_credit = sum(
            (amt for pid, amt in line.plan_hourly_credits.items() if pid in valid_plan_ids or not valid_plan_ids),
            Decimal("0.00"),
        )
        col_6b = q_cent(tot_hrs * hr_credit)
        col_6c = q_cent(tot_hrs * line.cash_in_lieu_hourly_rate)
        st_earnings = q_cent(st_tot * line.st_rate_paid)
        ot_earnings = q_cent(ot_tot * line.ot_rate_paid)
        col_7a = q_cent(st_earnings + ot_earnings + col_6c)

        worker_project_gross_sum[line.worker_entry_no] = (
            worker_project_gross_sum.get(line.worker_entry_no, Decimal("0.00")) + col_7a
        )

        req_base, req_fringe = resolve_prevailing_floor(line, wd_map, ap_map)
        eff_fringe_hr = hr_credit + line.cash_in_lieu_hourly_rate
        eff_st_total = line.st_rate_paid + eff_fringe_hr
        eff_ot_total = line.ot_rate_paid + eff_fringe_hr

        req_st_tot: Decimal | None = None
        req_ot_tot: Decimal | None = None
        st_short = Decimal("0.00")
        ot_short = Decimal("0.00")
        back_wages = Decimal("0.00")

        if req_base is not None and req_fringe is not None:
            req_st_tot = req_base + req_fringe
            req_ot_tot, _ = compute_dbra_overtime_floor(
                req_base, req_fringe, line.st_rate_paid, eff_fringe_hr
            )
            if eff_st_total < req_st_tot:
                st_short = req_st_tot - eff_st_total
            if ot_tot > 0 and eff_ot_total < req_ot_tot:
                ot_short = req_ot_tot - eff_ot_total
            back_wages = q_cent(st_tot * st_short + ot_tot * ot_short)

        computed_lines.append(
            ComputedWorkerLine(
                row_index=idx,
                source=line,
                is_primary_row_for_worker=is_primary,
                st_total_hours=st_tot,
                ot_total_hours=ot_tot,
                total_hours=tot_hrs,
                hourly_fringe_credit=q_cent(hr_credit),
                col_6b_total_fringe_credit=col_6b,
                col_6c_cash_in_lieu=col_6c,
                col_7a_gross_project=col_7a,
                required_basic_rate=req_base,
                required_fringe_rate=req_fringe,
                required_st_total_rate=req_st_tot,
                required_ot_cash_plus_fringe_rate=req_ot_tot,
                effective_st_total_paid=q_cent(eff_st_total),
                effective_ot_total_paid=q_cent(eff_ot_total),
                st_shortfall_per_hour=q_cent(st_short),
                ot_shortfall_per_hour=q_cent(ot_short),
                total_back_wage_shortfall=back_wages,
            )
        )

    # Second pass: populate worker-level All-Work Gross (7B), Deductions (8), Net Pay (9) on primary row
    single_other_remarks: list[str] = []
    deduction_addendum: list[dict[str, Any]] = []

    for cl in computed_lines:
        if not cl.is_primary_row_for_worker:
            continue
        eno = cl.source.worker_entry_no
        proj_sum = worker_project_gross_sum[eno]
        ded = submission.worker_deductions.get(eno)
        if ded is not None:
            gross_all = (
                ded.gross_all_work_override
                if ded.gross_all_work_override is not None
                else q_cent(proj_sum + ded.other_projects_gross)
            )
            tax = ded.tax_withholdings
            fica = ded.fica
            other_sum = sum((d.amount for d in ded.other_deductions), Decimal("0.00"))
            tot_ded = q_cent(tax + fica + other_sum)
            net_pay = (
                ded.net_pay_override
                if ded.net_pay_override is not None
                else q_cent(gross_all - tot_ded)
            )
            if len(ded.other_deductions) == 1:
                it = ded.other_deductions[0]
                single_other_remarks.append(
                    f"Entry #{eno} ({cl.source.last_name}) Other Deduction: {it.description} (${it.amount:.2f})"
                )
            elif len(ded.other_deductions) >= 2:
                deduction_addendum.append(
                    {
                        "worker_entry_no": eno,
                        "worker_name": f"{cl.source.last_name}, {cl.source.first_name}",
                        "items": ded.other_deductions,
                        "total_other": other_sum,
                    }
                )
        else:
            gross_all = proj_sum
            tax = Decimal("0.00")
            fica = Decimal("0.00")
            other_sum = Decimal("0.00")
            tot_ded = Decimal("0.00")
            net_pay = gross_all

        cl.col_7b_gross_all_work = gross_all
        cl.col_8_tax = tax
        cl.col_8_fica = fica
        cl.col_8_other = other_sum
        cl.col_8_total_deductions = tot_ded
        cl.col_9_net_pay = net_pay

    # Page 2 checkboxes & Fringe Benefit Hourly Credit table (per official DOL instructions):
    any_apprentice = any(cl.source.status == "RA" for cl in computed_lines)
    any_6b = any(cl.col_6b_total_fringe_credit > 0 for cl in computed_lines)
    any_6c = any(cl.col_6c_cash_in_lieu > 0 for cl in computed_lines)
    any_wd_fringe = any(w.fringe_hourly_rate > 0 for w in submission.wage_determinations)

    box4 = any_apprentice
    apprentice_na = not any_apprentice
    box5 = any_6b or any_6c or any_wd_fringe
    # Official instructions: if 100% cash-in-lieu (6B == 0 and 6C > 0), check Box 5
    # BUT do NOT populate the Page 2 Hourly Credit subsection!
    populate_fringe_grid = any_6b

    page2_fringe_rows: list[Page2WorkerFringeRow] = []
    if populate_fringe_grid:
        seen_p2: set[int] = set()
        for cl in computed_lines:
            eno = cl.source.worker_entry_no
            if eno in seen_p2:
                continue
            seen_p2.add(eno)
            mi = f" {cl.source.middle_initial}." if cl.source.middle_initial else ""
            disp = f"#{eno} {cl.source.last_name}, {cl.source.first_name}{mi}"
            p_credits = {p.plan_id: cl.source.plan_hourly_credits.get(p.plan_id, Decimal("0.00")) for p in submission.fringe_plans}
            tot_hc = sum(p_credits.values(), Decimal("0.00"))
            page2_fringe_rows.append(
                Page2WorkerFringeRow(
                    worker_entry_no=eno,
                    worker_display_name=disp,
                    plan_credits=p_credits,
                    total_hourly_credit=q_cent(tot_hc),
                )
            )

    remarks_parts: list[str] = []
    if submission.additional_remarks.strip():
        remarks_parts.append(submission.additional_remarks.strip())
    remarks_parts.extend(single_other_remarks)
    if deduction_addendum:
        remarks_parts.append("See attached Copeland Act (29 CFR 3.5) Itemized Deductions Addendum.")

    return ComputedPayrollResult(
        submission=submission,
        day_letters=day_letters,
        day_dates_md=day_dates,
        lines=computed_lines,
        page2_fringe_rows=page2_fringe_rows,
        box1_checked=True,
        box2_checked=True,
        box3_checked=True,
        box4_apprentices_checked=box4,
        box5_fringes_checked=box5,
        box6_checked=True,
        apprentice_table_na=apprentice_na,
        populate_page2_fringe_grid=populate_fringe_grid,
        auto_remarks=" | ".join(remarks_parts),
        deduction_addendum_rows=deduction_addendum,
        apprentice_addendum_rows=submission.apprentice_programs[3:],
        fringe_plan_addendum_plans=submission.fringe_plans[6:],
        total_project_hours=sum((c.total_hours for c in computed_lines), Decimal("0")),
        total_col_6b=sum((c.col_6b_total_fringe_credit for c in computed_lines), Decimal("0.00")),
        total_col_6c=sum((c.col_6c_cash_in_lieu for c in computed_lines), Decimal("0.00")),
        total_col_7a=sum((c.col_7a_gross_project for c in computed_lines), Decimal("0.00")),
        total_col_7b=sum(
            (c.col_7b_gross_all_work or Decimal("0.00") for c in computed_lines), Decimal("0.00")
        ),
        total_col_9_net=sum(
            (c.col_9_net_pay or Decimal("0.00") for c in computed_lines), Decimal("0.00")
        ),
        total_back_wages_due=sum(
            (c.total_back_wage_shortfall for c in computed_lines), Decimal("0.00")
        ),
    )
