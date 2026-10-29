"""Typed domain models for U.S. DOL Form WH-347 (Rev. Jan 2025, OMB 1235-0008, Exp. 01/31/2028)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

CENT = Decimal("0.01")


def to_dec(val: str | int | float | Decimal) -> Decimal:
    """Converts numeric input cleanly to Decimal without binary float artifacts."""
    if isinstance(val, Decimal):
        return val
    if isinstance(val, (int, str)):
        return Decimal(str(val).strip() or "0")
    return Decimal(f"{val:.6f}")


def q_cent(val: Decimal) -> Decimal:
    """Rounds a Decimal to exact cents using standard payroll ROUND_HALF_UP."""
    return val.quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass
class WageDeterminationRate:
    """Prevailing wage classification floor from SAM.gov Wage Determination."""

    classification: str
    basic_hourly_rate: Decimal
    fringe_hourly_rate: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        self.basic_hourly_rate = to_dec(self.basic_hourly_rate)
        self.fringe_hourly_rate = to_dec(self.fringe_hourly_rate)

    @property
    def total_prevailing_rate(self) -> Decimal:
        return self.basic_hourly_rate + self.fringe_hourly_rate


@dataclass
class ApprenticeProgram:
    """Registered bona fide apprenticeship program (DOL OA or State SAA)."""

    program_name: str
    registration_agency: str  # "OA" or "SAA"
    labor_classification: str
    journeyworker_classification: str = ""
    progression_pct: Decimal = Decimal("60")  # e.g., 60% of Journeyworker basic rate
    fringes_full_rate: bool = True  # Unless program specifies % fringes, full WD fringes apply
    apprentice_fringe_hourly_rate: Decimal | None = None
    ratio_apprentices: int = 1
    ratio_journeyworkers: int = 3  # e.g., 1:3 ratio

    def __post_init__(self) -> None:
        self.registration_agency = self.registration_agency.upper().strip()
        self.progression_pct = to_dec(self.progression_pct)
        if self.apprentice_fringe_hourly_rate is not None:
            self.apprentice_fringe_hourly_rate = to_dec(self.apprentice_fringe_hourly_rate)


@dataclass
class FringePlan:
    """Bona fide fringe benefit plan claimed toward Column (6B) / Page 2."""

    plan_id: str
    fb_name: str
    fb_type: str  # e.g. "Health & Welfare", "Pension / 401(k)", "Vacation", "Training"
    plan_no: str
    is_funded: bool = True
    dol_unfunded_approval_ref: str = ""


@dataclass
class DeductionItem:
    """Single 'Other' deduction under Copeland Act (29 CFR 3.5 / 3.6)."""

    description: str
    amount: Decimal
    is_permissible_29cfr35: bool = True
    dol_approval_ref: str = ""

    def __post_init__(self) -> None:
        self.amount = q_cent(to_dec(self.amount))


@dataclass
class WorkerLineInput:
    """Single row on WH-347 Page 1. Multi-classification workers share worker_entry_no."""

    worker_entry_no: int
    last_name: str
    first_name: str
    middle_initial: str = ""
    worker_id: str = ""  # Last 4 SSN or internal emp ID (never full 9-digit SSN!)
    status: str = "J"  # "J" or "RA"
    apprentice_progression: str = ""  # e.g. "Period 3 (65%)"
    apprentice_program_name: str = ""
    labor_classification: str = ""
    st_hours: list[Decimal] = field(default_factory=lambda: [Decimal("0")] * 7)
    ot_hours: list[Decimal] = field(default_factory=lambda: [Decimal("0")] * 7)
    st_rate_paid: Decimal = Decimal("0.00")  # Col 6A top (excluding cash-in-lieu!)
    ot_rate_paid: Decimal = Decimal("0.00")  # Col 6A bottom (excluding cash-in-lieu!)
    plan_hourly_credits: dict[str, Decimal] = field(default_factory=dict)  # plan_id -> $/hr
    cash_in_lieu_hourly_rate: Decimal = Decimal("0.00")  # $/hr paid as cash in lieu of fringes
    includes_cash_fringe_in_6a: bool = False  # Common contractor mistake flagged by auditor!

    def __post_init__(self) -> None:
        self.status = self.status.upper().strip()
        self.st_hours = [to_dec(x) for x in self.st_hours]
        self.ot_hours = [to_dec(x) for x in self.ot_hours]
        if len(self.st_hours) != 7 or len(self.ot_hours) != 7:
            raise ValueError("st_hours and ot_hours must each have exactly 7 daily entries.")
        self.st_rate_paid = to_dec(self.st_rate_paid)
        self.ot_rate_paid = to_dec(self.ot_rate_paid)
        self.plan_hourly_credits = {k: to_dec(v) for k, v in self.plan_hourly_credits.items()}
        self.cash_in_lieu_hourly_rate = to_dec(self.cash_in_lieu_hourly_rate)


@dataclass
class WorkerAllWorkDeductions:
    """Weekly all-work gross and deductions per unique worker_entry_no (Cols 7B, 8, 9)."""

    worker_entry_no: int
    other_projects_gross: Decimal = Decimal("0.00")
    gross_all_work_override: Decimal | None = None
    tax_withholdings: Decimal = Decimal("0.00")
    fica: Decimal = Decimal("0.00")
    other_deductions: list[DeductionItem] = field(default_factory=list)
    net_pay_override: Decimal | None = None

    def __post_init__(self) -> None:
        self.other_projects_gross = q_cent(to_dec(self.other_projects_gross))
        if self.gross_all_work_override is not None:
            self.gross_all_work_override = q_cent(to_dec(self.gross_all_work_override))
        self.tax_withholdings = q_cent(to_dec(self.tax_withholdings))
        self.fica = q_cent(to_dec(self.fica))
        if self.net_pay_override is not None:
            self.net_pay_override = q_cent(to_dec(self.net_pay_override))


@dataclass
class PayrollSubmission:
    """Complete weekly certified payroll submission for one covered DBRA contract."""

    project_name: str
    project_no: str
    certified_payroll_no: int
    contractor_role: str  # "prime" or "subcontractor"
    business_name: str
    business_address: str
    project_location: str
    wage_determination_no: str
    week_ending_date: str  # YYYY-MM-DD
    certifying_official_name: str
    certifying_official_title: str
    is_final_payroll: bool = False
    cwhssa_applies: bool = True  # True for contracts > $100,000
    signature_text: str = ""
    signature_date: str = ""
    telephone: str = ""
    email: str = ""
    additional_remarks: str = ""
    wage_determinations: list[WageDeterminationRate] = field(default_factory=list)
    apprentice_programs: list[ApprenticeProgram] = field(default_factory=list)
    fringe_plans: list[FringePlan] = field(default_factory=list)
    worker_lines: list[WorkerLineInput] = field(default_factory=list)
    worker_deductions: dict[int, WorkerAllWorkDeductions] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PayrollSubmission:
        wds = [WageDeterminationRate(**w) for w in data.get("wage_determinations", [])]
        aps = [ApprenticeProgram(**a) for a in data.get("apprentice_programs", [])]
        fps = [FringePlan(**f) for f in data.get("fringe_plans", [])]
        lines = [WorkerLineInput(**l) for l in data.get("worker_lines", [])]
        deds: dict[int, WorkerAllWorkDeductions] = {}
        for k, v in data.get("worker_deductions", {}).items():
            entry_no = int(k)
            items = [DeductionItem(**it) for it in v.get("other_deductions", [])]
            v_copy = {kk: vv for kk, vv in v.items() if kk not in ("other_deductions", "worker_entry_no")}
            deds[entry_no] = WorkerAllWorkDeductions(
                worker_entry_no=entry_no, other_deductions=items, **v_copy
            )
        base_keys = {
            "project_name", "project_no", "certified_payroll_no", "contractor_role",
            "business_name", "business_address", "project_location", "wage_determination_no",
            "week_ending_date", "certifying_official_name", "certifying_official_title",
            "is_final_payroll", "cwhssa_applies", "signature_text", "signature_date",
            "telephone", "email", "additional_remarks",
        }
        kwargs = {k: data[k] for k in base_keys if k in data}
        return cls(
            wage_determinations=wds,
            apprentice_programs=aps,
            fringe_plans=fps,
            worker_lines=lines,
            worker_deductions=deds,
            **kwargs,
        )
