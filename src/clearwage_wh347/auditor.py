"""26-Rule Statutory Davis-Bacon, CWHSSA, Copeland Act & Revised Jan-2025 WH-347 Auditor."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import re
from typing import Any

from clearwage_wh347.calculator import ComputedPayrollResult, compute_dbra_overtime_floor, compute_payroll
from clearwage_wh347.models import PayrollSubmission, q_cent

FULL_SSN_RE = re.compile(r"^\s*(?:\d{3}-\d{2}-\d{4}|\d{9})\s*$")
PARTIAL_SSN_EMBED_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


@dataclass
class AuditFinding:
    """Single deterministic compliance finding with CFR citation and remediation."""

    rule_id: str
    severity: str  # "BLOCKER" or "WARNING"
    category: str  # "PREVAILING_WAGE", "OVERTIME_CWHSSA", "FRINGE_2025", "APPRENTICE", "PRIVACY_HEADER", "COPELAND_DEDUCTIONS"
    worker_entry_no: int | None
    title: str
    detail: str
    cfr_citation: str
    back_wage_impact_usd: Decimal = Decimal("0.00")
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "category": self.category,
            "worker_entry_no": self.worker_entry_no,
            "title": self.title,
            "detail": self.detail,
            "cfr_citation": self.cfr_citation,
            "back_wage_impact_usd": float(self.back_wage_impact_usd),
            "remediation": self.remediation,
        }


@dataclass
class AuditReport:
    """Complete pre-submission compliance audit report for a WH-347 filing."""

    passed_submission_gate: bool
    blocker_count: int
    warning_count: int
    total_back_wages_usd: Decimal
    cwhssa_liquidated_damages_risk_usd: Decimal
    findings: list[AuditFinding] = field(default_factory=list)
    computed: ComputedPayrollResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed_submission_gate": self.passed_submission_gate,
            "blocker_count": self.blocker_count,
            "warning_count": self.warning_count,
            "total_back_wages_usd": float(self.total_back_wages_usd),
            "cwhssa_liquidated_damages_risk_usd": float(self.cwhssa_liquidated_damages_risk_usd),
            "findings": [f.to_dict() for f in self.findings],
        }


def audit_payroll(submission: PayrollSubmission) -> AuditReport:
    """Executes all 26 deterministic DBRA / Revised Jan-2025 WH-347 compliance checks."""
    calc = compute_payroll(submission)
    findings: list[AuditFinding] = []

    # --- HEADER & METADATA CHECKS ---
    if submission.contractor_role.strip().lower() not in ("prime", "subcontractor"):
        findings.append(
            AuditFinding(
                rule_id="WH347-001",
                severity="BLOCKER",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Missing Prime Contractor vs. Subcontractor Role Checkbox",
                detail="Page 1 top header requires marking either Prime Contractor or Subcontractor.",
                cfr_citation="DOL WH-347 Instructions (Rev. Jan 2025, OMB 1235-0008)",
                remediation="Set contractor_role to 'prime' or 'subcontractor'.",
            )
        )

    if submission.certified_payroll_no < 1:
        findings.append(
            AuditFinding(
                rule_id="WH347-002",
                severity="BLOCKER",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Invalid Certified Payroll Sequential Number",
                detail=f"Payroll number is '{submission.certified_payroll_no}'; must start at 1 and increment sequentially each week.",
                cfr_citation="29 CFR § 5.5(a)(3)(ii)",
                remediation="Assign sequential payroll number >= 1.",
            )
        )

    if not submission.wage_determination_no.strip():
        findings.append(
            AuditFinding(
                rule_id="WH347-003",
                severity="BLOCKER",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Missing SAM.gov Wage Determination Number",
                detail="The Revised Jan 2025 WH-347 added a mandatory dedicated header box for Wage Determination No. and modification/revision number.",
                cfr_citation="DOL WH-347 Instructions (OMB 1235-0008)",
                remediation="Enter the contract's SAM.gov Wage Determination number and modification (e.g., 'TX20260028 Mod 4').",
            )
        )

    if not submission.project_location.strip() or len(submission.project_location.strip()) < 5:
        findings.append(
            AuditFinding(
                rule_id="WH347-004",
                severity="BLOCKER",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Incomplete Project Location (County & State Required)",
                detail="DOL instructions require complete address or description including at minimum County and State.",
                cfr_citation="29 CFR § 5.5(a)(3)(ii); WH-347 Instructions",
                remediation="Include street/site description plus County and State (e.g., 'Austin, Travis County, TX').",
            )
        )

    if not submission.certifying_official_name.strip() or not submission.certifying_official_title.strip():
        findings.append(
            AuditFinding(
                rule_id="WH347-005",
                severity="BLOCKER",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Missing Certifying Official Name or Title on Page 2",
                detail="Statement of Compliance requires the printed name and official title of the person who paid or supervised payment.",
                cfr_citation="29 CFR § 3.3(b); 18 U.S.C. § 1001",
                remediation="Populate certifying_official_name and certifying_official_title.",
            )
        )

    if not submission.telephone.strip() or not submission.email.strip():
        findings.append(
            AuditFinding(
                rule_id="WH347-006",
                severity="WARNING",
                category="PRIVACY_HEADER",
                worker_entry_no=None,
                title="Missing Signer Telephone or Email on Page 2",
                detail="Revised Jan 2025 Page 2 added dedicated Telephone Number and Email Address boxes next to the signature block.",
                cfr_citation="DOL WH-347 Page 2 (Rev. Jan 2025)",
                remediation="Provide signer's direct phone number and email address to avoid agency holdbacks.",
            )
        )

    # --- WORKER IDENTITY & SPLIT-SHIFT INVARIANTS ---
    entry_to_identity: dict[int, tuple[str, str, str]] = {}
    name_to_entry: dict[tuple[str, str, str], int] = {}
    worker_weekly_total_hours: dict[int, Decimal] = {}
    worker_weekly_ot_hours: dict[int, Decimal] = {}
    worker_ot_days_count: dict[int, int] = {}

    for cl in calc.lines:
        src = cl.source
        eno = src.worker_entry_no
        ident = (src.last_name.strip().lower(), src.first_name.strip().lower(), src.worker_id.strip().lower())

        # WH347-007: Full SSN prohibited!
        if FULL_SSN_RE.match(src.worker_id) or PARTIAL_SSN_EMBED_RE.search(src.worker_id):
            findings.append(
                AuditFinding(
                    rule_id="WH347-007",
                    severity="BLOCKER",
                    category="PRIVACY_HEADER",
                    worker_entry_no=eno,
                    title=f"Full 9-Digit Social Security Number Detected in Col 1E (Entry #{eno})",
                    detail=f"Worker '{src.last_name}, {src.first_name}' has a 9-digit SSN pattern in Col 1E. Full SSNs are strictly prohibited on certified payrolls.",
                    cfr_citation="29 CFR § 5.5(a)(3)(ii)(A); WH-347 Col 1E Instructions",
                    remediation="Replace with last 4 digits of SSN (e.g., '4829') or internal employee ID.",
                )
            )
        elif not src.worker_id.strip():
            findings.append(
                AuditFinding(
                    rule_id="WH347-008",
                    severity="BLOCKER",
                    category="PRIVACY_HEADER",
                    worker_entry_no=eno,
                    title=f"Missing Worker Identifying Number in Col 1E (Entry #{eno})",
                    detail=f"Worker '{src.last_name}, {src.first_name}' has an empty Col 1E identifying number.",
                    cfr_citation="29 CFR § 5.5(a)(3)(ii)(B)",
                    remediation="Enter last 4 digits of SSN or unique employee identifier.",
                )
            )

        # WH347-009: Split-classification same worker_entry_no check
        if eno in entry_to_identity and entry_to_identity[eno] != ident:
            findings.append(
                AuditFinding(
                    rule_id="WH347-009",
                    severity="BLOCKER",
                    category="PRIVACY_HEADER",
                    worker_entry_no=eno,
                    title=f"Duplicate Worker Entry No. #{eno} Assigned to Different Workers",
                    detail=f"Entry #{eno} is shared by distinct worker identities. Only split-classification rows for the SAME worker may share an Entry No.",
                    cfr_citation="DOL WH-347 Col 1A Instructions",
                    remediation="Assign sequential distinct Entry Nos. to different workers.",
                )
            )
        entry_to_identity[eno] = ident

        if ident in name_to_entry and name_to_entry[ident] != eno:
            findings.append(
                AuditFinding(
                    rule_id="WH347-010",
                    severity="BLOCKER",
                    category="PRIVACY_HEADER",
                    worker_entry_no=eno,
                    title=f"Split-Classification Worker Listed Under Different Entry Numbers (#{name_to_entry[ident]} vs #{eno})",
                    detail=(
                        f"Worker '{src.last_name}, {src.first_name}' appears on multiple classification rows with different Col 1A numbers. "
                        "Rev. Jan 2025 instructions mandate reusing the SAME Worker Entry No. across split-classification rows."
                    ),
                    cfr_citation="DOL WH-347 Col 1A Instructions (Rev. Jan 2025)",
                    remediation=f"Set worker_entry_no = {name_to_entry[ident]} on all rows for {src.last_name}, {src.first_name}.",
                )
            )
        else:
            name_to_entry[ident] = eno

        # Accumulate weekly hours across split-classification rows for CWHSSA 40-hour check
        worker_weekly_total_hours[eno] = worker_weekly_total_hours.get(eno, Decimal("0")) + cl.total_hours
        worker_weekly_ot_hours[eno] = worker_weekly_ot_hours.get(eno, Decimal("0")) + cl.ot_total_hours
        for d_idx in range(7):
            if src.ot_hours[d_idx] > 0:
                worker_ot_days_count[eno] = worker_ot_days_count.get(eno, 0) + 1

        # WH347-011: Status J or RA validation
        if src.status not in ("J", "RA"):
            findings.append(
                AuditFinding(
                    rule_id="WH347-011",
                    severity="BLOCKER",
                    category="APPRENTICE",
                    worker_entry_no=eno,
                    title=f"Invalid Col 2 Worker Status '{src.status}' (Must Be 'J' or 'RA')",
                    detail="Revised Jan 2025 Column 2 strictly requires 'J' (Journeyworker) or 'RA' (Registered Apprentice).",
                    cfr_citation="DOL WH-347 Col 2 Instructions (Rev. Jan 2025)",
                    remediation="Set status to 'J' or 'RA'.",
                )
            )

        # WH347-012: Registered Apprentice progression & program registration check
        if src.status == "RA":
            if not src.apprentice_progression.strip():
                findings.append(
                    AuditFinding(
                        rule_id="WH347-012",
                        severity="BLOCKER",
                        category="APPRENTICE",
                        worker_entry_no=eno,
                        title=f"Registered Apprentice Missing Progression Step/Tier (Entry #{eno})",
                        detail=f"Apprentice '{src.last_name}' is marked 'RA' in Col 2 without level/period of progression.",
                        cfr_citation="29 CFR § 5.5(a)(4)(i); WH-347 Col 2 Instructions",
                        remediation="Specify progression step/percentage (e.g., 'Per. 3 - 65%') and attach OA/SAA registration.",
                    )
                )
            matching_progs = [
                p for p in submission.apprentice_programs
                if p.program_name.strip().lower() == src.apprentice_program_name.strip().lower()
                or p.labor_classification.strip().lower() == src.labor_classification.strip().lower()
            ]
            if not matching_progs:
                findings.append(
                    AuditFinding(
                        rule_id="WH347-013",
                        severity="BLOCKER",
                        category="APPRENTICE",
                        worker_entry_no=eno,
                        title=f"Unregistered Apprentice on Page 2 Box 4 Table (Entry #{eno})",
                        detail=(
                            f"Apprentice '{src.last_name}' is paid apprentice rates, but no OA/SAA bona fide apprenticeship program "
                            "is listed for Page 2 Box 4. Unregistered apprentices MUST be paid full Journeyworker prevailing wages!"
                        ),
                        cfr_citation="29 CFR § 5.5(a)(4)(i)",
                        remediation="Add the DOL OA or State SAA registered program details to Page 2 Box 4, or reclassify as 'J' at full Journeyworker rate.",
                    )
                )

        # WH347-014: Cash-in-lieu erroneously included inside Col 6A hourly rate
        if src.includes_cash_fringe_in_6a:
            findings.append(
                AuditFinding(
                    rule_id="WH347-014",
                    severity="BLOCKER",
                    category="FRINGE_2025",
                    worker_entry_no=eno,
                    title=f"Cash-in-Lieu Fringe Erroneously Included in Col 6A Base Rate (Entry #{eno})",
                    detail=(
                        "Rev. Jan 2025 Col 6A instructions explicitly prohibit including cash payments in lieu of fringes in Col 6A. "
                        "Cash-in-lieu must be isolated in new Column 6C."
                    ),
                    cfr_citation="DOL WH-347 Col 6A & 6C Instructions (Rev. Jan 2025)",
                    remediation="Report pure base ST/OT wage rates in Col 6A and move hourly cash-in-lieu to cash_in_lieu_hourly_rate (Col 6C).",
                )
            )

        # WH347-015: Classification missing from Wage Determination schedule
        if submission.wage_determinations and cl.required_basic_rate is None:
            findings.append(
                AuditFinding(
                    rule_id="WH347-015",
                    severity="WARNING",
                    category="PREVAILING_WAGE",
                    worker_entry_no=eno,
                    title=f"Unlisted Labor Classification '{src.labor_classification}' (SF-1444 Conformance Check)",
                    detail=(
                        f"Classification '{src.labor_classification}' for Entry #{eno} does not match any classification in the project Wage Determination schedule."
                    ),
                    cfr_citation="29 CFR § 5.5(a)(1)(iii) (SF-1444 Conformance)",
                    remediation="Match exact SAM.gov Wage Determination classification title or request SF-1444 conformance from Contracting Officer.",
                )
            )

        # WH347-016: Straight-Time Prevailing Wage + Fringe Shortfall
        if cl.st_shortfall_per_hour > 0 and cl.st_total_hours > 0:
            impact = q_cent(cl.st_total_hours * cl.st_shortfall_per_hour)
            findings.append(
                AuditFinding(
                    rule_id="WH347-016",
                    severity="BLOCKER",
                    category="PREVAILING_WAGE",
                    worker_entry_no=eno,
                    title=f"Prevailing Straight-Time + Fringe Underpayment of ${cl.st_shortfall_per_hour:.2f}/hr (Entry #{eno})",
                    detail=(
                        f"{src.last_name} ({src.labor_classification}) effective ST package is ${cl.effective_st_total_paid:.2f}/hr "
                        f"(${src.st_rate_paid:.2f} base + ${cl.hourly_fringe_credit:.2f} plan credit + ${src.cash_in_lieu_hourly_rate:.2f} cash fringe), "
                        f"which is below the required prevailing total of ${cl.required_st_total_rate:.2f}/hr across {cl.st_total_hours} ST hrs."
                    ),
                    cfr_citation="29 CFR § 5.5(a)(1)(i); 40 U.S.C. § 3142",
                    back_wage_impact_usd=impact,
                    remediation=f"Increase cash-in-lieu fringe (Col 6C) or ST base rate (Col 6A) by at least ${cl.st_shortfall_per_hour:.2f}/hr (Restitution due: ${impact:.2f}).",
                )
            )

        # WH347-017: DBRA / CWHSSA / FLSA Overtime Rate Shortfall
        if cl.ot_total_hours > 0 and cl.required_basic_rate is not None and cl.required_fringe_rate is not None:
            eff_fringe = cl.hourly_fringe_credit + src.cash_in_lieu_hourly_rate
            req_ot_tot, min_cash_ot = compute_dbra_overtime_floor(
                cl.required_basic_rate, cl.required_fringe_rate, src.st_rate_paid, eff_fringe
            )
            if cl.ot_shortfall_per_hour > 0:
                ot_impact = q_cent(cl.ot_total_hours * cl.ot_shortfall_per_hour)
                findings.append(
                    AuditFinding(
                        rule_id="WH347-017",
                        severity="BLOCKER",
                        category="OVERTIME_CWHSSA",
                        worker_entry_no=eno,
                        title=f"DBRA/CWHSSA Overtime Underpayment of ${cl.ot_shortfall_per_hour:.2f}/hr (Entry #{eno})",
                        detail=(
                            f"{src.last_name} worked {cl.ot_total_hours} OT hrs at ${src.ot_rate_paid:.2f}/hr cash + ${eff_fringe:.2f}/hr fringe "
                            f"(= ${cl.effective_ot_total_paid:.2f}/hr), below legal minimum ${req_ot_tot:.2f}/hr "
                            f"(1.5x regular/WD base + full prevailing fringe)."
                        ),
                        cfr_citation="29 CFR § 5.32; CWHSSA 40 U.S.C. § 3702",
                        back_wage_impact_usd=ot_impact,
                        remediation=f"Set Col 6A OT rate >= ${min_cash_ot:.2f}/hr plus full fringe (Back wages due: ${ot_impact:.2f}).",
                    )
                )
            elif src.ot_rate_paid < min_cash_ot and src.st_rate_paid >= cl.required_basic_rate:
                cash_gap = q_cent((min_cash_ot - src.ot_rate_paid) * cl.ot_total_hours)
                findings.append(
                    AuditFinding(
                        rule_id="WH347-018",
                        severity="BLOCKER",
                        category="OVERTIME_CWHSSA",
                        worker_entry_no=eno,
                        title=f"FLSA Cash Overtime Rate Below 1.5x Actual Regular Rate (Entry #{eno})",
                        detail=(
                            f"Col 6A OT rate (${src.ot_rate_paid:.2f}/hr) is less than 1.5x worker's actual ST base rate (${min_cash_ot:.2f}/hr)."
                        ),
                        cfr_citation="29 CFR § 778.107; 29 CFR § 5.32(a)",
                        back_wage_impact_usd=cash_gap,
                        remediation=f"Increase Col 6A OT rate to at least ${min_cash_ot:.2f}/hr.",
                    )
                )

    # --- CWHSSA >40 WEEKLY HOURS LOGGED AS STRAIGHT TIME CHECK ---
    cwhssa_damages = Decimal("0.00")
    if submission.cwhssa_applies:
        for eno, tot_w_hrs in worker_weekly_total_hours.items():
            logged_ot = worker_weekly_ot_hours.get(eno, Decimal("0"))
            min_required_ot_hrs = max(Decimal("0"), tot_w_hrs - Decimal("40"))
            if logged_ot < min_required_ot_hrs:
                unpaid_ot_hrs = min_required_ot_hrs - logged_ot
                # Liquidated damages under CWHSSA (29 CFR 5.5(b)(2)) are $32/day per calendar day of unpaid OT!
                est_days = max(1, int((unpaid_ot_hrs / Decimal("8")).to_integral_value()) + 1)
                liq_dmg = Decimal(32 * est_days)
                cwhssa_damages += liq_dmg
                # Estimate half-time premium back wages
                primary_cl = next(c for c in calc.lines if c.source.worker_entry_no == eno)
                half_rate = q_cent(Decimal("0.5") * primary_cl.source.st_rate_paid)
                ot_bw = q_cent(unpaid_ot_hrs * half_rate)
                findings.append(
                    AuditFinding(
                        rule_id="WH347-019",
                        severity="BLOCKER",
                        category="OVERTIME_CWHSSA",
                        worker_entry_no=eno,
                        title=f"CWHSSA >40 Weekly Hours Logged as Straight Time (Entry #{eno}: {tot_w_hrs} hrs, only {logged_ot} OT)",
                        detail=(
                            f"Entry #{eno} worked {tot_w_hrs} project hours across all classifications this week, requiring at least "
                            f"{min_required_ot_hrs} OT hours under CWHSSA, but only {logged_ot} OT hours were paid. "
                            f"Exposes contractor to ${ot_bw:.2f} back wages PLUS ~$32/day CWHSSA liquidated damages (~${liq_dmg:.2f})."
                        ),
                        cfr_citation="40 U.S.C. § 3702; 29 CFR § 5.5(b)(1)-(2)",
                        back_wage_impact_usd=ot_bw,
                        remediation=f"Reclassify {unpaid_ot_hrs} hours from ST to OT and pay 1.5x overtime rate.",
                    )
                )

    # --- APPRENTICE-TO-JOURNEYWORKER RATIO CHECK ---
    for prog in submission.apprentice_programs:
        cls_key = prog.labor_classification.strip().lower()
        jw_key = (prog.journeyworker_classification or prog.labor_classification).strip().lower()
        ra_workers = {
            c.source.worker_entry_no for c in calc.lines
            if c.source.status == "RA" and c.source.labor_classification.strip().lower() == cls_key and c.total_hours > 0
        }
        jw_workers = {
            c.source.worker_entry_no for c in calc.lines
            if c.source.status == "J" and c.source.labor_classification.strip().lower() in (cls_key, jw_key) and c.total_hours > 0
        }
        if ra_workers:
            allowed_ra = (len(jw_workers) // max(1, prog.ratio_journeyworkers)) * prog.ratio_apprentices
            # Note: Many OA/SAA standards permit the 1st apprentice with >=1 journeyworker on site; flag if 0 JWs or ratio exceeded
            if len(jw_workers) == 0 or (len(jw_workers) >= prog.ratio_journeyworkers and len(ra_workers) > allowed_ra):
                findings.append(
                    AuditFinding(
                        rule_id="WH347-020",
                        severity="BLOCKER",
                        category="APPRENTICE",
                        worker_entry_no=None,
                        title=f"Apprentice Ratio Violation for '{prog.labor_classification}' ({len(ra_workers)} RA vs. {len(jw_workers)} J)",
                        detail=(
                            f"Program '{prog.program_name}' enforces a {prog.ratio_apprentices}:{prog.ratio_journeyworkers} RA-to-J ratio, "
                            f"but {len(ra_workers)} apprentice(s) worked with {len(jw_workers)} journeyworker(s). Excess apprentices must be paid full Journeyworker rate."
                        ),
                        cfr_citation="29 CFR § 5.5(a)(4)(i)",
                        remediation="Reclassify out-of-ratio apprentice hours to full Journeyworker prevailing wage rate.",
                    )
                )

    # --- UNFUNDED FRINGE BENEFIT PLAN CHECK (29 CFR 5.28) ---
    for plan in submission.fringe_plans:
        if not plan.is_funded and not plan.dol_unfunded_approval_ref.strip():
            findings.append(
                AuditFinding(
                    rule_id="WH347-021",
                    severity="BLOCKER",
                    category="FRINGE_2025",
                    worker_entry_no=None,
                    title=f"Unfunded Fringe Plan '{plan.fb_name}' Claimed Without Prior DOL Approval (29 CFR § 5.28)",
                    detail=(
                        f"Page 2 marks plan '{plan.fb_name}' as Unfunded, but no prior written DOL WHD approval reference is recorded. "
                        "Contractors cannot claim Col 6B credit for unfunded plans without prior DOL approval."
                    ),
                    cfr_citation="29 CFR § 5.28(b)(4); WH-347 Page 2 Instructions",
                    remediation="Provide DOL unfunded plan approval reference or pay the obligation as cash-in-lieu in Col 6C.",
                )
            )

    # --- ALL-WORK GROSS (7B), COPELAND ACT DEDUCTIONS (8), AND NET PAY (9) CHECKS ---
    for cl in calc.lines:
        if not cl.is_primary_row_for_worker:
            continue
        eno = cl.source.worker_entry_no
        proj_sum = sum(
            (x.col_7a_gross_project for x in calc.lines if x.source.worker_entry_no == eno),
            Decimal("0.00"),
        )
        if cl.col_7b_gross_all_work is not None and cl.col_7b_gross_all_work < proj_sum:
            findings.append(
                AuditFinding(
                    rule_id="WH347-022",
                    severity="BLOCKER",
                    category="COPELAND_DEDUCTIONS",
                    worker_entry_no=eno,
                    title=f"Col 7B All-Work Gross (${cl.col_7b_gross_all_work:.2f}) Less Than Col 7A Project Gross (${proj_sum:.2f})",
                    detail=f"Entry #{eno} total gross wages for all work cannot be less than gross wages earned on this DBRA project.",
                    cfr_citation="DOL WH-347 Col 7A/7B Instructions",
                    remediation=f"Set Col 7B >= ${proj_sum:.2f}.",
                )
            )

        ded = submission.worker_deductions.get(eno)
        if ded is not None:
            for item in ded.other_deductions:
                if not item.description.strip():
                    findings.append(
                        AuditFinding(
                            rule_id="WH347-023",
                            severity="BLOCKER",
                            category="COPELAND_DEDUCTIONS",
                            worker_entry_no=eno,
                            title=f"Unspecified 'Other' Deduction of ${item.amount:.2f} in Col 8 (Entry #{eno})",
                            detail="Any 'Other' deduction in Column 8 must be explicitly described on Page 2 Additional Remarks (if 1 item) or an attached Addendum (if >=2 items).",
                            cfr_citation="29 CFR § 3.5; WH-347 Col 8 Instructions",
                            remediation="Provide a specific deduction description (e.g., 'Child Support Garnishment' or '401(k) Employee Deferral').",
                        )
                    )
                if not item.is_permissible_29cfr35 and not item.dol_approval_ref.strip():
                    findings.append(
                        AuditFinding(
                            rule_id="WH347-024",
                            severity="BLOCKER",
                            category="COPELAND_DEDUCTIONS",
                            worker_entry_no=eno,
                            title=f"Impermissible Payroll Deduction '${item.description}' Without DOL Approval (Entry #{eno})",
                            detail=f"Deduction '{item.description}' (${item.amount:.2f}) is not exempt under 29 CFR § 3.5 and lacks prior DOL approval under 29 CFR § 3.6.",
                            cfr_citation="Copeland Anti-Kickback Act; 29 CFR §§ 3.5–3.6",
                            back_wage_impact_usd=item.amount,
                            remediation="Refund impermissible deduction or record written DOL 29 CFR § 3.6 approval.",
                        )
                    )
            if ded.net_pay_override is not None and cl.col_7b_gross_all_work is not None and cl.col_8_total_deductions is not None:
                expected_net = q_cent(cl.col_7b_gross_all_work - cl.col_8_total_deductions)
                if ded.net_pay_override != expected_net:
                    findings.append(
                        AuditFinding(
                            rule_id="WH347-025",
                            severity="BLOCKER",
                            category="COPELAND_DEDUCTIONS",
                            worker_entry_no=eno,
                            title=f"Col 9 Net Pay Math Mismatch on Entry #{eno} (${ded.net_pay_override:.2f} vs Expected ${expected_net:.2f})",
                            detail=(
                                f"Col 7B (${cl.col_7b_gross_all_work:.2f}) minus Col 8 Total Deductions (${cl.col_8_total_deductions:.2f}) "
                                f"equals ${expected_net:.2f}, but Net Pay was entered as ${ded.net_pay_override:.2f}."
                            ),
                            cfr_citation="DOL WH-347 Col 8 & Col 9 Instructions",
                            remediation=f"Reconcile withholding/deduction items so Net Pay equals ${expected_net:.2f}.",
                        )
                    )

    # --- ADDENDUM TRIGGER INFORMATIONAL WARNINGS ---
    if len(submission.fringe_plans) > 6 or len(submission.apprentice_programs) > 3 or calc.deduction_addendum_rows:
        findings.append(
            AuditFinding(
                rule_id="WH347-026",
                severity="WARNING",
                category="FRINGE_2025",
                worker_entry_no=None,
                title="Mandatory Continuation / Addendum Page Auto-Generated",
                detail="Submission exceeds single-sheet Page 2 table capacity (>6 fringe plans, >3 apprentice programs, or >=2 Other deductions per worker); ClearWage automatically appends compliant Addendum page(s).",
                cfr_citation="DOL WH-347 Page 1 Col 8 & Page 2 Instructions",
                remediation="Ensure all generated Addendum pages remain attached to the signed PDF packet.",
            )
        )

    blockers = sum(1 for f in findings if f.severity == "BLOCKER")
    warnings = sum(1 for f in findings if f.severity == "WARNING")
    total_bw = sum((f.back_wage_impact_usd for f in findings), Decimal("0.00"))

    return AuditReport(
        passed_submission_gate=(blockers == 0),
        blocker_count=blockers,
        warning_count=warnings,
        total_back_wages_usd=q_cent(total_bw),
        cwhssa_liquidated_damages_risk_usd=q_cent(cwhssa_damages),
        findings=findings,
        computed=calc,
    )
